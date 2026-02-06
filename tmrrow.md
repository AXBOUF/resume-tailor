Got you. Keep it **tight, concrete, and non-vibey**. This is a *one-day execution plan*, not a dream roadmap.

Here’s a clean **`TODO.md` for tomorrow** 👇

---

````md
# TODO – Resume Tailoring System (Day Plan)

## 1. Fix the scraping abstraction (HIGH PRIORITY)
- [ ] Stop scraping LinkedIn search result pages
- [ ] Extract only individual job posting URLs from search results
- [ ] Fetch ONE job posting page at a time
- [ ] Save raw HTML snapshots for debugging

Outcome:
> One JSON per job posting, not a feed dump

---

## 2. Build rule-based job description parser (NO LLM)
- [ ] Identify DOM selectors for:
  - Job title
  - Company
  - Location
  - Employment type
- [ ] Split job content into sections:
  - Responsibilities
  - Required skills
  - Nice-to-have skills
- [ ] Strip auth / UI / footer noise
- [ ] Output structured JD JSON

Deliverable:
```json
job_description.json
````

---

## 3. Define resume JSON schema (LOCK THIS)

* [ ] Decide immutable vs mutable fields
* [ ] Parse LaTeX resume into JSON:

  * Sections
  * Bullet points
  * Metrics
* [ ] Preserve original LaTeX commands

Deliverable:

```json
resume_base.json
```

---

## 4. Create RAG knowledge base (minimal v1)

* [ ] Write `resume_rules.md`

  * ATS-safe wording
  * Bullet structure
  * Quantification rules
* [ ] Write `data_engineer_skills.md`

  * Core skills
  * Common tooling
  * Keyword variations
* [ ] Store as retrievable chunks

Goal:

> LLM never guesses resume best practices

---

## 5. LLM Step 1 – Job understanding ONLY

* [ ] Feed structured JD JSON to LLM
* [ ] Ask for:

  * Ranked required skills
  * Seniority signals
  * Key keywords
* [ ] Force JSON output

Deliverable:

```json
job_signal_analysis.json
```

---

## 6. Wire the pipeline (no generation yet)

* [ ] resume JSON + job JSON + job analysis flow end-to-end
* [ ] Log every intermediate output
* [ ] Reject output if schema mismatch

---

## 7. Write notes (important)

* [ ] What broke today?
* [ ] What assumptions were wrong?
* [ ] What should NOT be done with LLMs?

These notes = interview gold.

```

---

### How to approach the day (mentally)
- If something feels “clever”, you’re probably doing too much
- If it feels boring and mechanical, you’re on the right path
- Do **not** generate a resume tomorrow — earn the right first

This is real engineering progress, not demo progress.

Sleep after this. You’ll feel *clean* instead of fried.
```
