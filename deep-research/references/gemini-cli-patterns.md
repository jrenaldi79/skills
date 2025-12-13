# Gemini CLI Research Patterns

Detailed patterns for using Gemini CLI effectively in deep research workflows.

## Why Gemini CLI for Research

Gemini CLI enables:
- **Parallel execution** - Spawn multiple sub-agents to execute tasks simultaneously
- **Deep content extraction** - web_fetch retrieves full article text, not just summaries
- **Scale** - Handle dozens of searches and fetches in a single turn
- **Efficiency** - Gather all raw data before analysis, avoiding context-switching

## Core Pattern: Autonomous Sub-Agents

To run Gemini CLI as a non-interactive, autonomous sub-agent that automatically approves tool use and outputs to files, you MUST use the following flags:

1. `--yolo` (or `-y`): **CRITICAL**. Stands for "You Only Look Once". Tells the agent to automatically accept all tool calls without waiting for user confirmation.
2. `> output.txt 2> error.txt`: Standard bash redirection to capture the agent's final answer (stdout) and any logs/errors (stderr) into separate files.

### The Exact Command Pattern

```bash
/Users/john_renaldi/.npm-global/bin/gemini "YOUR PROMPT HERE" --yolo > /tmp/output.txt 2> /tmp/error.txt &
```

**Breakdown:**
- `/Users/.../gemini`: Full path to executable (safer than just `gemini`).
- `"YOUR PROMPT HERE"`: Self-contained task instructions.
- `--yolo`: **MANDATORY**. Without this, the sub-agent hangs waiting for input.
- `> /tmp/output.txt`: Captures final response.
- `2> /tmp/error.txt`: Captures debug logs/errors.
- `&`: Runs in background for parallelization.

## Parallel Execution Workflow

**ALWAYS** spawn multiple agents simultaneously for different sub-questions.

### Example: Spawning 3 Agents at Once

```bash
# 1. Financials Agent
/Users/john_renaldi/.npm-global/bin/gemini "Research Life360 Q3 2025 revenue. Perform google_web_search, then web_fetch top 3 results." --yolo > /tmp/fin.txt 2> /tmp/fin_err.txt &

# 2. Technical Agent
/Users/john_renaldi/.npm-global/bin/gemini "Analyze Life360 AWS architecture. Perform google_web_search, then web_fetch top 3 results." --yolo > /tmp/tech.txt 2> /tmp/tech_err.txt &

# 3. Privacy Agent
/Users/john_renaldi/.npm-global/bin/gemini "Summarize Life360 data privacy lawsuits. Perform google_web_search, then web_fetch top 3 results." --yolo > /tmp/priv.txt 2> /tmp/priv_err.txt &

# Wait for all to finish
wait
```

## Sub-Agent Prompt Design

The prompt string passed to the sub-agent must be explicit and self-contained. It should instruct the sub-agent to:
1. Perform specific searches (give keywords)
2. Identify relevant URLs
3. **Explicitly use `web_fetch`** on those URLs (search summaries are insufficient)
4. Synthesize findings

**Good Prompt Example:**
> "Research the economic impact of AI in healthcare for 2024. Run 3 distinct google_web_searches. Select the top 5 most relevant articles and use web_fetch to extract their full text. Summarize the key economic figures, cost savings, and market growth projections found in the full text."

## Best Practices

### Search Query Design
- Use 3-5 search variations per sub-question
- Vary keywords to capture different perspectives
- Include year/timeframe when recency matters

### URL Selection for web_fetch
Prioritize:
1. Academic papers and peer-reviewed journals
2. Government and regulatory sources
3. Industry reports from reputable organizations
4. Established news outlets

Avoid:
- Marketing content and press releases (unless official statements needed)
- Blog posts without clear expertise
- Paywalled content that may not extract fully
