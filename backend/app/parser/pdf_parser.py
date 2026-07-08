from dataclasses import dataclass

import fitz

from app.utils.exceptions import ResumeParsingFailed


@dataclass(frozen=True)
class ParsedPdf:
    text: str
    page_count: int


class PdfParser:
    """Extract text content from PDF resume bytes."""

    @staticmethod
    def extract_text(file_bytes: bytes) -> ParsedPdf:
        try:
            with fitz.open(stream=file_bytes, filetype="pdf") as document:
                page_text = [page.get_text("text") for page in document]
                text = "\n".join(page_text).strip()
                page_count = document.page_count
        except Exception as exc:
            raise ResumeParsingFailed("Unable to parse the uploaded PDF.") from exc

        if not text:
            raise ResumeParsingFailed(
                "No readable text was found in the uploaded PDF.",
            )

        return ParsedPdf(text=text, page_count=page_count)
