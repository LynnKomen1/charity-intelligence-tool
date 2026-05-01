# 🔍 mhance Charity Intelligence Tool

A lightweight web app that helps mhance's sales team identify which UK charities are growing, flat, or shrinking — so they can prioritise outreach to growth-stage prospects in the Microsoft Dynamics 365 nonprofit space.

**Live demo:** https://lynn-charity-intelligence-tool.streamlit.app

Built for the **SilverTree Pioneers technical assessment — Track A**.

---

## What it does

A salesperson types a charity name or registration number into the search box. Within a few seconds, the tool returns:

- 📊 Last 3 years of **income** and **expenditure** with percentage trend
- 📈 Visual trend chart (income vs. expenditure)
- 🔥 **HOT PROSPECT** flag if income grew >10% year-on-year
- 👥 List of charity trustees
- ⬇️ One-click **CSV export** for piping data into the sales pipeline

This replaces what used to be a manual workflow: opening individual records on the Charity Commission register and eyeballing PDF accounts. The salesperson now spends 10 seconds per charity instead of 5–10 minutes.

---

## Try these examples

| Charity | Reg # | Why it's interesting |
|---|---|---|
| `Oxfam` | `202918` | Large charity in decline (-15% income) |
| `Cancer Research UK` | `1089464` | Steady but expenditure outpacing income |
| `4 Cancer Group` | `1090133` | 🔥 Hot prospect: +21.6% income growth |

---

## Stack & decisions

| Layer | Choice | Why |
|---|---|---|
| Backend | **Python** | Best ecosystem for AI/data work, fastest to ship |
| UI | **Streamlit** | Zero-frontend overhead, instantly shareable, looks polished out of the box |
| Data | **UK Charity Commission Register API (v1.0)** | Official, free, real-time |
| Hosting | **Streamlit Community Cloud** | Free, public URL, GitHub-integrated CI/CD |
| Caching | `@st.cache_data` (1-hour TTL) | Reduces API calls, faster repeat lookups |
| Secrets | Streamlit secrets + env vars | API key stays out of the repo |

### Decisions I made & alternatives I considered

- **Streamlit over Flask/FastAPI:** I prioritised time-to-demo over flexibility. A FastAPI + React build would be more production-grade but would have taken 3-4× longer for the same demo value.
- **Hosted over local:** the brief said "hosted is better." Streamlit Cloud was a 5-minute deploy from a GitHub push — no Docker, no server config.
- **Sales-first language ("HOT PROSPECT", "outreach"):** every label is written for the user (mhance's sales team), not for an engineer. The tool isn't a data viewer; it's a prioritisation tool.
- **Trend thresholds (5% flat, 10% hot):** these are placeholder business rules. In production, mhance's sales leadership would calibrate these based on conversion data.
- **Hot prospect placement:** the flag sits **above** the chart, not below it — so the most actionable signal is the first thing a salesperson sees.
- **Developer mode toggle:** raw API responses are hidden by default but accessible via a sidebar toggle. Good for debugging in production without confusing end users.

---

## What I'd do differently with a full week

I had ~5 hours focused build time. With a full week, I'd cut nothing from the current MVP — but I'd add:

1. **Multi-charity batch search** — paste a list of names/reg numbers, get a single ranked CSV. This is the actual sales workflow.
2. **Sector filtering & "find me hot prospects in education"** — turn the tool from a lookup into a discovery engine.
3. **Trustee enrichment** — cross-reference trustee names against LinkedIn/Companies House to surface decision-makers and warm-intro paths. This is where the real sales value is.
4. **Outreach status & CRM integration** — sync flagged prospects directly into mhance's Dynamics 365 (poetic given they're a Dynamics partner).
5. **Scheduled refresh + alerting** — re-run flagged charities monthly; ping a Slack channel when a watched charity files new accounts.
6. **A real frontend** — Streamlit is great for prototypes; for production I'd rebuild the UI in React + a FastAPI backend, with proper auth and audit logging.

What I'd cut: nothing yet. The MVP is intentionally narrow.

---

## Production-readiness gaps

The current build is a working prototype. To take it to production, the next priorities would be:

- **Error handling for API rate limits** — the Charity Commission API rate-limits requests; I'd add exponential backoff and a Redis-based shared cache.
- **Auth** — Streamlit Cloud's public URL has no access control. Production would need SSO (probably Microsoft Entra given mhance's Microsoft alignment).
- **Monitoring** — basic logging exists; production needs Sentry for errors and a usage dashboard.
- **Tests** — no automated tests yet. Priority test coverage: trend calculation logic, hot-prospect logic, API response parsing.
- **Data freshness indicator** — the cache is 1-hour TTL but the user can't see when data was last fetched. A "last updated" stamp would build trust.

---

## One thing that didn't work, and how I worked it out

**The Charity Commission API endpoints I initially used returned 404 errors for every search.**

The assessment brief said the API needed no key, but the real API requires a free key from the developer portal. Once I had the key, my searches still 404'd because I'd guessed the endpoint paths from a stale npm package's docs.

**How I worked it out:** I traced the official PDF documentation linked from the developer portal (`API_GET_operations_v1.1.pdf`), which has the actual endpoint routes (`searchCharityName/{name}`, `charityfinancialhistory/{regNum}/{suffix}`, etc.). I added a "Developer mode" toggle that surfaces the raw API response inline — that let me see the real field names (`financial_period_end_date`, `income`, `expenditure`) which differed from what I'd guessed (`fin_period_end_date`, `total_gross_income`, etc.). I corrected the field names and the data flowed through.

**Lesson:** Don't trust LLM-generated assumptions about a real API. Build a debug surface into the tool itself — it pays for itself in five minutes.

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

## Three ways I'd improve this assessment for future hires

1. **State that the Charity Commission API requires a free key.** The brief says "no key needed" — this is no longer true and cost me ~30 minutes of confused debugging. Either say "free signup at this URL" or pre-issue keys.
2. **Provide one or two known-good test charities upfront.** Knowing that `202918` is Oxfam (with rich data) is the difference between a 5-minute API smoke test and a 30-minute one. Mentioning a couple of reg numbers in the brief saves candidates real time.
3. **Be explicit about whether stretch goals are graded.** I prioritised core correctness then stretch goals — but the brief is ambiguous. Clarifying "everything beyond core is for time-permitting bonus, no penalty for skipping" would let candidates allocate their time more confidently and reduce stress for less-experienced builders.

---

**Built by Lynn Komen, May 2026**