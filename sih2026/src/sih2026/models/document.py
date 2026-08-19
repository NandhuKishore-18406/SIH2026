"""Document data models using Pydantic."""

from pydantic import BaseModel, Field


class DocumentPage(BaseModel):
    """Represents a single page in a document."""

    page_number: int = Field(..., description="1-indexed page number of the document")
    text: str = Field(..., description="Extracted text content of the page")
    extraction_method: str = Field(
        ..., description="Method used to extract text (e.g., 'text', 'docx')"
    )


class Document(BaseModel):
    """Represents a full document containing page-level extracted data."""

    filename: str = Field(..., description="Name of the document file")
    pages: list[DocumentPage] = Field(
        default_factory=list, description="List of document pages"
    )
