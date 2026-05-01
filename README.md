# 🔍 mhance Charity Intelligence Tool

A lightweight web app that helps mhance's sales team identify which UK charities are growing, flat, or shrinking — so they can prioritise outreach to growth-stage prospects in the Microsoft Dynamics 365 nonprofit space.

**Live demo:** https://lynn-charity-intelligence-tool.streamlit.app

Built for the **SilverTree Pioneers technical assessment — Track A**.

---

## What it does

The tool runs in two modes:

### 🔎 Single charity lookup
A salesperson types a charity name or registration number. Within seconds, the tool returns:

- 📊 Last 3 years of **income** and **expenditure** with percentage trend
- 📈 Visual trend chart (income vs. expenditure)
- 🔥 **HOT PROSPECT** flag if income grew >10% year-on-year
- 👥 List of charity trustees
- ⬇️ One-click **CSV export**

### 📋 Batch prospect screening
A salesperson pastes a list of charity names or registration numbers (mixed freely, one per line). The tool resolves each one, pulls financials, calculates trends, and returns a single sortable table — with hot prospects ranked at the top.

- Mix names and registration numbers freely
- Automatic deduplication by registration number
- Sorted by hot-prospect flag, then by income growth
- One-click CSV export of the entire batch

This replaces what used to be a manual workflow: opening individual records on the Charity Commission register and eyeballing PDF accounts. The salesperson now spends seconds per charity instead of 5–10 minutes.

---

## Try these examples

| Charity | Reg # | Why it's interesting |
|---|---|---|
| `Oxfam` | `202918` | Large charity in decline (-15% income) |
| `Cancer Research UK` | `1089464` | Steady income, expenditure outpacing it |
| `4 Cancer Group` | `1090133` | 🔥 Hot prospect: +21.6% income growth |

---

## Stack and decisions

| Layer | Choice | Why |
|---|---|---|
| Backend | **Python** | Best ecosystem for AI/data work, fastest to ship |
| UI | **Streamlit** | Zero-frontend overhead, instantly shareable, polished out of the box |
| Data | **UK Charity Commission Register API (v1.0)** | Official, free, real-time |
| Hosting | **Streamlit Community Cloud** | Free, public URL, GitHub-integrated CI/CD |
| Caching | `@st.cache_data` (1-hour TTL) | Reduces API calls, faster repeat lookups |
| Secrets | Streamlit secrets + env vars | API key stays out of the repo |

### Decisions I made and alternatives I considered

- **Streamlit over Flask/FastAPI.** I prioritised time-to-demo over flexibility. A FastAPI + React build would be more production-grade but would have taken 3-4× longer for the same demo value.
- **Streamlit Cloud over Replit.** Replit was my initial choice, but its UI has been redesigned around an AI Agent flow that made spinning up a blank Python environment surprisingly difficult. After 30 minutes of fighting it, I pivoted to local development + Streamlit Cloud deployment via GitHub. The deployment workflow turned out to be much more production-grade — and a more transferable skill.
- **Hosted over local.** The brief said "hosted is better." Streamlit Cloud was a 5-minute deploy from a GitHub push — no Docker, no server config.
- **Sales-first language ("HOT PROSPECT", "outreach").** Every label is written for the user (mhance's sales team), not for an engineer. The tool isn't a data viewer; it's a prioritisation tool.
- **Trend thresholds (5% flat, 10% hot).** Placeholder business rules. In production, mhance's sales leadership would calibrate these based on conversion data from past deals.
- **Hot prospect placement.** The flag sits **above** the chart, not below it, so the most actionable signal is the first thing a salesperson sees.
- **Batch deduplication by reg number.** When testing batch mode, I noticed users would naturally paste both names and registration numbers — sometimes referencing the same charity twice. Rather than returning duplicate rows, the tool dedupes by resolved registration number. Small fix; the kind of edge case that determines whether a tool is actually used.
- **Developer mode toggle.** Raw API responses are hidden by default but accessible via a sidebar toggle. Good for debugging in production without confusing end users.

---

## Stretch goals from the brief

| Stretch goal | Status |
|---|---|
| Multi-charity at once | ✅ Done (batch screening tab) |
| Hot prospect flag (>10% YoY) | ✅ Done |
| CSV export | ✅ Done (single + batch) |
| Cache API responses | ✅ Done (1-hour TTL) |
| README with decisions | ✅ Done (this file + Reflections.md) |
| Search by sector / geography / income band | ❌ Deliberately skipped — see [Reflections.md](Reflections.md) |

Plus a non-listed addition: **batch deduplication by registration number** to handle real-world user behaviour.

---

## What I would do differently with a full week

I had 3 days of focused build time. With a full week, I would not cut anything from the current MVP — but I would add:

1. **Sector and geography discovery.** "Show me all charities in education with income £500k–£2m, growing >10%." Shifts the tool from "verify a known prospect" to "discover prospects I didn't know existed."
2. **Trustee enrichment.** Cross-reference trustee names against Companies House and LinkedIn to surface decision-makers and warm-introduction paths. This is where most of the actual sales value lives.
3. **CRM integration with Dynamics 365.** mhance is a Dynamics partner — flagged prospects should sync directly into Dynamics rather than being copy-pasted from a CSV.
4. **Scheduled refresh + Slack alerts.** Re-check watched charities monthly; alert when fresh accounts are filed.
5. **A real frontend.** Streamlit is great for prototypes; for production I would rebuild in React + a FastAPI backend, with proper auth and audit logging.

What I would cut: Nothing yet. The MVP is intentionally narrow.

A fuller version of this section, including the assessment-improvement suggestions, lives in [Reflections.md](Reflections.md).

---

## Production-readiness gaps

The current build is a working prototype. To take it to production, the next priorities would be:

- **Rate-limit handling.** Add exponential backoff and a Redis-based shared cache (so multiple salespeople don't all hit the API independently).
- **Auth.** Streamlit Cloud's public URL has no access control. Production would need SSO — probably Microsoft Entra given mhance's Microsoft alignment.
- **Monitoring.** Basic logging exists; production needs Sentry for errors and a usage dashboard.
- **Automated tests.** No test coverage yet. Priority targets: trend calculation, hot-prospect logic, API response parsing.
- **Data freshness indicator.** The cache is 1-hour TTL but the user can't see when data was last fetched. A "last updated" stamp would build trust.

---

## What did not work, and how I worked it out

Three things hit walls during the build.

### 1. Replit
Replit was my initial choice. Its UI has been redesigned around an AI Agent flow that funnels every "new project" attempt through a "describe what you want" prompt. After repeated attempts to get a plain Python environment, I pivoted to **local development in VS Code + deployment to Streamlit Cloud via GitHub**. The deploy turned out to be more production-grade (public URL, auto-redeploy on commit, secrets management) and a more transferable workflow. Lesson: Do not sunk-cost a tool when the friction is structural, not technical.

### 2. The Charity Commission API
The brief said no key was needed. That is outdated — the API now requires a free key from a developer portal. Even after I got the key, my first endpoint calls all returned 404s because I had guessed the routes from an old npm package's docs.

I worked through it by reading the official PDF documentation linked from the developer portal, which has the real routes (`searchCharityName/{name}`, `charityfinancialhistory/{regNum}/{suffix}`). Then the financial table came back as all zeros — so I built a developer-mode toggle into the app to surface raw API responses inline. That immediately showed the real field names (`income`, `expenditure`) versus what I had assumed (`total_gross_income`, etc.).

Lesson: when integrating with an unknown API, build the debug surface into the tool itself. It pays for itself in five minutes.

### 3. Duplicate rows in batch mode
First version of batch screening returned duplicate rows when users pasted both a charity name and its registration number. Technically correct, practically annoying for anyone exporting to a CRM. Added a deduplication step that tracks resolved registration numbers across the run.

---

## How to run locally

```bash
git clone https://github.com/LynnKomen1/charity-intelligence-tool.git
cd charity-intelligence-tool
pip install -r requirements.txt
```

Get a free API key at [api-portal.charitycommission.gov.uk](https://api-portal.charitycommission.gov.uk/), then create `.streamlit/secrets.toml`:

```toml
CHARITY_API_KEY = "your-key-here"
```

Run it:

```bash
streamlit run app.py
```

---