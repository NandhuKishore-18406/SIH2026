# SIH 2026 - Skill-Gap Analyzer: Stage 1 Document Extraction & Cleaning

An AI-based Skill-Gap Analyzer designed to compare academic syllabi with industry requirements. 

This repository contains **Stage 1** of the pipeline: reliable, page-aware text extraction and conservative text cleaning for **PDF** and **DOCX** documents.

---

## 📌 Architectural Pipeline

```
PDF / DOCX Document
        ↓
Text Extraction (PyMuPDF / python-docx)
        ↓
Page-Aware Document Representation (Pydantic Models)
        ↓
Conservative Text Cleaning (Null char removal, space normalization)
        ↓
Page-Aware JSON Output
```

> **Note:** This stage strictly focuses on document parsing and conservative cleaning. AI/NLP tasks like OCR, skill extraction, embeddings, and skill-gap scoring will be added in subsequent stages.

---

## 📂 Project Structure

```
sih2026/
├── data/
│   ├── input/             # Place input PDF and DOCX documents here
│   └── output/            # Generated page-aware JSON output files
├── src/
│   └── sih2026/
│       ├── __init__.py
│       ├── main.py        # CLI entry point for the pipeline
│       ├── extraction/    # Extractor modules for PDF & DOCX
│       │   ├── __init__.py
│       │   ├── docx.py
│       │   ├── exceptions.py
│       │   └── pdf.py
│       ├── models/        # Pydantic data models
│       │   ├── __init__.py
│       │   └── document.py
│       └── processing/    # Conservative text cleaner
│           ├── __init__.py
│           └── cleaner.py
├── tests/                 # Comprehensive Pytest suite
│   ├── test_cleaner.py
│   ├── test_document.py
│   ├── test_docx.py
│   ├── test_main.py
│   └── test_pdf.py
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock                # Locked dependency tree
└── README.md
```

---

## 🚀 Quick Start & How to Run

### Prerequisites
- [uv](https://github.com/astral-sh/uv) package manager installed.
- Python `>= 3.14` (or compatible version managed by `uv`).

### 1. Install Dependencies
Dependencies are managed automatically with `uv`. To sync the environment:
```bash
uv sync
```

### 2. Run Document Processing

Run the main script against any `.pdf` or `.docx` file in `data/input/`:

```bash
# Process a PDF file
uv run python -m sih2026.main data/input/syllabus.pdf

# Process a DOCX file
uv run python -m sih2026.main data/input/syllabus.docx
```

Alternatively, if installed as a CLI tool:
```bash
uv run sih2026 data/input/syllabus.pdf
```

### 3. Output Format
The resulting JSON file will be saved in `data/output/<filename_stem>.json`.

**Sample JSON Output (`data/output/syllabus.json`):**
```json
{
  "filename": "syllabus.pdf",
  "pages": [
    {
      "page_number": 1,
      "text": "UNIT I: INTRODUCTION TO DATA SCIENCE\nConcepts of Big Data, Data Processing Pipeline.\nTools and Frameworks.",
      "extraction_method": "text"
    },
    {
      "page_number": 2,
      "text": "UNIT II: MACHINE LEARNING ALGORITHMS\nSupervised vs Unsupervised Learning.\nDecision Trees & Random Forests.",
      "extraction_method": "text"
    }
  ]
}
```

---

## ⚙️ How the Pipeline Process Works

1. **Extraction**:
   - **PDFs**: Uses `PyMuPDF` (`pymupdf`) to extract text page-by-page. Page boundaries (1-indexed) and layout line breaks (`\n`) are strictly preserved so later NLP modules can trace topics back to their original page.
   - **DOCX**: Uses `python-docx` to iterate through paragraphs and table elements in exact visual sequence.

2. **Conservative Cleaning**:
   - Removes null characters (`\x00`).
   - Normalizes horizontal spaces/tabs without affecting meaningful line breaks.
   - Collapses excessive blank lines (caps gaps at a maximum of 2 newlines).
   - **Preserves original wording, casing, punctuation, and academic terminology intact.**

3. **Data Validation & Output**:
   - Structured using Pydantic models (`Document` and `DocumentPage`).
   - Written to disk as UTF-8 encoded, human-readable indented JSON.

---

## 🛠️ How to Add New File Extensions & Extractors

To extend support for additional file types (e.g., `.txt`, `.pptx`, `.html` or adding OCR for scanned PDFs):

### Step 1: Create a New Extractor Module
Add a new extractor file under `src/sih2026/extraction/`, e.g., `src/sih2026/extraction/txt.py`:

```python
# src/sih2026/extraction/txt.py
from pathlib import Path
from sih2026.models.document import Document, DocumentPage
from sih2026.extraction.exceptions import UnsupportedFileTypeError, NoTextExtractedError

def extract_txt(file_path: str | Path) -> Document:
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() != ".txt":
        raise UnsupportedFileTypeError(f"Expected .txt file, got '{path.suffix}'")
        
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise NoTextExtractedError(f"TXT file '{path}' is empty.")
        
    pages = [
        DocumentPage(
            page_number=1,
            text=text,
            extraction_method="txt"
        )
    ]
    return Document(filename=path.name, pages=pages)
```

### Step 2: Export in `src/sih2026/extraction/__init__.py`
Update `src/sih2026/extraction/__init__.py` to re-export the new extractor function:

```python
from sih2026.extraction.txt import extract_txt

__all__ = [
    "extract_pdf",
    "extract_docx",
    "extract_txt",
    # ...
]
```

### Step 3: Register Extension in `src/sih2026/main.py`
Add the file extension handler to the `process_document` function in `src/sih2026/main.py`:

```python
# In src/sih2026/main.py
from sih2026.extraction.txt import extract_txt

def process_document(input_path: Path) -> Path:
    suffix = input_path.suffix.lower()
    if suffix == ".pdf":
        raw_doc = extract_pdf(input_path)
    elif suffix == ".docx":
        raw_doc = extract_docx(input_path)
    elif suffix == ".txt":
        raw_doc = extract_txt(input_path)
    else:
        raise ValueError(f"Unsupported file format '{input_path.suffix}'")
```

### Step 4: Add Unit Tests
Create `tests/test_txt.py` to cover success, missing file, and empty file cases.

---

## 🧪 Running Tests

Run the full pytest test suite:
```bash
uv run pytest
```

To run tests with detailed output:
```bash
uv run pytest -v
```
