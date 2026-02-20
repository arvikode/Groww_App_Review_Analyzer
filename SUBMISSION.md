# 📊 App Review Insights Analyser

**Product:** Groww (Indian Investment & Stock Trading App)  
**Platform:** Google Play Store  
**Review Period:** Dec 2025 – Feb 2026 (8–12 weeks)

---

### 📊 Groww Review Pulse Sample — Week of 2026-02-18

**Reviews Analysed:** 67 &nbsp;|&nbsp; **Period:** 2025-12-18 → 2026-02-15 &nbsp;|&nbsp; **Source:** Google Play Store

---

#### 🎯 Top 3 Themes

---

**🐛 #1 · Performance & Technical Bugs** — 45% of reviews (30 / 67)

> *"App crashes every time I try to check my portfolio."*
> ⭐ 1-star · 2026-02-12

Crashes and slow loading are the single loudest signal this week.

**⚡ Action Idea:** Launch a crash-free sprint — instrument the top three crash traces and ship a stability-focused patch before the next release cycle.

---

**🧭 #2 · Onboarding & UX Confusion** — 28% of reviews (19 / 67)

> *"Login process is confusing AF. Took me 20 mins to get in."*
> ⭐ 3-star · 2026-02-05

New users are hitting friction before they place their first trade.

**⚡ Action Idea:** Redesign the login flow with a step-indicator and reduce required taps by 40% — measure drop-off at each authentication step.

---

**🔒 #3 · Trust & Security Concerns** — 18% of reviews (12 / 67)

> *"KYC verification stuck for 3 days. Support not responding."*
> ⭐ 2-star · 2026-02-09

Verification delays are eroding confidence in a money-handling app.

**⚡ Action Idea:** Add a KYC status-tracker with real-time updates and a 24-hour SLA commitment — turn a pain point into a trust signal.

---

*Laugh. Learn. Iterate. 🚀 &nbsp;|&nbsp; Word count: 172 / 250*

---

## 2️⃣ Email
Screenshot - https://github.com/arvikode/Groww_App_Review_Analyzer/blob/main/Artifacts/Screenshot%202026-02-20%20at%2011.07.58%E2%80%AFPM.png

PDF - https://github.com/arvikode/Groww_App_Review_Analyzer/blob/main/Artifacts/Nextleap%20LIP3%20Email_f0d9d825-4bde-4abe-8cda-db38742b3094.pdf


> **How the email is sent:** The n8n workflow's **Send Email** node delivers this as a styled HTML email via Gmail OAuth2. The subject line auto-includes the current week date for easy inbox archiving.

---

## 3️⃣ Reviews CSV (Redacted Sample — 20 rows)

> No usernames, emails, or account IDs. Only: rating, title, text, date.

https://github.com/arvikode/Groww_App_Review_Analyzer/blob/main/n8n_configs/reviews_clean_20.csv

**Redaction applied by `scripts/redact_pii.py`:** strips any usernames, emails, phone numbers, and reviewer IDs before the CSV enters the n8n pipeline.

---

## 4️⃣ How to Re-run & Theme Legend

### How to Re-run for a New Week

**One-time setup (~20 min):** Import `n8n_configs/workflow.json` into [n8n Cloud](https://app.n8n.cloud), add your Groq API key, and connect Gmail OAuth2.

**Each weekly run (~2 min):**

**Option A — Quick demo (no CSV needed)**
```
1. Open n8n → Groww Review Analyzer workflow
2. Click "Upload CSV (Manual Trigger)" → "Test step"
3. Open the form URL in your browser
4. Select "Use sample Groww data" → Submit
5. Wait ~90 seconds → check your inbox
```

**Option B — Fresh Play Store data**
```
1. python scripts/scrape_reviews.py        # fetches latest reviews
2. python scripts/redact_pii.py            # strips PII → reviews_clean.csv
3. Open n8n → Groww Review Analyzer workflow
4. Click "Upload CSV (Manual Trigger)" → "Test step"
5. Open the form URL → select "Upload custom CSV" → upload reviews_clean.csv
6. Submit → wait ~90 seconds → check inbox
```

---

### Theme Legend

Reviews are classified into exactly **one of 5 fixed themes** using Groq AI (primary) → keyword scoring (fallback).

| # | Theme | Emoji | Signal keywords |
|---|-------|-------|-----------------|
| 1 | Onboarding & UX Confusion | 🧭 | login, signup, confusing, navigate, find, UI |
| 2 | Performance & Technical Bugs | 🐛 | crash, slow, loading, error, freeze, bug |
| 3 | Missing Features & Requests | 💡 | wish, need, add, missing, feature, should have |
| 4 | Trust & Security Concerns | 🔒 | money, account, security, kyc, blocked, verification |
| 5 | Support & Communication | 📞 | support, customer service, help, response, resolve |

The **top 3 themes by review volume** appear in each weekly report.

---

## 5️⃣ System Architecture (Summary)

```
Google Play Store
       │
       ▼
scripts/scrape_reviews.py   ←── Fetches last 8–12 weeks of public reviews
       │
       ▼
scripts/redact_pii.py        ←── Strips usernames, emails, phone numbers
       │
       ▼  reviews_clean.csv
       │
       ▼
n8n Workflow (12 nodes)
  [Form Trigger]
       │
  [Route by Mode] ──── sample data OR uploaded CSV
       │
  [Filter & Sample]   ←── last 8 weeks, max 100 reviews
       │
  [Keyword Pre-classify]  ←── baseline theme scoring
       │
  [Groq AI: Classify Theme]  ←── LLM assigns theme 1–5
  (llama-3.1-8b-instant · temp 0.1)
       │
  [Wait 5s]  ←── rate-limit guard
       │
  [Aggregate & Generate Note]  ←── counts themes, builds HTML report
       │
  [Send Email via Gmail]  ←── delivers styled HTML to inbox
```

**Tools used:**
- **n8n Cloud** — workflow automation (no-code/low-code)
- **Groq AI** (llama-3.1-8b-instant) — theme classification & summarisation
- **Python 3** — review scraping + PII redaction
- **Gmail OAuth2** — email delivery

---
