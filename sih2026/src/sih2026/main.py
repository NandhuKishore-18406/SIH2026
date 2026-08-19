"""Main entry point for document extraction and cleaning pipeline."""

import json
import sys
from pathlib import Path

from sih2026.extraction.docx import extract_docx
from sih2026.extraction.exceptions import DocumentExtractionError
from sih2026.extraction.pdf import extract_pdf
from sih2026.processing.cleaner import clean_document


def process_document(input_path: Path) -> Path:
    """Extracts, cleans, and converts a document into page-aware JSON.

    Args:
        input_path: Path to the input PDF or DOCX file.

    Returns:
        Path to the generated JSON output file.
    """
    suffix = input_path.suffix.lower()
    if suffix == ".pdf":
        raw_doc = extract_pdf(input_path)
    elif suffix == ".docx":
        raw_doc = extract_docx(input_path)
    else:
        raise ValueError(
            f"Unsupported file format '{input_path.suffix}'. Supported formats are .pdf and .docx"
        )

    cleaned_doc = clean_document(raw_doc)

    output_dir = Path("data/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{input_path.stem}.json"

    # Serialize using model_dump for human-readable UTF-8 JSON output
    data = cleaned_doc.model_dump()
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return output_file


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage:")
        print("    uv run python -m sih2026.main <document>")
        sys.exit(1)

    input_file = Path(sys.argv[1])

    try:
        output_file = process_document(input_file)
        print(f"Successfully processed '{input_file.name}' -> '{output_file}'")
    except (FileNotFoundError, ValueError, DocumentExtractionError) as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
