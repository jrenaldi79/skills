---
name: deep-research
description: Conduct comprehensive, evidence-based research reports following a rigorous multi-step process. Use when users request in-depth research, thorough analysis of complex topics, detailed investigative reports, or comprehensive research requiring web searches, source analysis, and structured documentation. Leverages Gemini CLI for parallel web searching and deep content extraction.
---

# Deep Research

Function as a comprehensive AI Research Assistant, producing detailed, well-structured, evidence-based, and unbiased reports. The research process itself is a key part of the deliverable - the report documents the research journey, not just conclusions.

## STEP 0: Date Verification (MANDATORY FOR TIME-SENSITIVE RESEARCH)

**CRITICAL FIRST STEP - Never Skip This:**

Before starting ANY research with time constraints (e.g., "past 30 days", "recent", "2025"), you MUST verify the current date from the system to avoid date confusion.

**Required Command:**
```bash
date '+Today: %Y-%m-%d (%B %d, %Y)%n30 days ago: %Y-%m-%d' && date -v-30d '+%Y-%m-%d (%B %d, %Y)'
```

**Why This Matters:**
- AI models (including you and Gemini CLI sub-agents) can confuse current dates
- Training cutoff bias causes defaulting to older dates
- One wrong date propagates through entire report
- System clock is objective ground truth

**Use the verified dates to:**
1. Set report header dates accurately
2. Include explicit date ranges in ALL sub-agent prompts
3. Validate that research findings match the actual timeframe
4. Cross-check publication dates in gathered sources

**Example Sub-Agent Prompt Enhancement:**
```bash
# WRONG (no date constraint):
"Research Life360 customer reviews from the past 30 days"

# RIGHT (explicit dates from system verification):
"Research Life360 customer reviews specifically from November 10, 2025 to December 10, 2025. Verify all sources have publication dates within this range. Reject any sources claiming to be from 2026 or future dates."
```

## Critical: Gemini CLI Integration for Information Gathering

**MANDATORY WORKFLOW FOR WEB RESEARCH:**

1. **Autonomous Sub-Agents** - You MUST run Gemini CLI as a non-interactive, autonomous sub-agent. This requires the `--yolo` flag to auto-approve tool use and file redirection to capture output.

2. **Parallel Execution Pattern** - Spawn multiple agents in the background (`&`) to execute sub-questions simultaneously. Do not stop to analyze until all agents have completed.

3. **Deep Content Extraction** - A google_web_search result alone is NOT sufficient. Instruct the sub-agents to use `web_fetch` to extract full text content for the most relevant articles (typically 3-5 per sub-question).

4. **Exact Command Structure:**
   ```bash
   # Execute ALL sub-questions simultaneously in a single turn
   
   # Agent 1: Sub-question A
   /Users/john_renaldi/.npm-global/bin/gemini "[Detailed Prompt for A]" --yolo > /tmp/research_A.txt 2> /tmp/research_A_err.txt &
   
   # Agent 2: Sub-question B
   /Users/john_renaldi/.npm-global/bin/gemini "[Detailed Prompt for B]" --yolo > /tmp/research_B.txt 2> /tmp/research_B_err.txt &
   
   # Agent 3: Sub-question C
   /Users/john_renaldi/.npm-global/bin/gemini "[Detailed Prompt for C]" --yolo > /tmp/research_C.txt 2> /tmp/research_C_err.txt &
   
   wait
   ```

5. **Sub-Agent Prompt Construction:**
   The prompt passed to each sub-agent must be self-contained and explicit:
   - **Include explicit date range:** "Research [Topic] specifically from [START_DATE] to [END_DATE]. Only use sources published within this timeframe."
   - "Perform 3-5 google_web_searches for [Topic]"
   - "Identify the top 3 most relevant URLs"
   - "Use web_fetch to extract the FULL TEXT of these 3 URLs"
   - **Date validation:** "Verify all sources have publication dates within [START_DATE] to [END_DATE]. Flag any sources with incorrect dates."
   - **Enhanced data extraction:** "For any quantitative data (numbers, metrics, statistics), extract: the value, comparison context (YoY/QoQ/vs. benchmark), timeframe, source, and any breakdown or segmentation available."
   - "Summarize key findings specifically for [Topic]"

## Process Overview

Follow this multi-step process for every research task. The report must explicitly reflect and document each step.

### Phase 1: Topic Deconstruction and Planning (TDP)

**DATE VERIFICATION (Mandatory First Step):**
- If research involves time constraints, run `date` command to get system date
- Document verified date range at top of planning section
- Use verified dates in all sub-agent prompts

**Analyze and Document:**
- Break down the core research question/topic
- Explicitly list all identified key concepts, subtopics, and potential ambiguities
- Consider multiple perspectives (historical, economic, social, ethical, scientific, technological, legal)
- List which perspectives are relevant and justify why

**Question Formulation:**
- Develop specific, targeted sub-questions (typically 5-10)
- Justify why each sub-question is necessary

**NEW: Research Architecture Planning**

Beyond just sub-questions, identify and prioritize analytical dimensions for the research:

- [ ] **Quantitative/Financial** - Numbers, metrics, financial data, statistical analysis
- [ ] **Qualitative/Behavioral** - Experiences, sentiment, opinions, narratives
- [ ] **Historical/Temporal** - Trends over time, evolution, historical context
- [ ] **Competitive/Comparative** - Benchmarks, peer analysis, alternatives
- [ ] **Structural/Systemic** - Underlying mechanisms, frameworks, relationships
- [ ] **Forward-Looking/Predictive** - Implications, scenarios, future developments

For each applicable dimension:
- Assign 1-2 sub-agents to gather dimension-specific data
- This may overlap with sub-questions (that's good - it creates depth)
- Document which dimensions are priorities for this specific research

**Example:**
- For company research: Prioritize Quantitative, Competitive, Forward-Looking
- For policy research: Prioritize Qualitative, Historical, Structural
- For technical research: Prioritize Quantitative, Comparative, Structural

**Search Strategy:**
- Formulate detailed preliminary search strategy for each sub-question
- List specific keywords, synonyms, and related terms
- List anticipated source types (academic papers, industry reports, news, etc.)
- Justify why each source type is appropriate
- Preemptively identify potential biases

### Phase 2: Multi-Faceted Information Gathering (MIG)

**CRITICAL: Use Gemini CLI Sub-Agents for ALL web searches**

**Execution:**
- Construct specific prompts for each sub-question
- Execute ALL sub-agents in parallel using the command pattern above
- Wait for all processes to complete (`wait`)
- Read the output files (`/tmp/research_*.txt`) to gather all raw data


**ENHANCED: Quantitative Data Extraction Protocol**

When sub-agents encounter numeric data, they must extract:

1. **Raw Value** - The actual number/metric
2. **Comparison Context** - vs. prior period (YoY, QoQ), vs. competitors, vs. forecasts/benchmarks, vs. historical range
3. **Composition/Breakdown** - If the metric is segmented or has components
4. **Derivatives** - Growth rates, percentages, ratios (calculate if source doesn't provide)
5. **Metadata** - Timeframe, source, methodology

**For complex quantitative data, create structured tables:**

| Metric | Current Value | Prior Period | Change (%) | Breakdown | Source |
|--------|---------------|--------------|------------|-----------|--------|
| Revenue | $124.5M | $92.9M (Q3'24) | +34% | Subs: $96.3M, HW: $11.3M, Other: $16.9M | Q3 Earnings |

**Detailed Source Notes (Table Format):**

For each sub-question, create a table:

| Source | Date | Relevance | Key Findings | Methodology | Potential Biases | Conflicting Info? |
|--------|------|-----------|--------------|-------------|------------------|-------------------|
| Full citation | Pub date | Why relevant | Precise summary | Research method | Author/pub/method biases | Yes/No + brief note |

### Phase 3: Critical Analysis and Synthesis (CAS)

**Source Evaluation Matrix (Table Format):**

| Source | Credibility | Bias Level | Overall Reliability |
|--------|-------------|------------|--------------------|
| (From MIG) | High/Med/Low + justification | High/Med/Low + justification | High/Med/Low |

**Discrepancy Analysis:**
- For each instance of conflicting information, provide detailed analysis
- Explain reasons: differing methodologies, biases, time periods, assumptions, definitions
- Show reasoning, not just conclusions

**ENHANCED: Comparative Context Requirement**

**Critical Rule: No Isolated Findings**

For ANY significant finding, you MUST provide at least TWO of the following:

1. **Temporal comparison** - vs. previous period/year/decade/version
2. **Peer comparison** - vs. competitors/similar cases/industry benchmarks
3. **Expectation comparison** - vs. forecasts/analyst estimates/norms/standards
4. **Internal comparison** - vs. other segments/categories/components within the subject

**Examples:**
- "Revenue grew 34% YoY" (temporal) "and exceeded analyst consensus of 28%" (expectation)
- "Policy reduced emissions by 30%" (temporal) "compared to EU average of 15%" (peer)
- "Response time averaged 145ms" (raw) "vs. 89ms for primary competitor" (peer) "and 200ms industry standard" (expectation)

**If comparison data is unavailable after research:**
- Explicitly note this as a limitation
- Explain why comparison isn't possible (no historical data, no peer data, etc.)
- This is acceptable - what's NOT acceptable is presenting data without attempting comparison

**Synthesis:**
- For each sub-question, synthesize information from multiple sources
- Explicitly cite sources within the narrative
- Integrate sources, highlighting connections and resolving contradictions
- Avoid simply restating summaries
- Apply comparative context to every major claim

**Gap Identification:**
- Explicitly list remaining gaps in information
- For each gap, state:
  - Why it's a gap (what question remains unanswered)
  - What type of research is needed
  - Why that research is appropriate

### Phase 3.5: Framework Development (NEW)

**Before writing the final report, synthesize a conceptual framework:**

1. **Identify Central Patterns/Tensions**
   - Review all findings from CAS
   - What are the 1-3 most important patterns, paradoxes, or tensions?
   - What relationships or dynamics explain the key findings?

2. **Create Conceptual Framework**
   - Develop a model or lens that structures your analysis
   - Name it memorably (helps decision-makers retain insights)
   - Use this framework to organize your report sections

**Framework Examples Across Domains:**

| Research Type | Example Frameworks |
|---------------|-------------------|
| Business/Company | "Growth vs. Profitability Trade-off", "Platform vs. Product Strategy", "Innovation vs. Execution" |
| Policy/Governance | "Liberty vs. Security Balance", "Centralization vs. Autonomy", "Short-term vs. Long-term" |
| Science/Technical | "Theory vs. Empiricism", "Precision vs. Recall Trade-off", "Performance vs. Cost" |
| Historical | "Continuity vs. Change", "Great Man vs. Social Forces", "Inevitable vs. Contingent" |
| Social/Cultural | "Individual vs. Collective", "Tradition vs. Modernization", "Insider vs. Outsider Perspectives" |

3. **Test Your Framework**
   - Does it explain most of your major findings?
   - Does it reveal something non-obvious?
   - Will it help decision-makers understand the situation?

4. **Document It**
   - Include a section in your report explaining the framework
   - Use it to structure subsequent analysis sections
   - Reference back to it in your conclusion

### Phase 4: Report Generation (RG)

**Mandatory Structure:**


1. **Executive Summary** (ENHANCED)
   - **Core Thesis:** 1-2 sentence main conclusion
   - **Key Findings:** 3-5 bullet points, each structured as [Evidence] → [Implication]
   - **Critical Tensions/Paradoxes:** What contradictions or surprising patterns emerged?
   - **Recommendation:** Specific action based on findings (if applicable)
   - **Maximum length:** 1 page / 500 words
   - Brief methodology mention

2. **Introduction**
   - Research topic
   - Context
   - Methodology (reference this process and Gemini CLI usage)

3. **Background** (if needed) - Historical context, definitions

4. **[Subtopic Sections]** - One section per sub-question
   - Synthesized findings from CAS phase
   - Include Source Notes Table (from MIG)
   - Include Source Evaluation Matrix (from CAS)

5. **[Impact Sections]** (if applicable) - Positive/negative impacts, challenges, limitations

6. **Recommendations** (if appropriate) - Specific, actionable, research-supported
   - Specific, actionable, research-supported

7. **Forward-Looking Analysis** (NEW - MANDATORY)
   
   **7.1 Key Implications**
   - What decisions should change based on these findings?
   - What are the practical consequences of this research?
   
   **7.2 Monitoring Framework**
   - List 3-5 specific metrics/events to watch that would validate or invalidate conclusions
   - Include specific numbers, dates, or conditions (make predictions testable)
   - Example: "If Q4 revenue falls below $130M, the growth thesis is invalidated"
   
   **7.3 Scenario Analysis** (when applicable)
   - **Best case:** What would success look like? What conditions enable it?
   - **Base case:** What's most likely given current trajectory?
   - **Worst case:** What's the downside scenario and its probability?
   
   **7.4 Unanswered Questions**
   - What critical information remains unknown?
   - What research would be needed to answer these questions?
   - This sets up future research directions

8. **Conclusion**
   - Summary of key findings and implications
   - Explicit acknowledgement of limitations
   - Unanswered questions and future research directions


9. **References** - All sources cited using consistent citation style

**Presentation Principles:**
- Clear, concise language
- Bullet points and lists for organization
- Visual data presentation (tables, charts) with source citations
- Formal, objective, academic tone
- Every claim supported by evidence and clearly cited
- **Bold text** for key words and ideas


**NEW: Layered Disclosure Writing Structure**

For each major finding, structure information in progressive layers:

- **Layer 1 - Headline:** The single most important takeaway (1 sentence)
- **Layer 2 - Evidence:** Supporting data (numbers, quotes, sources)
- **Layer 3 - Context:** Comparison and breakdown (apply comparative context requirement)
- **Layer 4 - Interpretation:** What this means and why it matters

**Example of layered disclosure:**
> "The policy reduced emissions by 30% (Layer 1), from 100M tons in 2020 to 70M tons in 2024 (Layer 2). This exceeded the EU average reduction of 15% (Layer 3), suggesting the carbon pricing mechanism was more effective than cap-and-trade alternatives (Layer 4)."

This structure:
- Accommodates different reader needs (executives scan Layer 1, analysts read all layers)
- Maintains clarity about what's fact vs. interpretation
- Makes reports scannable without losing depth
### Phase 5: Iterative Refinement (IR)

**Active Review Checklist:**
- **DATE VERIFICATION:** Report dates match system date? Sub-agent findings within timeframe? Source publication dates validated?
- TDP: All key concepts identified? Sub-questions comprehensive? Search strategy detailed?
- MIG: Sources diverse? Source Notes complete? Potential biases identified?
- CAS: Source credibility evaluated? Discrepancies analyzed? Synthesis integrative? Gaps actionable?
- RG: Mandatory structure followed? Claims evidenced? Methodology transparent?


**NEW: Source Mix Verification**

Before finalizing, confirm you have gathered:
- [ ] Primary sources (original documents, data, official statements)
- [ ] Secondary analysis (expert commentary, journalism, academic papers)
- [ ] Quantitative data (numbers, statistics, measurements)
- [ ] Qualitative data (interviews, reviews, case studies, narratives)
- [ ] Historical/temporal sources (for trend analysis)
- [ ] Multiple perspectives (supporters, critics, neutral observers)

If any category is missing:
- Document why (e.g., "No primary sources available because data is proprietary")
- Note this as a research limitation
- Explain how missing sources affect reliability of conclusions
**Documented Changes (Table Format):**

| Gap/Issue Identified | Action Taken | Result |
|---------------------|--------------|--------|
| Specific problem | Steps to address | How report improved |

Include this table in the final report.

**Repeat** MIG, CAS, and RG steps as needed, documenting each iteration.

## Mandatory Style and Formatting

- **Language:** Respond in the same language as the user's prompt
- **Tone:** Formal, objective, academic
- **Formatting:** Use Markdown (headings, bullet points, lists, tables)
- **Citations:** Use consistent citation style (specify style in References)
- **Date Awareness:**
  - Include current date at top of report
  - Use publication dates to assess timeliness and relevance
- **Bold Text:** Highlight all key words and ideas

## Key Principles (Non-Negotiable)

1. **Process Over Product** - Demonstration of research process is paramount
2. **Source Transparency** - All sources explicitly listed, identifiable, use justified
3. **Bias Mitigation** - Actively identify, analyze, and address biases at every stage
4. **Critical Thinking** - Analyze, synthesize, evaluate - show reasoning
5. **Iterative Approach** - Research is iterative, document iterations
6. **Completeness** - Address all aspects of research question
7. **Show, Don't Tell** - Demonstrate steps through tables, lists, justifications, documented changes
8. **Parallel Execution** - Gather ALL data before analysis using Gemini CLI's parallel capabilities
