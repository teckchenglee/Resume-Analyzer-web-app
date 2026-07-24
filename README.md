# Resume Analyzer

Analyse your résumé against a job description you're applying to, powered by
Google's Gemini model. It mimics how an Applicant Tracking System (ATS) screens
candidates, scoring keyword match, bullet quality, jargon, structure, and
background fit against the JD — giving you a clear PASS/FAIL verdict and the
concrete strengths/weaknesses to edit your résumé around, so you have a better
chance of getting the interview.

It parses a résumé PDF and a job description, then runs a multi-stage LLM pipeline
to produce a 0–100 score, a PASS/FAIL verdict, and a downloadable Markdown/JSON
report.

Available both as a CLI tool and a Streamlit web app.

**Live demo:** [resume-analyzer-w.streamlit.app](https://resume-analyzer-w.streamlit.app/)

## Features

- **Keyword match** — compares résumé skills/experience against JD requirements
- **Bullet quality** — flags weak or unquantified bullet points
- **Jargon audit** — catches buzzwords/jargon that may hurt ATS parsing
- **Structure audit** — checks résumé formatting/section structure
- **Background fit** — narrative assessment of overall alignment with the JD
- **Overall score** — weighted 0–100 score with a PASS/FAIL verdict (threshold: 60)
- Reports exportable as Markdown and JSON

## Requirements

- Python 3.10+
- One of:
  - A local [Ollama](https://ollama.com) server (default, no API key needed)
  - An OpenAI API key
  - An Anthropic API key

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root:

   ```env
   # Model to use, as a LiteLLM-style "<provider>/<model>" string.
   #   ollama/...    — local; requires `ollama serve` and the model pulled; no API key
   #   openai/...    — cloud; requires OPENAI_API_KEY
   #   anthropic/... — cloud; requires ANTHROPIC_API_KEY
   MODEL=ollama/gemma4:e2b

   # Only needed if MODEL uses the ollama/ prefix and Ollama isn't on the default host.
   OLLAMA_API_BASE=http://localhost:11434

   # Only needed if MODEL uses the openai/ or anthropic/ prefix.
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   ```

## Usage

### CLI

```bash
python main.py path/to/resume.pdf path/to/job_description.txt
```

This prints progress for each pipeline stage, then a final verdict and 3-bullet
summary. Full reports are saved to `outputs/match_report_<timestamp>.{json,md}`.

### Web app (Streamlit)

```bash
streamlit run app.py
```

Upload a résumé PDF, paste the job description text, and click **Analyze Resume**
to see the score breakdown in-browser, with Markdown/JSON report downloads.

## Project structure

| File          | Responsibility                                              |
|---------------|--------------------------------------------------------------|
| `main.py`     | CLI entry point — orchestrates the full analysis pipeline    |
| `app.py`      | Streamlit web UI — same pipeline, interactive front end      |
| `parse.py`    | PDF/text extraction (no LLM calls)                            |
| `analyzer.py` | The 5 evaluation stages + scoring/summary logic               |
| `llm.py`      | Single LiteLLM wrapper (`ask_json` / `ask_text`) used by all LLM calls |
| `prompts.py`  | Prompt templates for each analysis stage                      |
| `report.py`   | Renders the report dict to Markdown                            |

## Notes

- Résumés longer than 2 pages trigger a warning (ATS systems typically expect one page).
- Image-only/scanned PDFs with no text layer will raise an error.
- Job descriptions under 100 characters are rejected as likely incomplete pastes.
