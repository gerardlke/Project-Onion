import fitz
from pptx import Presentation
from docx import Document
from fastapi import UploadFile
from io import BytesIO

### Set up configs
from app.configs.config import (
    SUPPORTED_EXTENSIONS,
    MAX_FILE_SIZE_MB
)

### Set up logger
from app.logging import setup_logger
logger = setup_logger(__name__)


async def extract_text(file: UploadFile):
    """Route uploaded file to the correct extractor based on extension

    Input:  UploadFile from FastAPI

    Output: raw text string for downstream chunking and concept extraction
    """
    extension = file.filename.split(".")[-1].lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: .{extension}. Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValueError(f"File '{file.filename}' exceeds the 50MB size limit: ({len(contents):.1f}MB)")

    logger.info(f"Extracting text from '{file.filename}' ({extension})")

    if extension in ["txt", "md"]:
        return _extract_text_file(contents)
    elif extension == "docx":
        return _extract_docx(contents)
    elif extension == "pdf":
        return _extract_pdf(contents)
    elif extension == "pptx":
        return _extract_pptx(contents)
    

### Helper functions


def _extract_text_file(contents: bytes):
    """Extract text from plain text or markdown files"""
    return contents.decode("utf-8")


def _extract_docx(contents: bytes):
    """Extract text from a Word document"""
    blocks = []
    doc = Document(BytesIO(contents))

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:
            blocks.append(text)

    for table in doc.tables:
        for row in table.rows:
            row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_texts:
                blocks.append(" | ".join(row_texts))

    return "\n".join(blocks)


def _extract_pdf(contents: bytes):
    """Extract text from a PDF using PyMuPDF (fitz)    """
    doc = fitz.open(stream=contents, filetype="pdf")
    pages = []

    for page_num, page in enumerate(doc):
        text = page.get_text("text").strip()
        if text:
            pages.append(text)
        else:
            logger.debug(f"Page {page_num + 1}: no extractable text (may be image-only)")

    doc.close()

    if not pages:
        raise ValueError("No extractable text found in PDF.")

    total_pages = len(doc)
    logger.info(f"Extracted text from {len(pages)}/{total_pages} PDF page(s)")
    return "\n\n".join(pages)


def _extract_pptx(contents: bytes):
    """Extract text from a PowerPoint presentation"""
    prs = Presentation(BytesIO(contents))
    slides_text = []

    for slide_num, slide in enumerate(prs.slides, start=1):
        slide_blocks = [f"--- Slide {slide_num} ---"]

        for shape in slide.shapes:
            # Text frames: titles, body text, bullet points
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    text = para.text.strip()
                    if text:
                        slide_blocks.append(text)

            # Tables: comparison slides, data slides
            if shape.has_table:
                for row in shape.table.rows:
                    row_texts = [
                        cell.text.strip()
                        for cell in row.cells
                        if cell.text.strip()
                    ]
                    if row_texts:
                        slide_blocks.append(" | ".join(row_texts))

        # Speaker notes
        if slide.has_notes_slide:
            notes_frame = slide.notes_slide.notes_text_frame
            if notes_frame:
                notes_text = notes_frame.text.strip()
                if notes_text and notes_text != "":
                    slide_blocks.append(f"[Notes: {notes_text}]")

        if len(slide_blocks) > 1:
            slides_text.append("\n".join(slide_blocks))

    if not slides_text:
        raise ValueError("No extractable text found in PPTX file.")

    logger.info(f"Extracted text from {len(slides_text)} slide(s)")
    return "\n\n".join(slides_text)