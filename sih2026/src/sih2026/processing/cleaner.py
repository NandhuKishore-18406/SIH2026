"""Conservative text cleaner module."""

import re
from sih2026.models.document import Document, DocumentPage


def clean_text(text: str) -> str:
    """Conservatively cleans raw extracted text.

    Removes null characters, excessive horizontal spaces/tabs, and excessive
    blank lines while keeping meaningful line breaks, punctuation, and wording intact.

    Args:
        text: Raw text string.

    Returns:
        Cleaned text string.
    """
    if not text:
        return ""

    # 1. Remove null characters
    text = text.replace("\x00", "")

    # 2. Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 3. Clean horizontal whitespace line-by-line while preserving line breaks
    cleaned_lines = [re.sub(r"[ \t]+", " ", line).rstrip() for line in text.split("\n")]
    text = "\n".join(cleaned_lines)

    # 4. Collapse 3 or more consecutive blank lines into 2 (1 empty line gap)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_document(document: Document) -> Document:
    """Returns a new Document with conservatively cleaned page texts.

    Args:
        document: The input Document instance.

    Returns:
        Document: A new Document with cleaned page text.
    """
    cleaned_pages = [
        DocumentPage(
            page_number=page.page_number,
            text=clean_text(page.text),
            extraction_method=page.extraction_method,
        )
        for page in document.pages
    ]
    return Document(filename=document.filename, pages=cleaned_pages)
