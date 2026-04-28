import gradio as gr
import pandas as pd
import plotly.graph_objects as go

from src.analyzer import analyze_resume_against_jd
from src.ui_helpers import build_score_chart, format_list_html


def app_runner(resume_text_input, resume_file_path, job_description):
    try:
        result = analyze_resume_against_jd(
            resume_text_input=resume_text_input,
            resume_file_path=resume_file_path,
            job_description=job_description
        )

        summary_df = pd.DataFrame(
            {"Metric": list(result["summary"].keys()), "Value": list(result["summary"].values())}
        )

        chart = build_score_chart(result["summary"])
        matched_html = format_list_html(result["matched_skills"], "No matched skills found.")
        missing_html = format_list_html(result["missing_skills"], "No missing skills found.")
        keywords_html = format_list_html(result["top_keywords"], "No important keywords found.")
        suggestions_html = format_list_html(result["suggestions"], "No suggestions generated.")

        return summary_df, chart, matched_html, missing_html, keywords_html, suggestions_html

    except Exception as e:
        error_df = pd.DataFrame({"Metric": ["Error"], "Value": [str(e)]})
        empty_chart = go.Figure()
        return error_df, empty_chart, "", "", "", ""


custom_css = """
.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
    font-family: Inter, sans-serif !important;
}
.hero {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    padding: 24px 28px;
    border-radius: 20px;
    margin-bottom: 18px;
}
.card-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 6px;
}
.card-subtitle {
    font-size: 14px;
    opacity: 0.96;
    line-height: 1.7;
}
.result-list {
    padding-left: 18px;
    line-height: 1.8;
}
.empty-note {
    color: #64748b;
    font-style: italic;
}
"""

with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as demo:
    gr.HTML("""
    <div class="hero">
        <div class="card-title">Smart Resume Screener</div>
        <div class="card-subtitle">
            Compare a resume against a job description and get a match score, missing skills,
            keyword coverage, and improvement suggestions.
        </div>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=5):
            resume_text_box = gr.Textbox(
                label="Paste Resume Text",
                lines=14,
                placeholder="Paste resume text here..."
            )

            resume_file = gr.File(
                label="Or Upload Resume File (PDF / DOCX / TXT)",
                file_types=[".pdf", ".docx", ".txt"],
                type="filepath"
            )

        with gr.Column(scale=5):
            jd_text_box = gr.Textbox(
                label="Paste Job Description",
                lines=18,
                placeholder="Paste the job description here..."
            )

    analyze_btn = gr.Button("Analyze Resume", variant="primary")

    with gr.Row():
        summary_output = gr.Dataframe(label="Score Summary", interactive=False)

    with gr.Row():
        score_chart_output = gr.Plot(label="Scoring Breakdown")

    with gr.Row():
        with gr.Column():
            matched_output = gr.HTML(label="Matched Skills")
        with gr.Column():
            missing_output = gr.HTML(label="Missing Skills")

    with gr.Row():
        with gr.Column():
            keywords_output = gr.HTML(label="Important Job Keywords")
        with gr.Column():
            suggestions_output = gr.HTML(label="Improvement Suggestions")

    analyze_btn.click(
        fn=app_runner,
        inputs=[resume_text_box, resume_file, jd_text_box],
        outputs=[
            summary_output,
            score_chart_output,
            matched_output,
            missing_output,
            keywords_output,
            suggestions_output
        ]
    )

if __name__ == "__main__":
    demo.launch(debug=True)
