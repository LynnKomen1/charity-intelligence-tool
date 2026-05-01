# Reflections

Pre- and post-build reflections, as requested in the assessment brief.

---

## If I had a full week instead of 3 days

I had ~5 hours of focused build time across one afternoon. With a full week, here's what I'd add — and what I'd deliberately cut.

### What I'd add

1. **Multi-charity batch search.** A salesperson rarely looks up one charity in isolation. The real workflow is: paste a list of 50 registration numbers, get back a ranked CSV with trends, hot-prospect flags, and trustees — pre-sorted by growth rate. This single feature would change the tool from a lookup utility into a prospecting engine.

2. **Sector and geography filtering with discovery.** Right now the user has to know which charity they're looking for. With more time, I'd let them ask: *"Show me all charities with income £500k–£2m in education, growing >10% YoY."* This shifts the value from "verify a known prospect" to "discover prospects I didn't know existed."

3. **Trustee enrichment.** The Charity Commission gives me trustee names — but a name isn't useful without context. I'd cross-reference each name against Companies House and LinkedIn to surface decision-makers, board overlaps, and warm-introduction paths. This is where most of the actual sales value lives, and it's where AI tooling could really help (for example, using an LLM to summarise a trustee's professional background from public sources).

4. **CRM integration with Dynamics 365.** mhance is a Microsoft Dynamics 365 partner, so flagged prospects should sync directly into Dynamics rather than being copy-pasted from a CSV. This is poetically appropriate and the kind of integration that turns a one-off tool into part of the sales motion.

5. **Scheduled refresh and Slack alerts.** Once a charity is flagged as a watched prospect, the tool should re-check it monthly and alert the salesperson when fresh accounts are filed. This converts the tool from a manual lookup to an ambient signal.

6. **A real frontend.** Streamlit is excellent for prototypes and stakeholder demos, but for production I'd rebuild in **React with a FastAPI backend** — proper auth, audit logging, role-based access, and integration with mhance's existing identity provider (Microsoft Entra).

### What I'd cut

Honestly — nothing yet. The current MVP is intentionally narrow because every feature in it earns its place by directly answering the original brief: *"someone types in a charity name and gets back income, expenditure, trends, and trustees."* Adding scope before that core flow felt complete would have hurt clarity.

If anything, I'd consider whether the line chart is even necessary — for a 3-year window, the table plus trend label tells the story. The chart is partly there because Streamlit makes charts cheap, which is the wrong reason to include something. I'd test removing it with users before committing to the design.

---

## Three ways I'd improve this assessment for future hires

1. **State that the Charity Commission API now requires a free key.** The brief currently says "no key needed" — this is outdated. The API was migrated to a key-gated developer portal, and the signup adds about 5–10 minutes of friction. This cost me ~30 minutes of confused debugging when my first endpoint calls all returned 401s. Either update the brief to say "free signup at this URL" or pre-issue keys to candidates.

2. **Provide one or two known-good test charity numbers in the brief.** Knowing that `202918` is Oxfam (with rich, multi-year financial data) is the difference between a 5-minute API smoke test and a 30-minute one. Without this, candidates spend time guessing whether their code is broken or whether they've just picked a charity with no filed accounts. Two reg numbers in the brief would save every candidate real time.

3. **Be explicit about whether stretch goals are graded.** The brief lists stretch goals but doesn't say whether they're "do these for bonus points" or "do these to be competitive." I prioritised core correctness first, then a few stretch goals, but the ambiguity meant I spent some time second-guessing the allocation. A line like *"core is mandatory; stretch goals are bonus and skipping them won't hurt your score"* would let candidates allocate time more confidently — particularly less-experienced builders who could otherwise spend hours over-engineering features that aren't being assessed.

---

**Lynn Komen, May 2026**