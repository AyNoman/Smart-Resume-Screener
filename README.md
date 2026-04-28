# Smart Resume Screener

A Python + Gradio app that compares a resume against a job description and returns:

- final match score
- fit level
- matched skills
- missing skills
- important job keywords
- improvement suggestions

It supports:
- pasted resume text
- PDF upload
- DOCX upload
- TXT upload

## Features

- NLP-based resume vs JD comparison
- weighted scoring logic
- skill extraction using a curated skills catalog
- keyword coverage analysis
- safer PDF/DOCX/TXT error handling
- simple and clean Gradio UI

## Project Structure

```text
smart-resume-screener/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── parsers.py
│   ├── preprocessing.py
│   ├── analyzer.py
│   └── ui_helpers.py
│
└── assets/
    └── screenshot.png
```

## Installation

```bash
pip install -r requirements.txt
```

## Run the App

```bash
python app.py
```

## How It Works

1. User pastes resume text or uploads a PDF/DOCX/TXT resume.
2. User pastes a job description.
3. The app cleans both texts.
4. It extracts skills from the resume and job description.
5. It computes:
   - text similarity
   - skill match
   - keyword coverage
   - experience alignment
6. It combines these into a final weighted score.
7. It returns missing skills and improvement suggestions.

## Scoring Logic

The final score is based on:

- 45% text similarity
- 35% skill match
- 10% keyword coverage
- 10% experience alignment

## Notes

- PDF extraction works best for text-based PDFs.
- Scanned or image-only PDFs may fail because OCR is not included.
- This project is intended as an educational portfolio project.

## Screenshot

Add a screenshot at:

```text
assets/screenshot.png
```

Then display it here:

```markdown
![App Screenshot](assets/screenshot.png)
```
