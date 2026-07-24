import json
from datetime import datetime
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv

from parse import read_resume_pdf
from analyzer import (
    extract_resume_profile, extract_jd_profile, analyse_keyword_match,
    analyse_bullets, analyse_jargon, analyse_structure,
    analyse_background_fit, summarise_overall, compute_overall_score,
)
from report import render_markdown

load_dotenv()

ATS_PASS_THRESHOLD = 60
_MIN_JD_CHARS = 100

st.set_page_config(page_title="Resume Analyzer", layout="wide")
st.title("📄 AI Resume Analyzer")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
jd_text = st.text_area("Paste Job Description", height=250)
run = st.button("Analyze Resume")

if run:
    if not resume_file or not jd_text.strip():
        st.error("Please upload resume and paste job description.")
        st.stop()
    if len(jd_text.strip()) < _MIN_JD_CHARS:
        st.error(f"Job description looks too short ({len(jd_text.strip())} chars); did you forget to paste the full text?")
        st.stop()

    progress = st.progress(0.0)
    status = st.empty()

    def step(n: int, label: str) -> None:
        status.write(f"[{n}/8] {label}…")
        progress.progress(n / 8)

    try:
        step(1, "Reading résumé PDF")
        resume_text = read_resume_pdf(resume_file)
        jd_text_clean = jd_text.strip()

        step(2, "Extracting résumé profile")
        resume_profile = extract_resume_profile(resume_text)

        step(3, "Extracting JD profile")
        jd_profile = extract_jd_profile(jd_text_clean)

        step(4, "Analysing keyword match")
        keyword_match = analyse_keyword_match(resume_profile, jd_profile)

        step(5, "Analysing bullet points")
        bullets = analyse_bullets(resume_profile)

        step(6, "Analysing jargon")
        jargon = analyse_jargon(resume_profile, jd_profile)

        step(7, "Analysing structure")
        structure = analyse_structure(resume_text)

        step(8, "Analysing background fit")
        background_fit = analyse_background_fit(resume_profile, jd_profile)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    status.write("Assembling report…")
    progress.progress(1.0)

    report = {
        "resume_profile": resume_profile,
        "jd_profile": jd_profile,
        "keyword_match": keyword_match,
        "bullets": bullets,
        "jargon": jargon,
        "structure": structure,
        "background_fit": background_fit,
    }
    overall_score = compute_overall_score(report)
    report["overall_score"] = overall_score
    report["passes_ats_threshold"] = overall_score >= ATS_PASS_THRESHOLD
    report["summary"] = summarise_overall(report)

    status.empty()
    progress.empty()

    verdict = "PASS" if report["passes_ats_threshold"] else "FAIL"
    verdict_color = "green" if verdict == "PASS" else "red"
    st.header(f":{verdict_color}[{verdict}] — {overall_score}/100")
    st.caption(f"ATS pass threshold: {ATS_PASS_THRESHOLD}/100")

    for bullet in report["summary"].strip().split("\n")[:3]:
        if bullet.strip():
            st.markdown(bullet)

    with st.expander("Keyword Match", expanded=True):
        st.write(f"Score: {keyword_match.get('keyword_match_score', 0)}/100")
        col1, col2 = st.columns(2)
        col1.write("**Present**")
        col1.write([p.get("keyword") for p in keyword_match.get("present", [])])
        col2.write("**Missing**")
        col2.write([m.get("keyword") for m in keyword_match.get("missing", [])])

    with st.expander("Bullet Quality"):
        st.write(f"Average score: {bullets.get('bullet_quality_avg', 0)}/100")
        st.json(bullets.get("bullets", []))

    with st.expander("Jargon Audit"):
        st.write(f"Score: {jargon.get('jargon_score', 0)}/100")
        st.json(jargon.get("flags", []))

    with st.expander("Structure Audit"):
        st.write(f"Score: {structure.get('structure_score', 0)}/100")
        st.json(structure)

    with st.expander("Background Fit"):
        st.write(f"Score: {background_fit.get('background_fit_score', 0)}/100")
        st.write(background_fit.get("alignment_commentary", ""))

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_buffer = BytesIO()
    md_path = f"/tmp/match_report_{ts}.md"
    render_markdown(report, out_path=md_path)
    with open(md_path, "rb") as f:
        md_bytes = f.read()

    dl_col1, dl_col2 = st.columns(2)
    dl_col1.download_button(
        "Download Markdown Report", md_bytes,
        file_name=f"match_report_{ts}.md", mime="text/markdown",
    )
    dl_col2.download_button(
        "Download JSON Report", json.dumps(report, indent=2),
        file_name=f"match_report_{ts}.json", mime="application/json",
    )
