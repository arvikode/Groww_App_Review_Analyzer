# Groww Review Insights Analyser

Automated weekly analysis of Groww app reviews from Google Play Store. Classifies reviews into 5 fixed themes using Groq AI, generates a one-page pulse report (≤250 words), and sends it straight to your inbox.

**Full setup:** See [`n8n_configs/SETUP_GUIDE.md`](n8n_configs/SETUP_GUIDE.md)  
**Architecture deep-dive:** See [`ARCHITECTURE.md`](ARCHITECTURE.md)

---

## How to Re-run for a New Week

Each weekly run takes about 2 minutes. Choose one of two modes:

### Option A — Quick demo (sample data, no CSV needed)

```
1. Open n8n → Groww Review Analyzer workflow
2. Click "Upload CSV (Manual Trigger)" → "Test step"
3. Open the form URL in your browser
4. Select "Use sample Groww data" from the dropdown
5. Click Submit
6. Wait ~90 seconds → check your inbox
```

### Option B — Fresh data from Play Store (recommended for real runs)

```
1. Run: python scripts/scrape_reviews.py
2. Run: python scripts/redact_pii.py
3. Open n8n → Groww Review Analyzer workflow
4. Click "Upload CSV (Manual Trigger)" → "Test step"
5. Open the form URL in your browser
6. Select "Upload custom CSV" → upload data/reviews_clean.csv
7. Click Submit
8. Wait ~90 seconds → check your inbox
```

> **What happens under the hood:** The workflow filters the last 8 weeks of reviews, samples up to 100, classifies each into a theme via Groq AI, aggregates the counts, and emails you a formatted report.

### Troubleshooting a failed run

| Problem | Fix |
|---------|-----|
| Groq 429 rate limit error | Increase the Wait node from 5s → 8s, then re-run |
| "No reviews found in last 8 weeks" | Check CSV dates are `YYYY-MM-DD` format; try sample data mode |
| Gmail auth error | Go to Settings → Credentials → reconnect Gmail OAuth |
| Word count >250 | In the **Aggregate & Generate Note** node, shorten the `blurb` strings in the `THEMES` object |
| All reviews same theme | Verify Groq API key starts with `Bearer gsk_...` in the Classify node headers |

---

## Theme Legend

Reviews are classified into exactly one of these 5 fixed themes. The top 3 by volume appear in each weekly report.

| # | Theme | Emoji | Typical keywords | Example review |
|---|-------|-------|-----------------|----------------|
| 1 | **Onboarding & UX Confusion** | 🧭 | login, signup, confusing, navigate, find, UI | *"Login process is confusing AF. Took me 20 mins to get in."* |
| 2 | **Performance & Technical Bugs** | 🐛 | crash, slow, loading, error, freeze, bug, not working | *"App crashes every time I try to check my portfolio."* |
| 3 | **Missing Features & Requests** | 💡 | wish, need, add, missing, feature, should have | *"Need an option to track SIP investments better."* |
| 4 | **Trust & Security Concerns** | 🔒 | money, account, security, safe, verification, kyc, blocked | *"KYC verification stuck for 3 days. Support not responding."* |
| 5 | **Support & Communication** | 📞 | support, customer service, help, response, contact, resolve | *"Support team ghosted me. No reply for a week."* |

**Classification method:** Groq AI (primary) → keyword scoring (fallback) → Theme 2 default if both fail.  
**Temperature:** 0.1 — low, for consistent and reproducible classification.

---

## Sample Email Format

This is what lands in your inbox after each successful run:

```
Subject: 📊 Groww Review Pulse: Week of 2026-02-18

──────────────────────────────────────────────────────────
📊 Groww Review Pulse — Week of 2026-02-18
Reviews Analyzed: 67 | Period: 2025-12-18 to 2026-02-15 | Source: Google Play Store
──────────────────────────────────────────────────────────

🎯 Top 3 Themes — with Quotes & Actions

┌─────────────────────────────────────────────────────────┐
│ 🐛 #1  Performance & Technical Bugs                     │
│ 45% of reviews • 30 out of 67                           │
│ Crashes and slowness are killing the vibe.              │
│                                                         │
│ "App crashes every time I try to check my portfolio."   │
│ ⭐ 1-star review • 2026-02-12                           │
│                                                         │
│ ⚡ ACTION IDEA                                          │
│ Speed boost urgently needed — 45% are watching          │
│ loading spinners like it's dial-up TV.                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🧭 #2  Onboarding & UX Confusion                        │
│ 28% of reviews • 19 out of 67                           │
│ Login flow playing hide-and-seek. Users need breadcrumbs│
│                                                         │
│ "Login process is confusing AF. Took me 20 mins."       │
│ ⭐ 3-star review • 2026-02-05                           │
│                                                         │
│ ⚡ ACTION IDEA                                          │
│ Simplify the login flow — users shouldn't need          │
│ a treasure map to get in!                               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🔒 #3  Trust & Security Concerns                        │
│ 18% of reviews • 12 out of 67                           │
│ KYC stuck in purgatory. Money anxiety spiking.          │
│                                                         │
│ "KYC verification stuck for 3 days. No response."       │
│ ⭐ 2-star review • 2026-02-09                           │
│                                                         │
│ ⚡ ACTION IDEA                                          │
│ Verification hiccups are spooking users —               │
│ smooth out the KYC bumps.                               │
└─────────────────────────────────────────────────────────┘

──────────────────────────────────────────────────────────
Laugh. Learn. Iterate. 🚀
Word count: 243 / 250
──────────────────────────────────────────────────────────
```

**Email characteristics:**
- Sent as an HTML email with styled cards per theme
- Subject always includes the week date for easy archiving
- Word count shown in footer — target is ≤250 words
- Tone is constructive and lightly humorous by design
- Zero PII: no usernames, only anonymised star ratings and dates

---

## File Structure

```
App-Review-Insights-Analyser/
├── README.md                        ← You are here
├── ARCHITECTURE.md                  ← Full system design & data flow
├── requirements.txt                 ← Python dependencies
├── .gitignore                       ← Keeps CSV data out of git
│
├── scripts/
│   ├── scrape_reviews.py            ← Fetches reviews from Play Store
│   └── redact_pii.py                ← Strips usernames, emails, phones
│
├── data/                            ← Gitignored (CSV files live here)
│   ├── reviews_raw.csv              ← Output of scrape_reviews.py
│   └── reviews_clean.csv            ← Output of redact_pii.py (upload this to n8n)
│
├── n8n_configs/
│   ├── SETUP_GUIDE.md               ← One-time n8n + Groq + Gmail setup
│   └── workflow.json                ← Import this into n8n
│
└── outputs/                         ← Archive of past weekly reports
```
