import plotly.graph_objects as go


def build_score_chart(summary_dict: dict):
    labels = []
    values = []

    for key in ["Text Similarity", "Skill Match", "Keyword Coverage", "Experience Alignment"]:
        labels.append(key)
        values.append(float(str(summary_dict[key]).replace("%", "")))

    fig = go.Figure(
        data=[
            go.Bar(
                x=labels,
                y=values,
                text=[f"{v}%" for v in values],
                textposition="auto"
            )
        ]
    )

    fig.update_layout(
        title="Scoring Breakdown",
        yaxis_title="Score",
        xaxis_title="Metric",
        template="plotly_white",
        height=360
    )

    return fig


def format_list_html(items: list[str], empty_message: str = "None found") -> str:
    if not items:
        return f"<div class='empty-note'>{empty_message}</div>"

    html = "<ul class='result-list'>"
    for item in items:
        html += f"<li>{item.title()}</li>"
    html += "</ul>"
    return html
