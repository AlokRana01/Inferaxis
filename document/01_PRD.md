# Product Requirements Document (PRD)

## Project: Inferaxis — Autonomous AI for Evidence-Based Data Intelligence
**Document Version:** 1.0.0  
**Status:** Approved / Active Development  
**Target Release:** MVP (Phase 1)  
**Author:** Inferaxis Core Architecture & Product Team  
**Last Updated:** October 2026  

---

## 1. Executive Summary

**Inferaxis** is an autonomous AI-powered data intelligence platform designed to transform raw tabular datasets and natural-language business questions into **evidence-backed analysis, statistical insights, interactive visualizations, and actionable recommendations**.

Unlike generic conversational AI chatbots that hallucinate numbers, execute unvetted code, or jump to speculative conclusions, Inferaxis operates on a fundamental Data Science principle:

> **"The AI reasons about the analysis. Controlled Python tools perform the analysis."**

Inferaxis orchestrates specialized agentic roles (Supervisor, Data Understanding, Data Quality, EDA, Statistical Analysis, Visualization, Insight, and Recommendation) via **LangGraph**. The agents select from a deterministic library of verified Python Data Science functions (Pandas, SciPy, NumPy, Scikit-learn), preventing LLM calculation hallucinations and guaranteeing reproducible, mathematically sound results.

---

## 2. Problem Statement

Organizations and professionals accumulate vast amounts of tabular data (CSVs, Excel files, database dumps) but face severe bottlenecks when trying to extract timely, trustworthy insights:

1. **The Chatbot Hallucination Trap:** Generic LLMs frequently miscalculate sums, invent percentages, misapply aggregations, and present plausible-sounding falsehoods as facts.
2. **The Black-Box Python Code Risk:** Code-interpreter style tools run arbitrary, uncontrolled code that can time out, expose security vulnerabilities, or produce irreproducible artifacts without proper validation.
3. **Statistical Illiteracy:** Standard generative models confuse correlation with causation, ignore data distributions, overlook missing value biases, and fail to perform hypothesis tests before claiming relationships exist.
4. **Data Science Talent Shortage:** Small-to-midsize businesses, product managers, and functional analysts cannot hire dedicated data science teams for every ad-hoc investigative inquiry ("Why did Q3 revenue drop in Europe?").
5. **Disconnected Toolchains:** Existing workflows require switching between Excel, Jupyter Notebooks, BI dashboards (Tableau/PowerBI), and slide presentations, creating days of latency between question and decision.

---

## 3. Product Vision & Value Proposition

### 3.1 Product Vision
To build an autonomous AI Data Scientist that **actively investigates data** rather than merely talking about it—delivering verifiable, transparent, auditable, and presentation-ready business intelligence on demand.

### 3.2 Value Proposition
* **Zero Math Hallucination:** 100% of numerical calculations and metrics are produced by deterministic Python engines.
* **Evidence-Backed Insights:** Every insight is paired with explicit statistical evidence, sample sizes, and confidence intervals.
* **Controlled Security:** Zero arbitrary code execution; all agent operations use vetted, sandboxed functional tools.
* **Actionable Recommendations:** Moves beyond "what happened" to diagnostic "why it happened" and prescriptive "what to do next".
* **Production-Grade UI:** A modern React/TypeScript workspace with live agent reasoning streams, interactive charts, and instant executive report export.

---

## 4. Target User Personas

| Persona | Role & Background | Core Pain Point | How Inferaxis Solves It |
| :--- | :--- | :--- | :--- |
| **P1: Business Analyst (Priya)** | Data-savvy analyst supporting Marketing and Operations. Proficient in Excel and basic SQL. | Spends 60% of her week cleaning data, running repetitive pivot tables, and drafting basic charts. | Uploads CSVs, asks complex diagnostic questions in plain English, and receives verified charts and bulleted evidence in minutes. |
| **P2: Product Manager (Marcus)** | Non-technical PM tracking user retention, churn, and feature adoption. | Lacks Python/R skills; BI dashboards answer "what" happened, but cannot explain "why" metrics dropped. | Asks root-cause questions ("Why did churn surge for Android users in v2.4?"); Inferaxis performs multi-variate statistical tests and pinpoints drivers. |
| **P3: Startup Founder / Executive (Elena)** | Seed-stage founder without a dedicated analytics team. | Needs rapid, defensible numbers for investor decks and strategic planning without hiring an expensive agency. | Generates boardroom-ready executive PDF/Markdown reports with audited data sources and actionable strategic next steps. |
| **P4: BI / Data Science Lead (David)** | Senior Data Scientist leading analytics infrastructure. | Skeptical of AI tools due to hallucinations, compliance risks, and lack of statistical rigor. | Inspects the full agent reasoning plan, Python tool execution logs, hypothesis test outputs (p-values, degrees of freedom), and methodology. |

---

## 5. Product Goals & Non-Goals

### 5.1 Business & Product Goals (MVP)
* **Trust & Verifiability:** Attain 100% mathematical accuracy on all tool-derived values (zero invented numbers).
* **Speed to Insight:** Deliver complete multi-faceted investigative analysis within **< 45 seconds** for datasets up to 100,000 rows.
* **Self-Service Usability:** Allow non-technical users to go from raw CSV upload to actionable insights in under 3 clicks.
* **Auditability:** Provide complete transparency into every tool call, parameters, intermediate data tables, and statistical tests.

### 5.2 Non-Goals (Out of Scope for MVP)
* Arbitrary Python shell/terminal execution by end users.
* Real-time streaming database pipelines (Kafka/Flink) or direct production database write-access.
* Deep learning / unstructured data processing (audio, image, raw video).
* End-to-end automated ML model deployment and hosting (reserved for Phase 2: AI ML Scientist).
* Native mobile applications (iOS/Android) — responsive web interface only.

---

## 6. Core Features & Capabilities

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             INFERAXIS MVP PLATFORM                             │
├─────────────────────┬───────────────────────────┬───────────────────────────┤
│   DATA MANAGEMENT   │   AGENTIC INTELLIGENCE    │   PRESENTATION & REPORT   │
├─────────────────────┼───────────────────────────┼───────────────────────────┤
│ • CSV/XLSX Ingest   │ • Supervisor Planning     │ • Live Reasoning Stream   │
│ • Schema Profiling  │ • Controlled Tool Calling │ • Interactive Recharts    │
│ • Quality Audit     │ • Statistical Engine      │ • Metric Evidence Badges  │
│ • Outlier Detection │ • Diagnostic Analysis     │ • PDF/Markdown Export     │
└─────────────────────┴───────────────────────────┴───────────────────────────┘
```

### 6.1 Data Ingestion & Understanding
* **Drag-and-Drop Ingestion:** Support CSV and Excel (`.xlsx`) files up to 50MB (up to 250,000 rows).
* **Autonomous Schema Detection:** Infer semantic data types (continuous numeric, discrete integer, categorical, datetime, text, boolean, ID).
* **Data Quality Profiling:** Automatically compute missing value rates, duplicate rows, cardinality, zero-variance columns, and extreme outliers.
* **Summary Scorecard:** Overall Data Health Score (0–100%) with actionable warnings (e.g., "Column `customer_id` has 4.2% duplicate entries").

### 6.2 Agentic Investigative Engine (LangGraph)
* **Supervisor Analysis Planning:** Parses the user question, checks schema relevance, selects the minimal necessary analytical path, and generates an inspectable execution plan.
* **Multi-Agent Specialization:**
  * *Data Quality Agent:* Checks if data cleaning or filtering is required before computation.
  * *EDA Agent:* Runs descriptive statistics, distributions, and group aggregations.
  * *Statistical Agent:* Selects and executes appropriate statistical tests (Pearson/Spearman correlation, Independent/Paired t-tests, Chi-Square test of independence, One-way ANOVA).
  * *Visualization Agent:* Recommends best-fit visual encoding (Bar, Line, Scatter, Boxplot, Heatmap).
  * *Insight Agent:* Translates statistical outputs into plain-language findings with explicit numerical citations.
  * *Recommendation Agent:* Formulates pragmatic business actions based on findings.
  * *Report Agent:* Compiles findings into an executive-ready structured briefing.

### 6.3 Controlled Data Science Tool Harness
* Pure deterministic Python functions wrapped with Pydantic validation:
  * `profile_dataset()`, `detect_outliers()`, `calculate_missing_values()`
  * `descriptive_statistics()`, `group_analysis()`, `trend_analysis()`
  * `t_test()`, `chi_square_test()`, `anova_test()`, `correlation_matrix()`
  * `generate_chart_spec()` (outputs declarative chart JSON for frontend rendering)

### 6.4 Interactive UI Workspace
* **Live Agent Execution Tracker:** Visual timeline showing active agent, reasoning step, tool call, execution duration, and status.
* **Interactive Charting Studio:** Recharts-powered responsive charts with tooltips, legend toggling, zoom, and SVG/PNG export.
* **Evidence Cards:** Visual cards highlighting metric, baseline, percentage change, statistical significance ($p$-value), and methodology note.
* **Executive Report Generator:** Single-click compilation into clean Markdown or downloadable PDF report.

---

## 7. MVP Scope vs. Future Phases

| Feature Dimension | Phase 1: MVP (Current Scope) | Phase 2: AI ML Scientist | Phase 3: Enterprise Platform |
| :--- | :--- | :--- | :--- |
| **Data Sources** | CSV, XLSX file upload | SQL Database connectors (Postgres, Snowflake) | Live data warehouses, Google Sheets, S3 |
| **Analytical Scope** | Descriptive, Diagnostic, Hypothesis Testing | Predictive ML (AutoML, XGBoost, Random Forest) | Prescriptive optimization, Causal Inference (DoWhy) |
| **Explainability** | Statistical tests, correlation vs causation checks | SHAP values, Partial Dependence plots | Counterfactual explanations, automated audits |
| **Collaboration** | Single-user local workspace, session history | Multi-user workspaces, commenting, role sharing | Team RBAC, SSO, audit trails, SOC2 compliance |
| **Export Formats** | Markdown, PDF, PNG/SVG charts | Interactive HTML notebooks, Python code export | Scheduled email digests, Slack alerts |

---

## 8. User Stories & Acceptance Criteria

### US-1: Dataset Upload & Automated Quality Profile
* **As a** Business Analyst,
* **I want to** drag and drop a 50MB CSV file into the workspace,
* **So that** I immediately see column types, missing rates, and potential data quality anomalies without writing manual inspection code.
* **Acceptance Criteria:**
  * Dataset parses within 3 seconds for 100k rows.
  * System displays total rows, columns, memory usage, and missing values breakdown per column.
  * Data Health Score is displayed with clear warning tags for columns with >20% missing values or single-value constants.

### US-2: Natural Language Diagnostic Querying
* **As a** Product Manager,
* **I want to** ask *"Why did conversion rate drop in September compared to August?"*,
* **So that** the AI identifies the exact segments or features responsible rather than giving generic advice.
* **Acceptance Criteria:**
  * Supervisor agent decomposes the query into date filtering, group aggregation by dimension (e.g., channel, device), and statistical t-test.
  * UI displays real-time execution steps as agents invoke tools.
  * Output clearly identifies the primary driver (e.g., "Mobile Safari conversion dropped 42%, $p < 0.001$, while Desktop remained unchanged").

### US-3: Zero-Hallucination Statistical Evidence
* **As a** BI Lead,
* **I want to** verify the mathematical proof behind an insight,
* **So that** I can confidently defend the findings in an executive review.
* **Acceptance Criteria:**
  * Every insight card includes an expandable "Evidence & Proof" panel.
  * Panel displays exact sample size ($N$), test statistic ($t$, $\chi^2$, or $F$), $p$-value, and the exact Python tool parameters used.
  * No numerical value appears in the LLM text that is not present in the tool execution result JSON.

### US-4: Exportable Executive Report
* **As a** Startup Founder,
* **I want to** export the full analysis session into a branded PDF or Markdown document,
* **So that** I can share findings directly with stakeholders and investors.
* **Acceptance Criteria:**
  * Report includes Title, Executive Summary, Key Findings, Charts, Methodology, and Next Steps.
  * PDF generation renders cleanly with no clipped charts or broken formatting.

---

## 9. Success Metrics & Key Performance Indicators (KPIs)

| Metric | Target (MVP) | Measurement Methodology |
| :--- | :--- | :--- |
| **Calculation Accuracy** | **100.0%** | Zero discrepancies between LLM output figures and Python tool return values across automated test suites. |
| **Analysis Latency** | **< 30 seconds** | Median duration from query submission to complete insight generation for 100k row datasets. |
| **Quality Profiling Speed** | **< 4 seconds** | Median duration from upload completion to profile screen display. |
| **Query Success Rate** | **> 92%** | Percentage of queries completed without unhandled exceptions or retry failures. |
| **Insight Actionability Rating** | **> 4.5 / 5.0** | User feedback rating on recommendations usefulness during beta trials. |
| **Report Export Rate** | **> 40%** | Percentage of completed analyses resulting in a PDF/Markdown download. |

---

## 10. Assumptions, Risks & Mitigation Strategies

| Risk / Assumption | Severity | Likelihood | Mitigation Strategy |
| :--- | :---: | :---: | :--- |
| **Assumption:** Datasets have clean headers and tabular format. | Medium | High | Implement robust parsing fallback with encoding detection (`chardet`), header inference, and whitespace stripping. |
| **Risk: LLM Tool Selection Error:** Agent selects incorrect columns or inappropriate statistical test. | High | Medium | Enforce strict Pydantic schemas, column name fuzzy-matching, and supervisor validation gates before tool invocation. |
| **Risk: Large Dataset Memory Overhead:** Uploading large CSVs causes Out-Of-Memory (OOM) on backend server. | High | Low | Enforce 50MB file size limit for MVP; use streaming file upload and chunked Polars/Pandas reading. |
| **Risk: LLM Rate Limiting or Provider Outage:** Provider API fails during multi-step graph execution. | Medium | Medium | Support interchangeable LLM providers (OpenAI, Anthropic, Gemini) via unified LangChain interface with automatic exponential backoff retry. |
| **Risk: Over-interpretation of Spurious Correlations:** System misleads users into thinking correlation implies causation. | High | Medium | Enforce system-prompt guardrails and UI warning badges explicitly distinguishing correlation from causal claims. |

---

## 11. MVP Acceptance Criteria Checklist

- [ ] Users can upload `.csv` and `.xlsx` files up to 50MB.
- [ ] Automated profiling generates summary statistics, missing values, and data health scores.
- [ ] Users can submit natural language analytical queries against the uploaded dataset.
- [ ] LangGraph supervisor plans and coordinates multi-agent execution transparently.
- [ ] All numerical metrics are computed via deterministic Python tool functions.
- [ ] Results stream to the frontend in real time via WebSockets.
- [ ] Interactive charts (Bar, Line, Scatter, Boxplot, Heatmap) render with Recharts.
- [ ] Every insight is backed by verified evidence, sample counts, and statistical validity checks.
- [ ] Analysis sessions can be exported to clean Markdown and PDF reports.
