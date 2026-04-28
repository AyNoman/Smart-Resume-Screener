from pathlib import Path

import pdfplumber
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    try:
        pages_text = []

        with pdfplumber.open(file_path) as pdf:
            if len(pdf.pages) == 0:
                raise ValueError("The uploaded PDF has no pages.")

            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)

        final_text = "\n".join(pages_text).strip()

        if len(final_text) < 30:
            raise ValueError(
                "Could not extract enough text from the PDF. "
                "This may be a scanned or image-based PDF."
            )

        return final_text

    except Exception as e:
        raise ValueError(f"PDF parsing failed: {str(e)}")


def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
        final_text = "\n".join(paragraphs).strip()

        if len(final_text) < 20:
            raise ValueError("The DOCX file appears empty or has very little readable text.")

        return final_text

    except Exception as e:
        raise ValueError(f"DOCX parsing failed: {str(e)}")


def extract_text_from_txt(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read().strip()

        if len(text) < 20:
            raise ValueError("The TXT file appears empty or too short.")

        return text

    except Exception as e:
        raise ValueError(f"TXT parsing failed: {str(e)}")


def get_resume_text(resume_text_input: str, resume_file_path: str | None) -> str:
    has_text = bool(resume_text_input and resume_text_input.strip())
    has_file = bool(resume_file_path)

    if not has_text and not has_file:
        raise ValueError("Please either paste resume text or upload a resume file.")

    if has_file:
        suffix = Path(resume_file_path).suffix.lower()

        if suffix == ".pdf":
            return extract_text_from_pdf(resume_file_path)
        elif suffix == ".docx":
            return extract_text_from_docx(resume_file_path)
        elif suffix == ".txt":
            return extract_text_from_txt(resume_file_path)
        else:
            raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT only.")

    return resume_text_input.strip()
