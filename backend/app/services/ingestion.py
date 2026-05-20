from pathlib import Path
from docx import Document


# TODO: Move to config file later
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

def extract_text(file_path: Path) -> str:
    """Extracts file extension for specific text extraction

    Input:

    Ouput:
    """

    suffix = file_path.suffix.lower()

    if suffix == ".txt":
        return extract_txt(file_path)
    elif suffix == ".md":
        return extract_txt(file_path)
    elif suffix == ".docx":
        return extract_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def extract_txt(file_path: Path) -> str:
    """Extracts text from txt file

    Input:
    
    Ouput:
    """

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def extract_docx(file_path: Path) -> str:
    """Extracts text from docx file

    Input:
    
    Ouput:
    """

    doc = Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return "\n".join(full_text)