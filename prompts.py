"""
prompts.py — all 8 system prompts used by analyzer.py.

Task 3 of the lab (Track A).
Study material references:
  §3.3 Schema-First Prompt Design
  §6.1 Extraction Prompts
  §6.2 Evaluation Prompts
  §6.3 Feedback-Only Principle

Every prompt must follow ICCO structure:
  Instruction  — what the model must do
  Context      — relevant background (rubric description, schema description)
  Constraints  — rules the model must not break
  Output       — the exact JSON schema expected

Every prompt (except OVERALL_SUMMARY_PROMPT) must end with:
  "Output ONLY a valid JSON object matching the schema above. No prose. No
  markdown fences. No commentary. Never rewrite or generate résumé content."

Temperature guidance (set in the ask_json() call in analyzer.py):
  Extraction prompts (RESUME_PROFILE, JD_PROFILE): 0.0
  Evaluation prompts (KEYWORD_MATCH, BULLET_QUALITY, JARGON, STRUCTURE, BACKGROUND_FIT): 0.2–0.3
  OVERALL_SUMMARY_PROMPT: 0.3
"""


# ---------------------------------------------------------------------------
# Extraction prompts
# ---------------------------------------------------------------------------

# Purpose: extract a structured candidate profile from plain résumé text.
# Input to ask_json(): system=RESUME_PROFILE_PROMPT, user="RÉSUMÉ TEXT:\n\n{text}"
# Expected output schema — all fields required; arrays may be empty:
# {
#   "name": "string",
#   "contact": {
#     "email": "string", "phone": "string", "linkedin": "string",
#     "github": "string", "portfolio": "string"
#   },
#   "summary": "string",
#   "education": [{"school": "string", "degree": "string",
#                  "graduation_date": "string", "courses": ["string"]}],
#   "projects":  [{"title": "string", "date": "string", "bullets": ["string"]}],
#   "experience":[{"title": "string", "company": "string",
#                  "date": "string", "bullets": ["string"]}],
#   "skills": {
#     "languages": ["string"], "frameworks": ["string"], "tools": ["string"],
#     "concepts": ["string"], "platforms": ["string"]
#   }
# }
RESUME_PROFILE_PROMPT = """
INSTRUCTION:
You convert a résumé's plain text into a single structured JSON object.
Extract only what is literally present in the résumé text below — never
invent, guess, infer, or fill in a field with plausible-sounding content
that is not explicitly stated. If a field is not present anywhere in the
text, use an empty string "" for scalar fields or an empty array [] for
list fields. Every key in the schema must appear in your output.

CONTEXT:
Résumés vary widely in format: some list "Projects" separately from "Work
Experience", some combine them, some omit sections entirely. Identify each
section you can find (Summary, Education, Projects, Experience, Skills)
independently. Bullet points under a project or job must be copied
verbatim, character-for-character — do not paraphrase, shorten, reword, or
correct grammar/spelling in them. Sort each skill into the closest matching
category (languages, frameworks, tools, concepts, platforms) based on
common software/engineering usage; if unsure which category a skill
belongs to, place it under "tools".

CONSTRAINTS:
- Never invent a school, employer, date, contact detail, or skill that is
  not written in the text.
- Never rewrite, summarize, or improve any bullet — copy it exactly.
- Every field in the schema must be present in the output, even if empty.
- Arrays may be empty; do not pad them with placeholder entries.
- Do not add commentary about résumé quality — this is extraction only,
  not evaluation.

OUTPUT:
Return a single JSON object with exactly this shape:
{
  "name": "string",
  "contact": {
    "email": "string", "phone": "string", "linkedin": "string",
    "github": "string", "portfolio": "string"
  },
  "summary": "string",
  "education": [{"school": "string", "degree": "string",
                 "graduation_date": "string", "courses": ["string"]}],
  "projects":  [{"title": "string", "date": "string", "bullets": ["string"]}],
  "experience":[{"title": "string", "company": "string",
                 "date": "string", "bullets": ["string"]}],
  "skills": {
    "languages": ["string"], "frameworks": ["string"], "tools": ["string"],
    "concepts": ["string"], "platforms": ["string"]
  }
}

Output ONLY a valid JSON object matching the schema above. No prose. No
markdown fences. No commentary. Never rewrite or generate résumé content.
"""


# Purpose: extract a structured JD profile from free-form job posting text.
# Input to ask_json(): system=JD_PROFILE_PROMPT, user="JOB DESCRIPTION TEXT:\n\n{text}"
# Expected output schema — all fields required; arrays may be empty:
# {
#   "job_title": "string",
#   "company": "string",
#   "location": "string",
#   "experience_level": "string",
#   "required_skills": ["string"],
#   "preferred_skills": ["string"],
#   "tools_technologies": ["string"],
#   "responsibilities": ["string"],
#   "soft_skills": ["string"],
#   "buzzwords": ["string"],
#   "deal_breakers": ["string"]
# }
JD_PROFILE_PROMPT = """
INSTRUCTION:
You convert a job description's plain text into a single structured JSON
object. Extract only what is literally present in the text below — never
invent, guess, or infer a requirement, skill, or detail that is not
explicitly stated. If a field cannot be found anywhere in the text, use an
empty string "" for scalar fields or an empty array [] for list fields.

CONTEXT:
Job postings mix concrete requirements with marketing language, company
boilerplate, and culture-fit phrasing. Distinguish skills/technologies
stated as required ("required", "must have", "X years of experience in")
from those stated as preferred/nice-to-have ("bonus", "plus", "preferred",
"nice to have"). "buzzwords" means vague culture or soft-skill language
that does not map to a concrete, testable skill (e.g. "rockstar",
"fast-paced environment", "wear many hats", "self-starter").
"deal_breakers" means explicit hard requirements stated as mandatory,
disqualifying, or non-negotiable (e.g. required clearance, required
degree, minimum years of experience, on-site only).

CONSTRAINTS:
- Never invent a company name, location, or skill not written in the text.
- Classify each skill as required or preferred based only on the language
  actually used in the posting — do not guess based on typical industry
  norms.
- Every field in the schema must be present in the output, even if empty.
- Arrays may be empty; do not pad them with placeholder entries.
- Do not add commentary about the job posting's quality — this is
  extraction only.

OUTPUT:
Return a single JSON object with exactly this shape:
{
  "job_title": "string",
  "company": "string",
  "location": "string",
  "experience_level": "string",
  "required_skills": ["string"],
  "preferred_skills": ["string"],
  "tools_technologies": ["string"],
  "responsibilities": ["string"],
  "soft_skills": ["string"],
  "buzzwords": ["string"],
  "deal_breakers": ["string"]
}

Output ONLY a valid JSON object matching the schema above. No prose. No
markdown fences. No commentary. Never rewrite or generate résumé content.
"""


# ---------------------------------------------------------------------------
# Evaluation prompts
# ---------------------------------------------------------------------------

# Purpose: compare résumé keywords against JD requirements; produce a score.
# Input to ask_json():
#   system=KEYWORD_MATCH_PROMPT
#   user="RÉSUMÉ PROFILE:\n{json}\n\nJD PROFILE:\n{json}"
# Expected output schema:
# {
#   "present": [{"keyword": "string", "category": "language|framework|tool|concept|soft_skill|buzzword",
#                "found_in": "summary|projects|experience|education|skills", "exact_match": true}],
#   "missing": [{"keyword": "string", "category": "...", "importance": "required|preferred",
#                "suggested_section": "skills|projects|experience|summary",
#                "why_it_matters": "string (25 words max — diagnostic only)"}],
#   "keyword_match_score": 0
# }
# Scoring formula: 100 × (required_skills found in résumé) / max(1, total required_skills)
# IMPORTANT: the résumé and JD profiles are always provided in full, even when
# they share zero keywords — that is a normal, valid input, not a missing one.
# The model must still return the schema (an empty "present" array is a
# correct result) rather than asking for clarification or claiming no résumé
# was given. Small/local models are especially prone to breaking character on
# a total-mismatch input, so state this constraint explicitly.
KEYWORD_MATCH_PROMPT = """
INSTRUCTION:
You are given a structured résumé profile (JSON) and a structured job
description profile (JSON), both produced by a prior extraction step.
Compare the résumé's stated skills, summary, projects, and experience
against the JD's required_skills, preferred_skills, and
tools_technologies. Produce a list of keywords that are present in the
résumé and a list of JD keywords that are missing from the résumé, then
compute a match score.

CONTEXT:
This mirrors how an ATS keyword scanner and a recruiter's mental checklist
both work: they look for literal or near-literal overlap between JD
requirements and résumé content. A keyword counts as "present" only if it
(or a very close variant, e.g. plural/singular, common abbreviation)
appears somewhere in the résumé profile — record which section it was
found in via "found_in". "exact_match" is true if the wording matches
closely, false if it is only a loose/approximate match.
It is normal and expected for a résumé to share few or even zero keywords
with a JD — this indicates a poor-fit candidate, not an error in the
input. Some inputs you receive will be a deliberate mismatch (e.g. a
résumé for a completely unrelated field). In that case, correctly return
an empty or near-empty "present" array and a full "missing" array, with a
low keyword_match_score. Never respond by claiming no résumé was
provided, asking for clarification, or refusing to continue — always
return the JSON schema below, no matter how mismatched the two profiles
are.

CONSTRAINTS:
- "why_it_matters" must be 25 words or fewer, must only explain why the
  missing keyword matters for this role, and must never contain
  rewritten résumé text or a suggested bullet.
- "category" must be one of: language, framework, tool, concept,
  soft_skill, buzzword.
- "importance" must be "required" if the keyword came from
  required_skills, "preferred" if it came from preferred_skills or
  tools_technologies.
- Compute keyword_match_score as: 100 × (number of required_skills found
  in the résumé) / max(1, total number of required_skills). Round to the
  nearest whole number.
- Arrays may be empty; this is a valid and expected result, not an error.

OUTPUT:
Return a single JSON object with exactly this shape:
{
  "present": [{"keyword": "string", "category": "language|framework|tool|concept|soft_skill|buzzword",
               "found_in": "summary|projects|experience|education|skills", "exact_match": true}],
  "missing": [{"keyword": "string", "category": "language|framework|tool|concept|soft_skill|buzzword",
               "importance": "required|preferred",
               "suggested_section": "skills|projects|experience|summary",
               "why_it_matters": "string (25 words max)"}],
  "keyword_match_score": 0
}

Output ONLY a valid JSON object matching the schema above. No prose. No
markdown fences. No commentary. Never rewrite or generate résumé content.
"""


# Purpose: score each résumé bullet against the Action → Technology → Impact rubric.
# Input to ask_json(): system=BULLET_QUALITY_PROMPT, user="RÉSUMÉ PROFILE:\n{json}"
# Expected output schema:
# {
#   "bullets": [{"source": "projects|experience", "parent_title": "string",
#                "bullet_text": "string (verbatim)", "has_action_verb": true,
#                "has_specific_technology": true, "has_measurable_impact": false,
#                "level": "L1_OK|L2_BETTER|L3_BEST",
#                "what_is_missing": "string (20 words max — diagnose only)"}],
#   "bullet_quality_avg": 0
# }
# Scoring formula: round(100 × sum(level_score) / (3 × count)) where L1=1, L2=2, L3=3
# IMPORTANT: embed the Action→Technology→Impact rubric verbatim inside this prompt,
# including the L1/L2/L3 reference level examples. This is a well-known, general
# résumé-writing framework — no external reference document needed.
BULLET_QUALITY_PROMPT = """
INSTRUCTION:
You are given a structured résumé profile (JSON). Score every bullet
point in every project and every job in "experience" against the
Action → Technology → Impact rubric below. Evaluate each bullet
independently.

CONTEXT — the Action → Technology → Impact (ATI) rubric:
A strong résumé bullet contains three ingredients:
1. Action — a concrete action verb describing what the candidate did
   (e.g. "built", "designed", "automated", "led"), not a passive
   description (e.g. "responsible for").
2. Technology — the specific tool, language, framework, or system used
   (e.g. "Python", "Kafka", "React"), not a vague reference (e.g. "modern
   technologies", "various tools").
3. Impact — a measurable or concrete outcome (a number, percentage, time
   saved, scale, or clearly stated result), not a vague claim (e.g.
   "improved performance" with no number).

Levels:
- L1_OK: has an action verb, but no specific technology named and no
  measurable impact. Example: "Led a team to improve the onboarding
  process."
- L2_BETTER: has an action verb AND names a specific technology/tool, but
  no measurable impact. Example: "Built a data pipeline using Apache
  Kafka and Python to process user events."
- L3_BEST: has an action verb, a specific technology/tool, AND a
  measurable impact. Example: "Built a data pipeline using Apache Kafka
  and Python, reducing event-processing latency by 40% for 2M daily
  events."

CONSTRAINTS:
- "bullet_text" must be copied verbatim from the résumé profile — do not
  alter it.
- "what_is_missing" must be 20 words or fewer, must diagnose only which
  ingredient (technology and/or impact) is absent, and must never
  contain a rewritten or improved version of the bullet.
- "has_action_verb", "has_specific_technology", and
  "has_measurable_impact" are independent booleans; "level" is derived
  from how many of them are true, per the rubric above.
- Include every bullet from every project and every experience entry —
  do not skip any or summarize across bullets.
- Compute bullet_quality_avg as: round(100 × sum(level_score) /
  (3 × count)), where L1_OK=1, L2_BETTER=2, L3_BEST=3, and count is the
  total number of bullets scored. If there are no bullets at all, use 0.

OUTPUT:
Return a single JSON object with exactly this shape:
{
  "bullets": [{"source": "projects|experience", "parent_title": "string",
               "bullet_text": "string (verbatim)", "has_action_verb": true,
               "has_specific_technology": true, "has_measurable_impact": false,
               "level": "L1_OK|L2_BETTER|L3_BEST",
               "what_is_missing": "string (20 words max)"}],
  "bullet_quality_avg": 0
}

Scoring formula: round(100 × sum(level_score) / (3 × count)) where L1=1, L2=2, L3=3
IMPORTANT: embed the Action→Technology→Impact rubric verbatim inside this prompt,
including the L1/L2/L3 reference level examples. This is a well-known, general
résumé-writing framework — no external reference document needed.

Output ONLY a valid JSON object matching the schema above. No prose. No
markdown fences. No commentary. Never rewrite or generate résumé content.
"""


# Purpose: detect résumé terminology that is a likely semantic match for JD
#          terminology but would not literally keyword-match an ATS scan.
# Input to ask_json():
#   system=JARGON_AUDIT_PROMPT
#   user="RÉSUMÉ PROFILE:\n{json}\n\nJD PROFILE:\n{json}"
# Expected output schema:
# {
#   "flags": [{"bullet_text": "string (verbatim)", "term_used": "string",
#              "suggested_translation": "string", "severity": "low|medium|high"}],
#   "jargon_score": 0
# }
# No static table: the model compares résumé text against JD text dynamically —
# a real ATS/recruiter tool does semantic matching, not a hand-maintained dictionary.
# Severity rules: high if the JD uses no equivalent language at all; medium if
# partial overlap; low if the JD already uses matching or adjacent terminology.
# Scoring formula: max(0, 100 - 10*high_count - 5*medium_count - 2*low_count)
JARGON_AUDIT_PROMPT = """
INSTRUCTION:
You are given a structured résumé profile (JSON) and a structured JD
profile (JSON). Find résumé terms (in summary, skills, or bullets) that
likely mean the same thing as something the JD is asking for, but are
worded differently enough that a literal keyword-matching ATS scan would
not connect them. Flag each one.

CONTEXT:
There is no fixed dictionary of equivalent terms to consult — compare the
actual résumé wording against the actual JD wording for this specific
pair of inputs, dynamically, the way a human recruiter reading both
documents side by side would notice "oh, 'REST API integration' and
'built backend services' are basically the same skill, just phrased
differently." Only flag terms where there is a real, plausible semantic
overlap — do not flag unrelated terms just because they sound technical.
Severity rules:
- "high": the JD uses no equivalent language anywhere for this concept —
  a reviewer would likely miss the connection entirely.
- "medium": the JD has partial/loose overlap — an alert reader might
  connect them, but it is not obvious.
- "low": the JD already uses matching or closely adjacent terminology —
  the risk of being missed is minimal.

CONSTRAINTS:
- "bullet_text" must be copied verbatim from the résumé profile.
- "suggested_translation" must be a short phrase naming which JD-style
  term the résumé's term corresponds to — it must never be a rewritten
  bullet, sentence, or résumé content; it is a diagnostic label only
  (e.g. "JD calls this 'CI/CD pipeline management'").
- Compute jargon_score as: max(0, 100 - 10 × count(high) -
  5 × count(medium) - 2 × count(low)).
- If there is no plausible overlap between the two documents at all,
  return an empty "flags" array and a jargon_score of 100 — this is a
  valid result, not an error.

OUTPUT:
Return a single JSON object with exactly this shape:
{
  "flags": [{"bullet_text": "string (verbatim)", "term_used": "string",
             "suggested_translation": "string", "severity": "low|medium|high"}],
  "jargon_score": 0
}

Output ONLY a valid JSON object matching the schema above. No prose. No
markdown fences. No commentary. Never rewrite or generate résumé content.
"""


# Purpose: audit general ATS-parseability formatting.
# Input to ask_json(): system=STRUCTURE_AUDIT_PROMPT, user="RÉSUMÉ TEXT:\n\n{text}"
# Expected output schema:
# {
#   "page_count_estimate": 1,
#   "single_column_likely": true,
#   "section_headings_present": ["string"],
#   "section_headings_missing": ["string"],
#   "reverse_chronological_likely": true,
#   "contact_info_at_top": true,
#   "length_appropriate": true,
#   "no_images_or_graphics": true,
#   "ats_red_flags": [{"issue": "string", "evidence": "string"}],
#   "structure_score": 0
# }
# IMPORTANT: embed general ATS-parseability rules verbatim inside this prompt:
# single-column layout, standard section headers, reverse-chronological order,
# appropriate length, contact info placement, no images/graphics. These are
# well-known conventions — no external reference document needed.
STRUCTURE_AUDIT_PROMPT = """
INSTRUCTION:
You are given the plain extracted text of a résumé (already run through a
PDF text extractor). Judge how well the underlying résumé is likely to
parse cleanly through an Applicant Tracking System (ATS), based on
patterns visible in the extracted text.

CONTEXT — general ATS-parseability conventions:
- Single-column layout: multi-column résumés often produce scrambled,
  out-of-order text when extracted; look for jumbled reading order,
  interleaved unrelated lines, or fragments that do not read as coherent
  sentences — these suggest a multi-column source.
- Standard section headings: ATS systems and recruiters expect headings
  like "Summary", "Experience"/"Work Experience", "Education", "Skills",
  "Projects". Non-standard or missing headings (e.g. "My Journey" instead
  of "Experience") reduce parseability.
- Reverse-chronological order: the most recent role/degree should be
  listed first within each section.
- Appropriate length: roughly one page for early-career candidates, up to
  two pages for senior candidates; a wall of text with no clear
  structure, or extremely sparse content, is a red flag.
- Contact info placement: name and contact details (email/phone) should
  appear at the very top of the document, not buried mid-document or
  absent.
- No images/graphics: since you only receive extracted text, infer this
  from artifacts such as unusual character sequences, large gaps, or
  garbled fragments where a graphic/icon/table likely sat — the absence
  of such artifacts suggests a clean, image-free layout.

CONSTRAINTS:
- Base every judgment only on patterns actually visible in the given
  text — do not assume a layout you cannot infer from the text.
- "ats_red_flags" entries must cite the actual "evidence" (a short
  quoted or paraphrased snippet) that led you to flag the issue.
- Do not suggest rewrites or alternate phrasing for any content — this is
  a structural audit only.
- Compute structure_score as a 0-100 integer reflecting overall
  parseability: start at 100 and deduct proportionally for each red flag
  found (small deductions for minor issues like a slightly non-standard
  heading, larger deductions for major issues like an undetectable
  section structure or a suspected multi-column layout).

OUTPUT:
Return a single JSON object with exactly this shape:
{
  "page_count_estimate": 1,
  "single_column_likely": true,
  "section_headings_present": ["string"],
  "section_headings_missing": ["string"],
  "reverse_chronological_likely": true,
  "contact_info_at_top": true,
  "length_appropriate": true,
  "no_images_or_graphics": true,
  "ats_red_flags": [{"issue": "string", "evidence": "string"}],
  "structure_score": 0
}

Output ONLY a valid JSON object matching the schema above. No prose. No
markdown fences. No commentary. Never rewrite or generate résumé content.
"""


# Purpose: assess how well the candidate's stated education/experience background
# plausibly aligns with what this role is asking for — using only data already
# extracted into resume_profile and jd_profile (no external degree code needed).
# Input to ask_json():
#   system=BACKGROUND_FIT_PROMPT
#   user="RÉSUMÉ PROFILE:\n{json}\n\nJD PROFILE:\n{json}"
# Expected output schema:
# {
#   "candidate_background_summary": "string (1–2 sentences)",
#   "role_requirements_summary": "string (1–2 sentences)",
#   "alignment_commentary": "string (2–3 sentences — diagnostic only)",
#   "background_fit_score": 0
# }
BACKGROUND_FIT_PROMPT = """
INSTRUCTION:
You are given a structured résumé profile (JSON) and a structured JD
profile (JSON). Using only the "education" and "experience" fields of the
résumé profile, and the "experience_level", "responsibilities", and
"required_skills" fields of the JD profile, judge how plausible the
candidate's overall academic and professional background is as a fit for
this specific role.

CONTEXT:
This is a holistic judgment about background fit — not a keyword count.
Consider things like: does the candidate's degree/field of study relate
to the domain of the role; does the type and amount of prior experience
roughly match the JD's stated experience_level (e.g. entry-level vs
senior); is there a plausible narrative connecting what they have
studied/done to what this job asks for. There is no external table of
equivalent degree codes to consult — reason about it directly from the
profile text, the same way a hiring manager skimming both documents
would.

CONSTRAINTS:
- Use only resume_profile's education/experience fields and jd_profile's
  requirement fields — do not use outside knowledge of specific companies
  or degree-accreditation systems.
- "alignment_commentary" must be 2-3 sentences, diagnostic only — it must
  never contain rewritten résumé content or a suggested bullet/summary
  rewrite.
- "candidate_background_summary" and "role_requirements_summary" must
  each be 1-2 sentences.
- background_fit_score is a 0-100 integer reflecting overall plausibility
  of fit; a strong, clearly relevant background should score high, an
  unrelated background should score low.

OUTPUT:
Return a single JSON object with exactly this shape:
{
  "candidate_background_summary": "string (1-2 sentences)",
  "role_requirements_summary": "string (1-2 sentences)",
  "alignment_commentary": "string (2-3 sentences)",
  "background_fit_score": 0
}

Output ONLY a valid JSON object matching the schema above. No prose. No
markdown fences. No commentary. Never rewrite or generate résumé content.
"""


# ---------------------------------------------------------------------------
# Synthesis prompt
# ---------------------------------------------------------------------------

# Purpose: produce a 3-bullet plain Markdown executive summary from the full report.
# Input to ask_text(): system=OVERALL_SUMMARY_PROMPT, user="ANALYSIS REPORT:\n{json}"
# Returns: plain Markdown string (not JSON).
# NOTE: this prompt does NOT need the JSON output constraint line.
#       It also does NOT need a JSON schema — ask_text() is used, not ask_json().
# The summary must be diagnostic only — no rewrites, no generated résumé content.
OVERALL_SUMMARY_PROMPT = """
INSTRUCTION:
You are given a full analysis report (JSON) produced by a résumé-vs-job-
description scoring pipeline. Write a 3-bullet executive summary in plain
Markdown for the candidate.

CONTEXT:
The report contains an overall_score, whether the résumé
passes_ats_threshold, and sub-analyses for keyword_match, bullets,
jargon, structure, and background_fit. The audience is the candidate
themselves, who wants a quick, honest read of where they stand and what
matters most.

CONSTRAINTS:
- Output exactly 3 bullet points, each starting with "- ", and nothing
  else — no heading, no intro sentence, no closing sentence, no code
  fences.
- Each bullet must be diagnostic and specific, referencing a concrete
  finding from the report (e.g. a missing keyword, a low-scoring bullet
  pattern, a structural issue) — never invent a finding that is not
  present in the report.
- Never write a rewritten résumé bullet, rewritten summary, or any
  generated résumé content — only describe what the report found.
- Keep each bullet to one sentence.
"""
