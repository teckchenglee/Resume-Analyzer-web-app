"""
main.py — CLI entry point for the Résumé × JD Analyzer.

Task 5 of the lab (Track A).
Study material reference: §4 The Multi-Stage Pipeline

Your job is to write the main() function. The argument parser is already
provided — do not modify parse_args().
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from parse import read_resume_pdf, read_jd_text
from analyzer import (
    extract_resume_profile,
    extract_jd_profile,
    analyse_keyword_match,
    analyse_bullets,
    analyse_jargon,
    analyse_structure,
    analyse_background_fit,
    summarise_overall,
    compute_overall_score,
)
from report import render_markdown


ATS_PASS_THRESHOLD = 60


def parse_args(argv: list[str]) -> tuple[str, str]:
    """
    Parse command-line arguments. Pre-provided — do not modify.

    Usage:
        python main.py path/to/resume.pdf path/to/job_description.txt
    """
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="Résumé × JD Analyzer — diagnostic feedback only.",
    )
    parser.add_argument("resume", metavar="resume.pdf", help="Path to the PDF résumé.")
    parser.add_argument("job", metavar="job.txt", help="Path to the plain-text job description.")
    args = parser.parse_args(argv[1:])
    return args.resume, args.job


def main() -> int:
    """
    Orchestrate the full analysis pipeline. Return 0 on success, 1 on error.
	
    Steps to implement:
      [1/8] Parse CLI arguments (call parse_args(sys.argv)).
      [2/8] Load documents — call read_resume_pdf() and read_jd_text();
            catch ValueError and print to stderr, then return 1.
      [3/8] Extract structured profiles — call extract_resume_profile() and
            extract_jd_profile(); print progress as "[3/8] Extracting profiles…".
      [4/8] Run the 5 evaluations in order:
              analyse_keyword_match(resume_profile, jd_profile)
              analyse_bullets(resume_profile)
              analyse_jargon(resume_profile, jd_profile)
              analyse_structure(resume_text)
              analyse_background_fit(resume_profile, jd_profile)
            Print a [4/8]…[8/8] progress line for each.
      [9/9] Assemble the report dict:
              {
                "resume_profile":  resume_profile,
                "jd_profile":      jd_profile,
                "keyword_match":   keyword_match,
                "bullets":         bullets,
                "jargon":          jargon,
                "structure":       structure,
                "background_fit":  background_fit,
              }
            Compute overall_score with compute_overall_score(report).
            Add to report:
              report["overall_score"]       = overall_score
              report["passes_ats_threshold"] = overall_score >= ATS_PASS_THRESHOLD
              report["summary"]             = summarise_overall(report)

            Build a timestamped filename:
              ts = datetime.now().strftime("%Y%m%d_%H%M%S")
              json_path = Path("outputs") / f"match_report_{ts}.json"
              md_path   = Path("outputs") / f"match_report_{ts}.md"

            Save JSON: json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            Save Markdown: render_markdown(report, out_path=md_path)

            Print the final verdict and the 3-bullet summary.
            Return 0.
    """
    # [1/8] Parse CLI arguments
    resume_path, job_path = parse_args(sys.argv)

    # [2/8] Load documents
    print("[2/8] Loading documents...")
    try:
        resume_text = read_resume_pdf(resume_path)
        jd_text = read_jd_text(job_path)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1

    # [3/8] Extract structured profiles
    print("[3/8] Extracting profiles...")
    resume_profile = extract_resume_profile(resume_text)
    jd_profile = extract_jd_profile(jd_text)

    # [4/8] Keyword match
    print("[4/8] Analysing keyword match...")
    keyword_match = analyse_keyword_match(resume_profile, jd_profile)

    # [5/8] Bullet quality
    print("[5/8] Analysing bullet points...")
    bullets = analyse_bullets(resume_profile)

    # [6/8] Jargon
    print("[6/8] Analysing jargon...")
    jargon = analyse_jargon(resume_profile, jd_profile)

    # [7/8] Structure
    print("[7/8] Analysing structure...")
    structure = analyse_structure(resume_text)

    # [8/8] Background fit
    print("[8/8] Analysing background fit...")
    background_fit = analyse_background_fit(resume_profile, jd_profile)

    # [9/9] Assemble report
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
    report["passes_ats_threshold"] = (
        overall_score >= ATS_PASS_THRESHOLD
    )
    report["summary"] = summarise_overall(report)

    # Create output directory if needed
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"match_report_{ts}.json"
    md_path = output_dir / f"match_report_{ts}.md"

    json_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )
    render_markdown(report, out_path=md_path)

    # Final output
    verdict = (
        "PASS"
        if report["passes_ats_threshold"]
        else "FAIL"
    )
    print(f"\nATS Verdict: {verdict} ({overall_score}/100)")

    for bullet in report["summary"][:3]:
        print(f"- {bullet}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
