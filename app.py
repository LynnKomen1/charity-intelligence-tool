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
# Try environment variable first, then Streamlit secrets
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

# ---------- Header ----------
st.title("🔍 Charity Intelligence Tool")
st.caption(
    "Built for **mhance** — instantly see which UK charities are growing, "
    "shrinking, or flat. Spot hot prospects in seconds, not minutes."
)
# Sanity check that we have a key (must come AFTER set_page_config)
if not API_KEY:
    st.error(
        "⚠️ No API key configured. Set `CHARITY_API_KEY` as an environment "
        "variable or add it to `.streamlit/secrets.toml`. "
        "Get a free key at https://api-portal.charitycommission.gov.uk/"
    )
    st.stop()

# ---------- Helpers ----------
def get_trend(values):
    """Trend label based on first vs last value over the period."""
    if len(values) < 2 or values[0] == 0:
        return "→ Insufficient data"
    pct = (values[-1] - values[0]) / values[0] * 100
    if pct > 5:
        return f"↑ Growing ({pct:+.1f}%)"
    if pct < -5:
        return f"↓ Declining ({pct:+.1f}%)"
    return f"→ Flat ({pct:+.1f}%)"


def is_hot_prospect(values):
    """Hot prospect = income grew >10% year-on-year at any point."""
    for i in range(1, len(values)):
        if values[i - 1] > 0:
            yoy = (values[i] - values[i - 1]) / values[i - 1] * 100
            if yoy > 10:
                return True
    return False


# ---------- API calls (cached for 1 hour) ----------
@st.cache_data(ttl=3600, show_spinner=False)
def search_by_name(name):
    encoded = urllib.parse.quote(name)
    url = f"{BASE_URL}/searchCharityName/{encoded}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.json()
        st.error(f"Name search failed ({r.status_code})")
    except Exception as e:
        st.error(f"Search error: {e}")
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


# ---------- Sidebar with developer mode ----------
with st.sidebar:
    st.markdown("### About this tool")
    st.markdown(
        "Built for the SilverTree Pioneers technical assessment (Track A).\n\n"
        "**What it does:** look up any UK charity, see 3-year financial trends, "
        "and flag fast-growing organisations as **hot prospects** for outreach."
    )
    st.divider()
    st.markdown("### Try these examples")
    st.code("Oxfam\nCancer Research UK\n202918  ← Oxfam's reg number", language=None)
    st.divider()
    dev_mode = st.checkbox("🔧 Developer mode (show raw API responses)", value=False)


# ---------- UI ----------
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
        # Disambiguation
        if len(results) > 1:
            options = [
                f"{c.get('charity_name', 'Unknown')} ({c.get('reg_charity_number') or c.get('registered_charity_number') or ''})"
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

        # ---- Financials ----
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

                    # Display table with currency formatting
                    display_df = df.copy()
                    display_df["Income"] = display_df["Income"].apply(lambda x: f"£{x:,.0f}")
                    display_df["Expenditure"] = display_df["Expenditure"].apply(lambda x: f"£{x:,.0f}")
                    st.dataframe(display_df, hide_index=True, use_container_width=True)

                    # Hot prospect flag goes ABOVE the chart so it's the first thing seen
                    if is_hot_prospect(incomes):
                        st.success(
                            "🔥 **HOT PROSPECT** — Income grew >10% year-on-year. "
                            "Strong candidate for outreach."
                        )

                    # Trend metrics
                    c1, c2 = st.columns(2)
                    c1.metric("Income trend (3-yr)", get_trend(incomes))
                    c2.metric("Expenditure trend (3-yr)", get_trend(expenditures))

                    # Chart
                    chart_df = df.set_index("Year")
                    st.line_chart(chart_df)

                    # CSV export
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

        # ---- Trustees ----
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

st.divider()
st.caption(
    "Data source: UK Charity Commission Register · "
    "Built for the SilverTree Pioneers technical assessment · "
    "Lynn Komen, May 2026"
)