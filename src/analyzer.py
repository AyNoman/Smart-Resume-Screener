import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import SKILLS_CATALOG
from src.parsers import get_resume_text
from src.preprocessing import clean_text, extract_skills, extract_top_keywords, unique_preserve_order


def extract_experience_years(text: str) -> int:
    text = text.lower()

    patterns = [
        r"(\d+)\+?\s+years",
        r"(\d+)\+?\s+yrs",
        r"(\d+)\+?\s+year",
        r"experience\s+of\s+(\d+)\+?\s+years",
    ]

    found = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            try:
                found.append(int(m))
            except ValueError:
                pass

    return max(found) if found else 0


def compute_text_similarity(resume_text: str, job_description: str) -> float:
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=1
    )

    matrix = vectorizer.fit_transform([resume_text, job_description])
    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    return round(float(score) * 100, 2)


def compute_skill_match_details(resume_skills: list[str], jd_skills: list[str]) -> dict:
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    matched = sorted(list(resume_set & jd_set))
    missing = sorted(list(jd_set - resume_set))

    if not jd_set:
        match_percent = 0.0
    else:
        match_percent = round((len(matched) / len(jd_set)) * 100, 2)

    return {
        "matched": matched,
        "missing": missing,
        "match_percent": match_percent
    }


def compute_keyword_bonus(resume_text: str, top_keywords: list[str]) -> float:
    resume_text = resume_text.lower()

    if not top_keywords:
        return 0.0

    hits = 0
    for kw in top_keywords:
        if re.search(r"\b" + re.escape(kw.lower()) + r"\b", resume_text):
            hits += 1

    return round((hits / len(top_keywords)) * 100, 2)


def compute_experience_alignment(resume_text: str, job_description: str) -> float:
    resume_years = extract_experience_years(resume_text)
    jd_years = extract_experience_years(job_description)

    if jd_years == 0:
        return 100.0

    if resume_years == 0:
        return 30.0

    ratio = min(resume_years / jd_years, 1.0)
    return round(ratio * 100, 2)


def compute_final_score_components(
    resume_text: str,
    job_description: str,
    resume_skills: list[str],
    jd_skills: list[str],
    top_keywords: list[str]
) -> dict:
    text_similarity = compute_text_similarity(resume_text, job_description)
    skill_details = compute_skill_match_details(resume_skills, jd_skills)
    keyword_coverage = compute_keyword_bonus(resume_text, top_keywords)
    experience_alignment = compute_experience_alignment(resume_text, job_description)

    final_score = round(
        (0.45 * text_similarity) +
        (0.35 * skill_details["match_percent"]) +
        (0.10 * keyword_coverage) +
        (0.10 * experience_alignment),
        2
    )

    return {
        "text_similarity": text_similarity,
        "skill_match": skill_details["match_percent"],
        "keyword_coverage": keyword_coverage,
        "experience_alignment": experience_alignment,
        "final_score": final_score,
        "matched_skills": skill_details["matched"],
        "missing_skills": skill_details["missing"]
    }


def get_fit_label(score: float) -> str:
    if score >= 82:
        return "Strong Match"
    if score >= 65:
        return "Moderate Match"
    return "Weak Match"


def build_suggestions(missing_skills: list[str], fit_label: str, score_components: dict) -> list[str]:
    suggestions = []

    suggestion_map = {
        "python": "Add Python-based projects, scripts, or measurable work outcomes.",
        "sql": "Include SQL querying, joins, reporting, or database work.",
        "excel": "Mention Excel reporting, pivot tables, formulas, or dashboards.",
        "power bi": "Add dashboard or BI reporting examples using Power BI.",
        "tableau": "Mention Tableau dashboards or equivalent analytics visualization work.",
        "git": "Add version control usage, team collaboration, or GitHub project links.",
        "docker": "Mention deployment, containers, or reproducible environments using Docker.",
        "aws": "Highlight cloud exposure such as deployment, storage, or compute services.",
        "machine learning": "Include ML models, evaluation metrics, and practical projects.",
        "communication": "Add examples of teamwork, presentations, or stakeholder communication.",
        "leadership": "Mention ownership, initiative, or leading a task or team.",
        "teamwork": "Show collaboration experience with teams, clients, or cross-functional groups."
    }

    for skill in missing_skills[:5]:
        if skill in suggestion_map:
            suggestions.append(suggestion_map[skill])
        else:
            suggestions.append(f"Add stronger evidence for {skill.title()} if you have relevant experience.")

    if score_components["experience_alignment"] < 60:
        suggestions.append("Make your experience level clearer by explicitly mentioning years of relevant work or projects.")

    if score_components["text_similarity"] < 55:
        suggestions.append("Tailor the wording of your resume to better reflect the job description and target role.")

    if fit_label == "Weak Match":
        suggestions.append("Rework the resume for this specific role instead of sending a general version.")

    return unique_preserve_order(suggestions)[:6]


def analyze_resume_against_jd(resume_text_input: str, resume_file_path: str | None, job_description: str):
    if not job_description or not job_description.strip():
        raise ValueError("Please paste a job description.")

    resume_text = get_resume_text(resume_text_input, resume_file_path)

    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text could not be read.")

    cleaned_resume = clean_text(resume_text)
    cleaned_jd = clean_text(job_description)

    resume_skills = extract_skills(cleaned_resume, SKILLS_CATALOG)
    jd_skills = extract_skills(cleaned_jd, SKILLS_CATALOG)
    top_keywords = extract_top_keywords(cleaned_jd, top_n=15)

    score_components = compute_final_score_components(
        resume_text=cleaned_resume,
        job_description=cleaned_jd,
        resume_skills=resume_skills,
        jd_skills=jd_skills,
        top_keywords=top_keywords
    )

    fit_label = get_fit_label(score_components["final_score"])

    suggestions = build_suggestions(
        missing_skills=score_components["missing_skills"],
        fit_label=fit_label,
        score_components=score_components
    )

    summary = {
        "Final Match Score": f"{score_components['final_score']}%",
        "Fit Level": fit_label,
        "Text Similarity": f"{score_components['text_similarity']}%",
        "Skill Match": f"{score_components['skill_match']}%",
        "Keyword Coverage": f"{score_components['keyword_coverage']}%",
        "Experience Alignment": f"{score_components['experience_alignment']}%"
    }

    return {
        "summary": summary,
        "matched_skills": score_components["matched_skills"],
        "missing_skills": score_components["missing_skills"],
        "top_keywords": top_keywords,
        "suggestions": suggestions,
        "resume_text_preview": resume_text[:1500]
    }
