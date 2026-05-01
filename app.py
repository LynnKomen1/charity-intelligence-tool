"""
mhance Charity Intelligence Tool
================================
Built for the SilverTree Pioneers technical assessment (Track A).

Helps mhance's sales team identify which UK charities are growing,
flat, or shrinking — so they can prioritise outreach to growth-stage
prospects in the Microsoft Dynamics 365 nonprofit space.

Data source: UK Charity Commission Register API (v1.0)
Docs: https://api-portal.charitycommission.gov.uk/
"""

import os
import urllib.parse
import streamlit as st
import requests
import pandas as pd

# ---------- Config ----------
try:
    API_KEY = os.environ.get("CHARITY_API_KEY") or st.secrets.get("CHARITY_API_KEY", "")
except Exception:
    API_KEY = os.environ.get("CHARITY_API_KEY", "")

BASE_URL = "https://api.charitycommission.gov.uk/register/api"
HEADERS = {"Ocp-Apim-Subscription-Key": API_KEY, "Cache-Control": "no-cache"}

st.set_page_config(
    page_title="mhance Charity Intelligence",
    page_icon="🔍",
    layout="wide",
)

if not API_KEY:
    st.error(
        "⚠️ No API key configured. Set `CHARITY_API_KEY` as an environment "
        "variable or add it to `.streamlit/secrets.toml`. "
        "Get a free key at https://api-portal.charitycommission.gov.uk/"
    )
    st.stop()


# ---------- Helpers ----------
def get_trend(values):
    if len(values) < 2 or values[0] == 0:
        return "→ Insufficient data", 0
    pct = (values[-1] - values[0]) / values[0] * 100
    if pct > 5:
        return f"↑ Growing ({pct:+.1f}%)", pct
    if pct < -5:
        return f"↓ Declining ({pct:+.1f}%)", pct
    return f"→ Flat ({pct:+.1f}%)", pct


def is_hot_prospect(values):
    for i in range(1, len(values)):
        if values[i - 1] > 0:
            yoy = (values[i] - values[i - 1]) / values[i - 1] * 100
            if yoy > 10:
                return True
    return False


# ---------- API calls (cached) ----------
@st.cache_data(ttl=3600, show_spinner=False)
def search_by_name(name):
    encoded = urllib.parse.quote(name)
    url = f"{BASE_URL}/searchCharityName/{encoded}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


@st.cache_data(ttl=3600, show_spinner=False)
def get_charity_details(reg_number, suffix=0):
    url = f"{BASE_URL}/charitydetails/{reg_number}/{suffix}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            return data[0] if isinstance(data, list) and data else data
    except Exception:
        pass
    return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_financial_history(reg_number, suffix=0):
    url = f"{BASE_URL}/charityfinancialhistory/{reg_number}/{suffix}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_trustee_names(reg_number, suffix=0):
    url = f"{BASE_URL}/charitytrusteenamesV2/{reg_number}/{suffix}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def resolve_to_charity(query):
    """Resolve a name or number to (reg_num, name) — picks first match."""
    query = query.strip()
    if not query:
        return None
    if query.isdigit():
        details = get_charity_details(query)
        if details:
            return (
                details.get("reg_charity_number") or details.get("organisation_number"),
                details.get("charity_name", "Unknown"),
            )
    else:
        results = search_by_name(query)
        if results:
            first = results[0]
            return (
                first.get("reg_charity_number") or first.get("organisation_number"),
                first.get("charity_name", "Unknown"),
            )
    return None


def analyse_charity(reg_num, name):
    """Pull financials and return a summary dict for batch view."""
    history = get_financial_history(reg_num)
    if not history:
        return {
            "Charity": name.title(),
            "Reg #": reg_num,
            "Latest income": None,
            "Income trend": "No data",
            "Income growth %": None,
            "Hot prospect": "—",
        }
    sorted_hist = sorted(history, key=lambda x: x.get("financial_period_end_date", ""))[-3:]
    incomes = [e.get("income") or 0 for e in sorted_hist]
    trend_label, pct = get_trend(incomes)
    hot = is_hot_prospect(incomes)
    return {
        "Charity": name.title(),
        "Reg #": reg_num,
        "Latest income": incomes[-1] if incomes else 0,
        "Income trend": trend_label,
        "Income growth %": round(pct, 1) if incomes else None,
        "Hot prospect": "🔥 YES" if hot else "—",
    }


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### About this tool")
    st.markdown(
        "Built for the SilverTree Pioneers technical assessment (Track A).\n\n"
        "**What it does:** look up any UK charity, see 3-year financial trends, "
        "and flag fast-growing organisations as **hot prospects** for outreach."
    )
    st.divider()
    st.markdown("### Try these examples")
    st.code("Oxfam\nCancer Research UK\n4 Cancer Group\n1090133", language=None)
    st.divider()
    dev_mode = st.checkbox("🔧 Developer mode (show raw API responses)", value=False)


# ---------- Header ----------
st.title("🔍 Charity Intelligence Tool")
st.caption(
    "Built for **mhance** — instantly see which UK charities are growing, "
    "shrinking, or flat. Spot hot prospects in seconds, not minutes."
)


# ---------- Tabs ----------
tab1, tab2 = st.tabs(["🔎 Single charity lookup", "📋 Batch prospect screening"])


# ============================================================
# TAB 1 — Single charity lookup
# ============================================================
with tab1:
    query = st.text_input(
        "Enter charity name or registration number",
        placeholder="e.g. Oxfam or 202918",
    )

    if query:
        query = query.strip()

        if query.isdigit():
            with st.spinner("Looking up charity..."):
                details = get_charity_details(query)
            results = [details] if details else []
        else:
            with st.spinner("Searching the Register of Charities..."):
                results = search_by_name(query)

        if dev_mode:
            with st.expander("🔧 Debug: raw search response"):
                st.json(results[0] if results else "No results")

        if not results:
            st.warning("No charities found. Try a different search term.")
        else:
            if len(results) > 1:
                options = [
                    f"{c.get('charity_name', 'Unknown')} ({c.get('reg_charity_number') or c.get('organisation_number') or ''})"
                    for c in results
                ]
                choice = st.selectbox("Multiple matches — pick one:", options)
                charity = results[options.index(choice)]
            else:
                charity = results[0]

            reg_num = (
                charity.get("reg_charity_number")
                or charity.get("registered_charity_number")
                or charity.get("organisation_number")
            )
            name = charity.get("charity_name", "Unknown").title()

            st.divider()
            st.subheader(f"📋 {name}")
            st.caption(f"Charity registration number: **{reg_num}**")

            col1, col2 = st.columns([3, 2])

            with col1:
                st.markdown("### 💰 Financial trends — last 3 years")
                history = get_financial_history(reg_num)

                if dev_mode:
                    with st.expander("🔧 Debug: raw financial response"):
                        st.json(history)

                if history:
                    sorted_hist = sorted(
                        history, key=lambda x: x.get("financial_period_end_date", "")
                    )[-3:]

                    rows, incomes, expenditures = [], [], []
                    for entry in sorted_hist:
                        year = (entry.get("financial_period_end_date") or "")[:4]
                        inc = entry.get("income") or 0
                        exp = entry.get("expenditure") or 0
                        rows.append({"Year": year, "Income": inc, "Expenditure": exp})
                        incomes.append(inc)
                        expenditures.append(exp)

                    if rows:
                        df = pd.DataFrame(rows)
                        display_df = df.copy()
                        display_df["Income"] = display_df["Income"].apply(lambda x: f"£{x:,.0f}")
                        display_df["Expenditure"] = display_df["Expenditure"].apply(lambda x: f"£{x:,.0f}")
                        st.dataframe(display_df, hide_index=True, use_container_width=True)

                        if is_hot_prospect(incomes):
                            st.success(
                                "🔥 **HOT PROSPECT** — Income grew >10% year-on-year. "
                                "Strong candidate for outreach."
                            )

                        income_label, _ = get_trend(incomes)
                        exp_label, _ = get_trend(expenditures)
                        c1, c2 = st.columns(2)
                        c1.metric("Income (3-yr)", income_label)
                        c2.metric("Expenditure (3-yr)", exp_label)

                        chart_df = df.set_index("Year")
                        st.line_chart(chart_df)

                        csv = df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "⬇️ Export this charity's data to CSV",
                            csv,
                            f"{name.replace(' ', '_')}_financials.csv",
                            "text/csv",
                        )
                    else:
                        st.info("No financial history available for this charity.")
                else:
                    st.info("Financial data unavailable for this charity.")

            with col2:
                st.markdown("### 👥 Trustees")
                trustees = get_trustee_names(reg_num)
                if trustees:
                    for t in trustees[:10]:
                        tname = (t.get("trustee_name") or t.get("name", "Unknown")).title()
                        st.write(f"• {tname}")
                    if len(trustees) > 10:
                        st.caption(f"…and {len(trustees) - 10} more")
                else:
                    st.info("No trustee data available.")


# ============================================================
# TAB 2 — Batch prospect screening
# ============================================================
with tab2:
    st.markdown(
        "### 📋 Batch prospect screening\n"
        "Paste a list of charity names or registration numbers (one per line) "
        "to see all of them ranked by income growth. Hot prospects are flagged automatically."
    )

    default_batch = "Oxfam\nCancer Research UK\n4 Cancer Group\n1090133\nBritish Heart Foundation\nMacmillan Cancer Support"
    batch_input = st.text_area(
        "Charities to analyse (one per line):",
        value=default_batch,
        height=180,
        help="Mix names and registration numbers freely.",
    )

    if st.button("🚀 Run batch analysis", type="primary"):
        lines = [l.strip() for l in batch_input.split("\n") if l.strip()]

        if not lines:
            st.warning("Please enter at least one charity.")
        elif len(lines) > 25:
            st.warning("Limit to 25 charities at a time to respect API rate limits.")
        else:
            results = []
            progress = st.progress(0, text="Resolving charities...")

            seen_reg_nums = set()
            for i, line in enumerate(lines):
                resolved = resolve_to_charity(line)
                if resolved:
                    reg_num, name = resolved
                    if reg_num in seen_reg_nums:
                        progress.progress((i + 1) / len(lines), text=f"Skipped duplicate {i+1}/{len(lines)}")
                        continue
                    seen_reg_nums.add(reg_num)
                    summary = analyse_charity(reg_num, name)
                    results.append(summary)
                else:
                    results.append({
                        "Charity": line,
                        "Reg #": "Not found",
                        "Latest income": None,
                        "Income trend": "—",
                        "Income growth %": None,
                        "Hot prospect": "—",
                    })
                progress.progress((i + 1) / len(lines), text=f"Analysed {i+1}/{len(lines)}")

            progress.empty()

            if results:
                df = pd.DataFrame(results)
                # Sort hot prospects to top, then by growth %
                df["_sort_hot"] = df["Hot prospect"].apply(lambda x: 0 if "YES" in str(x) else 1)
                df["_sort_growth"] = df["Income growth %"].fillna(-999)
                df = df.sort_values(
                    by=["_sort_hot", "_sort_growth"],
                    ascending=[True, False]
                ).drop(columns=["_sort_hot", "_sort_growth"])

                hot_count = sum(1 for r in results if "YES" in str(r.get("Hot prospect", "")))
                if hot_count > 0:
                    st.success(f"🔥 Found **{hot_count} hot prospect{'s' if hot_count > 1 else ''}** in this batch.")

                # Pretty-format income for display
                display_df = df.copy()
                display_df["Latest income"] = display_df["Latest income"].apply(
                    lambda x: f"£{x:,.0f}" if pd.notna(x) and x else "—"
                )
                display_df["Income growth %"] = display_df["Income growth %"].apply(
                    lambda x: f"{x:+.1f}%" if pd.notna(x) else "—"
                )

                st.dataframe(display_df, hide_index=True, use_container_width=True)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Export batch results to CSV",
                    csv,
                    "charity_batch_results.csv",
                    "text/csv",
                )


# ---------- Footer ----------
st.divider()
st.caption(
    "Data source: UK Charity Commission Register · "
    "Built for the SilverTree Pioneers technical assessment · "
    "Lynn Komen, May 2026"
)