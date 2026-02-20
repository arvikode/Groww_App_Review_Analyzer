# n8n Workflow Setup Guide
## Groww Review Insights Analyzer

**Time Required:** ~20 minutes (one-time setup)  
**After setup, each weekly run takes:** ~2 minutes

---

## Prerequisites Checklist

Before starting, have these ready:

- [ ] n8n cloud account (free) — https://app.n8n.cloud
- [ ] Groq API key (free) — https://console.groq.com
- [ ] Gmail account for sending reports

---

## Step 1: Import the Workflow

1. Log in to https://app.n8n.cloud
2. Click **"Add workflow"** (top right)
3. In the new empty workflow, click the **"..."** menu (top right of canvas)
4. Select **"Import from file"**
5. Upload `n8n_configs/workflow.json` from this project
6. The workflow loads with 12 nodes across two branches
7. Click **"Save"** (top right) — name it `Groww Review Analyzer`

You should see this node layout left to right:

```
                     ┌─→ [Sample Data] ─┐
[Form] → [Route by Mode]               [Merge] → [Filter & Sample] → [Keyword Pre-classify]
                     └─→ [Parse CSV] ───┘
                                           → [Groq: Classify Theme] → [Extract Theme Number]
                                           → [Wait 5s] → [Aggregate & Generate Note] → [Send Email]
```

### How the two run modes work

The first node is a **Form Trigger** — it opens a small hosted web form in your browser. When you submit the form, n8n routes to one of two paths:

| Mode | What happens |
|------|-------------|
| **Use sample Groww data** | Loads 89 pre-embedded Groww reviews (Nov 2025–Feb 2026) — no file needed |
| **Upload custom CSV** | You upload your own `reviews_clean.csv` and the Parse CSV node reads it |

Both paths merge before the analysis nodes, so the rest of the workflow is identical.

---

## Step 2: Add Your Groq API Key

### Get Your Free API Key
1. Go to https://console.groq.com
2. Sign up for a free account
3. Click **"API Keys"** in the left sidebar
4. Click **"Create API Key"**
5. Copy the key — looks like `gsk_...`

### Set the Key in the Workflow
1. Back in n8n, click the **"Groq: Classify Theme"** node
2. In the right panel, scroll to the **Headers** section
3. Find the `Authorization` header value — it currently shows `Bearer PASTE_YOUR_GROQ_API_KEY_HERE`
4. Replace `PASTE_YOUR_GROQ_API_KEY_HERE` with your actual key (keep the `Bearer ` prefix)
5. Click outside to save — the node stays grey (HTTP nodes don't turn green until executed)

> **Free tier limits:** Groq allows ~6,000 tokens/minute on the free plan. The 5-second Wait node keeps usage within this limit for up to 100 reviews.

---

## Step 3: Connect Your Gmail

1. Click the **"Send Email"** node
2. In the right panel, find **Credential for Gmail OAuth2**
3. Click **"Create new credential"**
4. A browser popup opens — sign in with your Gmail account
5. Grant the requested permissions
6. The credential saves automatically

### Set Your Email Address
1. Still in the **"Send Email"** node
2. Find the **"To"** field — it shows `ENTER_YOUR_EMAIL_HERE@gmail.com`
3. Replace it with your actual email address
   - Single: `yourname@gmail.com`
   - Multiple: `email1@gmail.com, email2@gmail.com`
4. Click outside to save

---

## Step 4: Test with Sample Data (No CSV Needed)

This is the fastest way to confirm everything works end-to-end.

1. In n8n, click the **"Upload CSV (Manual Trigger)"** node to select it
2. Click **"Test step"** in the right panel
3. n8n shows a **form URL** — copy it and open it in a new browser tab
4. The form shows two fields:
   - **Run Mode** dropdown — select **"Use sample Groww data"**
   - **data** file upload — leave empty (not required for sample mode)
5. Click **"Submit"**
6. Switch back to n8n — the workflow continues automatically
7. Watch nodes turn green one by one (~90 seconds for 89 reviews)

### What to check
- **Route by Mode** — should route to the Sample Data branch (true/output 0)
- **Sample Data node** — output should show 89 items
- **Filter & Sample node** — output shows items from last 8 weeks
- **Groq: Classify Theme node** — each item has a `choices` field with a digit 1–5
- **Extract Theme node** — each item has `theme: 1` through `theme: 5`
- **Aggregate & Generate node** — output has `htmlBody`, `wordCount`, `top3Themes`
- **Send Email node** — should show success; check your inbox

---

## Step 5: Run with Your Own CSV

Once the sample test passes, you can upload your own review data:

1. Prepare your CSV with columns: `rating`, `title`, `text`, `date`
   - Dates must be `YYYY-MM-DD`, `M/D/YY`, or `M/D/YYYY` format
   - Reviews must fall within the last 8 weeks
2. Click **"Upload CSV (Manual Trigger)"** → **"Test step"**
3. Open the form URL in your browser
4. Select **"Upload custom CSV"** in the Run Mode dropdown
5. Click the file upload button and select your CSV
6. Click **"Submit"**
7. Wait ~90 seconds for all nodes to complete
8. Check your inbox for the weekly report email

---

## Step 6: Review the Output

Open the email in your inbox. It should look like:

```
Subject: 📊 Groww Review Pulse: Week of 2026-02-18

[Green header card]
📊 Groww Review Pulse — Week of 2026-02-18

Reviews Analyzed: 67 | Period: 2025-12-18 to 2026-02-15 | Source: Google Play Store

🎯 Top 3 Themes — with Quotes & Actions

┌────────────────────────────────────────────────────────┐
│ 🐛 #1 Performance & Technical Bugs                     │
│ 45% of reviews • 30 out of 67                          │
│ "Crashes and slowness are killing the vibe..."         │
│                                                        │
│ "App crashes every time I try to check my portfolio."  │
│ ⭐ 1-star review • 2026-02-12                          │
│                                                        │
│ ⚡ ACTION IDEA                                         │
│ Speed boost urgently needed — 45% are watching         │
│ loading spinners like it's dial-up TV.                 │
└────────────────────────────────────────────────────────┘

[similar cards for themes #2 and #3]

Laugh. Learn. Iterate. 🚀
```

### Verify Word Count
- The email footer shows the word count
- Target is ≤250 words
- If over, shorten the `blurb` values in the `THEMES` object inside the **Aggregate & Generate Note** node

---

## Troubleshooting

### Problem: Groq node shows red / 429 "rate limit" error
**Cause:** Too many token requests per minute  
**Fix:**
1. Click the **"Wait 5s (Rate Limit)"** node
2. Change the wait time from 5 to **8 seconds**
3. Save and re-run

### Problem: "No reviews found in the last 8 weeks"
**Cause:** CSV dates are outside the 8-week window, or wrong date format  
**Fix:**
1. Open your CSV and check the `date` column
2. Dates must be `YYYY-MM-DD`, `M/D/YY`, or `M/D/YYYY` format
3. Switch to **"Use sample Groww data"** mode to verify the rest works

### Problem: Gmail node shows red / auth error
**Cause:** OAuth token expired  
**Fix:**
1. Go to **Settings → Credentials**
2. Find your Gmail credential
3. Click **"Reconnect"** and re-authenticate

### Problem: Sample Data branch not triggering
**Cause:** The IF node condition may need checking  
**Fix:**
1. Click the **"Route by Mode"** node
2. Verify the left value expression is `={{ $json['Run Mode'] }}`
3. Verify the right value is exactly `Use sample Groww data` (no extra spaces)
4. The true branch (output 0) should connect to Sample Data; false (output 1) to Parse CSV

### Problem: Word count is >250
**Fix:**
1. Click the **"Aggregate & Generate Note"** node
2. Find the `THEMES` object near the top of the code (around line 5)
3. Shorten the `blurb` strings — keep them to 8–10 words each
4. Click **"Save"** and re-run

### Problem: All reviews classified as the same theme
**Cause:** Groq not responding, keyword fallback running for all  
**Fix:**
1. Check the **Groq: Classify Theme** node output for error messages
2. Verify your API key in the `Authorization` header starts with `Bearer gsk_...`
3. Test the Groq API at https://console.groq.com/playground

---

## Weekly Run Checklist (After Setup)

Every week, do these steps (2–5 minutes total):

### Option A — Use sample data (instant demo)
```
[ ] 1. Open n8n → Groww Review Analyzer workflow
[ ] 2. Click "Upload CSV (Manual Trigger)" → "Test step"
[ ] 3. Open the form URL in browser
[ ] 4. Select "Use sample Groww data" → Submit
[ ] 5. Wait ~90 seconds → check inbox
```

### Option B — Use fresh review data
```
[ ] 1. Run: python scripts/scrape_reviews.py
[ ] 2. Run: python scripts/redact_pii.py
[ ] 3. Open n8n → Groww Review Analyzer workflow
[ ] 4. Click "Upload CSV (Manual Trigger)" → "Test step"
[ ] 5. Open the form URL in browser
[ ] 6. Select "Upload custom CSV" → upload reviews_clean.csv → Submit
[ ] 7. Wait ~90 seconds → check inbox
```

---

## Exporting the Workflow (for Backup)

After confirming the workflow works:

1. In n8n, click the workflow name (top left)
2. Click **"..."** menu → **"Download"**
3. Save as `n8n_configs/workflow_backup.json`

---

## Node Summary Reference

| # | Node Name | Purpose | Requires Setup? |
|---|-----------|---------|-----------------|
| 1 | Upload CSV (Manual Trigger) | Form with run mode dropdown + optional file upload | No |
| 2 | Route by Mode | IF node — routes sample vs upload branch | No |
| 3 | Sample Data (Groww Reviews) | 89 embedded reviews — no file needed | No |
| 4 | Parse CSV | Reads the uploaded CSV file into JSON rows | No |
| 5 | Merge | Combines both branches into one stream | No |
| 6 | Filter & Sample (max 100) | Last 8 weeks, max 100 rows | No |
| 7 | Keyword Pre-classify | Baseline theme via keywords | No |
| 8 | Groq: Classify Theme | AI classification (1–5) | **Yes — API key** |
| 9 | Extract Theme Number | Parse Groq response + fallback | No |
| 10 | Wait 5s (Rate Limit) | Prevent API rate limit errors | No |
| 11 | Aggregate & Generate Note | Count themes, build HTML report | No |
| 12 | Send Email | Sends HTML email to inbox | **Yes — Gmail OAuth** |

**Only 2 nodes need credentials: Groq (Step 2) and Gmail (Step 3)**

---

## Architecture Reference

See `ARCHITECTURE.md` in the project root for full system design, data flow diagrams, and theme classification details.
