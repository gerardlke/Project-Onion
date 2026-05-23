from docx import Document
from fastapi import UploadFile
from io import BytesIO


async def extract_text(file: UploadFile) -> str:
    """Extracts file extension for specific text extraction

    Input:

    Ouput:
    """
    extension = file.filename.split(".")[-1].lower()

    if extension in ["txt", "md"]:
        return await extract_text_file(file)

    elif extension == "docx":
        return await extract_docx_file(file)

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )


async def extract_text_file(file: UploadFile) -> str:
    """Extracts text from txt file

    Input:
    
    Ouput:
    """
    contents = await file.read()
    return contents.decode("utf-8")


async def extract_docx_file(file: UploadFile) -> str:
    """Extracts text from docx file

    Input:
    
    Ouput:
    """
    contents = await file.read()
    doc = Document(BytesIO(contents))

    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)

    return "\n".join(full_text)