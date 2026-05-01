# Reflections

Pre- and post-build reflections.

---

## If I had a full week instead of 3 days

I had 3 days to work on this assessment. With a full week, here is what I would add — and what I would deliberately cut.

### What I would add


1. **Sector and geography filtering with discovery.** Right now the user has to know which charity they're looking for. With more time, I would let them ask: *"Show me all charities with income £500k–£2m in education, growing >10% YoY."* This shifts the value from "verify a known prospect" to "discover prospects I didn't know existed."

2. **Trustee enrichment.** The Charity Commission gives me trustee names — but a name isn't useful without context. I would cross-reference each name against Companies House and LinkedIn to surface decision-makers, board overlaps, and warm-introduction paths. This is where most of the actual sales value lives, and it's where AI tooling could really help (for example, using an LLM to summarise a trustee's professional background from public sources).

3. **CRM integration with Dynamics 365.** mhance is a Microsoft Dynamics 365 partner, so flagged prospects should sync directly into Dynamics rather than being copy-pasted from a CSV. This is poetically appropriate and the kind of integration that turns a one-off tool into part of the sales motion.

4. **Scheduled refresh and Slack alerts.** Once a charity is flagged as a watched prospect, the tool should re-check it monthly and alert the salesperson when fresh accounts are filed. This converts the tool from a manual lookup to an ambient signal.

5. **A real frontend.** Streamlit is excellent for prototypes and stakeholder demos, but for production I woud rebuild in **React with a FastAPI backend** — proper auth, audit logging, role-based access, and integration with mhance's existing identity provider (Microsoft Entra).

### What I would cut

Nothing yet. The current MVP is intentionally narrow because every feature in it earns its place by directly answering the original brief: *"someone types in a charity name and gets back income, expenditure, trends, and trustees."* Adding scope before that core flow felt complete would have hurt clarity.

I would consider whether the line chart is necessary — for a 3-year window, the table plus trend label tells the story. The chart is partly there because Streamlit makes charts cheap, which is the wrong reason to include something. I'd test removing it with users before committing to the design.

---

## Two ways I would improve this assessment for future hires

1. **State that the Charity Commission API now requires a free key.** The brief currently says "no key needed" — this is outdated. The API was migrated to a key-gated developer portal, and the signup adds about 5–10 minutes of friction. This cost me minutes of debugging when my first endpoint calls all returned 401s. Either update the brief to say "free signup at this URL" or pre-issue keys to candidates.

2. **Provide one or two known-good test charity numbers in the brief.** Knowing that `202918` is Oxfam (with rich, multi-year financial data) is the difference between a 5-minute API smoke test and a 30-minute one. Without this, candidates spend time guessing whether their code is broken or whether they've just picked a charity with no filed accounts. Two reg numbers in the brief would save every candidate real time.


---