# Software Requirements Specification (SRS)

## Project: Inferaxis — Autonomous AI for Evidence-Based Data Intelligence
**Document Version:** 1.0.0  
**Status:** Approved / Specification Baseline  
**Target Release:** MVP (Phase 1)  
**Author:** Inferaxis Systems Engineering & Architecture Group  
**Last Updated:** October 2026  

---

## 1. Introduction

### 1.1 Purpose
This document specifies the software requirements for **Inferaxis**, an autonomous AI-driven data intelligence platform. It provides a formal, testable specification of functional capabilities, non-functional constraints, data schemas, security controls, and error-handling behaviors for developers, testers, and product stakeholders.

### 1.2 System Scope
Inferaxis ingests tabular data files (CSV, XLSX), runs automated data profiling and quality assessments, orchestrates a multi-agent analytical pipeline using **LangGraph**, executes mathematical and statistical operations through controlled Python tools, and renders evidence-backed insights, interactive visualizations, and exportable reports in a modern React web application.

### 1.3 Key Architectural Axiom
> **"The AI reasons about the analysis; controlled Python tools execute the analysis."**  
> Under no circumstances shall an LLM generate or extrapolate analytical numbers without direct derivation from a vetted Python tool execution payload.

---

## 2. User Roles & Access Control

Inferaxis implements Role-Based Access Control (RBAC) to govern workspace data and analysis execution.

| Role Code | Role Name | Description | Key Permissions |
| :--- | :--- | :--- | :--- |
| **ROLE_VIEWER** | Viewer / Stakeholder | Read-only access to published analyses and shared executive reports. | View datasets, view analysis sessions, interact with charts, download reports. Cannot upload datasets or initiate new AI queries. |
| **ROLE_ANALYST** | Analyst / Member | Standard analytical practitioner. | Upload datasets, run profiling, submit natural-language queries, rerun agent plans, export reports, manage personal sessions. |
| **ROLE_ADMIN** | Workspace Admin | Manager of workspace settings, team members, and data retention. | Manage workspace users, delete datasets, view audit logs, configure LLM provider API keys, manage rate limits. |
| **ROLE_SYSADMIN** | System Administrator | Platform-level engineer responsible for infrastructure and system health. | Monitor system metrics, manage database migrations, inspect raw tool execution logs, toggle feature flags. |

### 2.1 Permissions Matrix

| Functional Action | Viewer | Analyst | Admin | SysAdmin |
| :--- | :---: | :---: | :---: | :---: |
| Upload Dataset (CSV/XLSX) | ❌ | ✅ | ✅ | ✅ |
| Delete Dataset | ❌ | Own Only | ✅ | ✅ |
| Execute Natural-Language Query | ❌ | ✅ | ✅ | ✅ |
| View Agent Execution Step Logs | ✅ | ✅ | ✅ | ✅ |
| Export Report (Markdown/PDF) | ✅ | ✅ | ✅ | ✅ |
| Configure LLM API Keys / Providers | ❌ | ❌ | ✅ | ✅ |
| Inspect Server Tool Logs & Metrics | ❌ | ❌ | ❌ | ✅ |

---

## 3. Business Rules

* **BR-001 (Deterministic Calculation):** All mathematical calculations, aggregations, percentages, hypothesis tests, and correlation coefficients presented to the user must originate from Python execution payloads. LLMs are prohibited from performing manual arithmetic.
* **BR-002 (Controlled Tool Execution):** Agents can only call pre-registered, sandboxed Python functions. Dynamic string code generation (`eval()`, `exec()`, arbitrary bash execution) is strictly disallowed in production runtime.
* **BR-003 (Causation Guardrail):** The system must never assert a causal claim unless explicitly backed by randomized controlled trial (A/B test) data or verified causal inference methodology. Observational relationships must be labeled as "associated with" or "correlated with".
* **BR-004 (Statistically Significant Threshold):** Any insight asserting a "difference" or "trend" must report the $p$-value. Differences with $p \ge 0.05$ must be explicitly labeled as "statistically insignificant" or "inconclusive".
* **BR-005 (Tenant Data Isolation):** Datasets and analysis sessions belonging to Workspace $A$ must never be accessible, readable, or leaked to Workspace $B$.
* **BR-006 (Zero Data Retention with Third-Party LLMs):** User data sent in prompts must be restricted to schema names, column summaries, and tool summary aggregates. Raw row-level microdata must never be piped into external LLM prompts.

---

## 4. Functional Requirements

### 4.1 Module 1: Data Ingestion & Storage (FR-INGEST)

* **FR-INGEST-001 (File Upload Support):** The system shall accept tabular file uploads in `.csv` and `.xlsx` formats up to 50MB in file size.
* **FR-INGEST-002 (Encoding & Delimiter Inference):** The system shall automatically detect character encodings (UTF-8, ISO-8859-1, Windows-1252) and delimiters (comma, semicolon, tab, pipe) using `chardet` and file sniffers.
* **FR-INGEST-003 (Sanitized Storage):** Uploaded files shall be stored in a secured file store (local volume or S3-compatible bucket) using a randomized UUID filename with original filename preserved in metadata.
* **FR-INGEST-004 (Schema Ingestion):** Upon upload, the system shall parse the first 1,000 rows to extract column names, sanitize invalid characters, and assign temporary types.

### 4.2 Module 2: Data Understanding & Quality Profiling (FR-PROFILE)

* **FR-PROFILE-001 (Semantic Type Classification):** The system shall classify each column into one of the following semantic types:
  * `Numeric Continuous` (floats, prices, ratios)
  * `Numeric Discrete` (counts, ranks, small integer spans)
  * `Categorical Nominal` (labels, country codes, names)
  * `Categorical Ordinal` (ratings, tiered stages)
  * `Datetime / Timestamp` (ISO formats, date strings)
  * `Unique Identifier` (UUIDs, sequential primary keys)
  * `Freeform Text` (long commentary, reviews)
* **FR-PROFILE-002 (Automated Quality Metrics):** The system shall calculate:
  * Total rows and total columns
  * Null / missing value count and percentage per column
  * Duplicate row count and percentage
  * Cardinality (distinct count) per column
  * Zero-variance columns (constant values across all rows)
  * Memory footprint in megabytes
* **FR-PROFILE-003 (Outlier Profiling):** For all numeric columns, the system shall compute Interquartile Range (IQR) bounds ($Q_1 - 1.5 \times IQR$, $Q_3 + 1.5 \times IQR$) and identify outlier counts.
* **FR-PROFILE-004 (Data Health Score):** The system shall compute a weighted Data Health Score (0 to 100) based on completeness, uniqueness, and consistency.

### 4.3 Module 3: Natural Language Query & Multi-Agent Orchestration (FR-AGENT)

* **FR-AGENT-001 (Query Ingestion):** The system shall provide an input interface accepting natural language questions up to 1,000 characters.
* **FR-AGENT-002 (Supervisor Query Decomposition):** The Supervisor Agent shall analyze the question and dataset profile to formulate an `AnalysisPlan` containing:
  * Restated business objective
  * Required target columns
  * Proposed sequence of agent tasks
* **FR-AGENT-003 (LangGraph State Propagation):** The system shall execute the multi-agent graph with state passing between:
  1. `SupervisorAgent`
  2. `DataUnderstandingAgent`
  3. `DataQualityAgent`
  4. `EDAAgent`
  5. `StatisticalAgent`
  6. `VisualizationAgent`
  7. `InsightAgent`
  8. `RecommendationAgent`
  9. `ReportAgent`
* **FR-AGENT-004 (Streaming Execution Updates):** The system shall stream agent thought steps, tool selection events, and intermediate execution statuses to the frontend over WebSockets with $<200\text{ms}$ event latency.
* **FR-AGENT-005 (Tool Selection Validation):** The system shall reject any agent tool call whose arguments do not strictly validate against the tool's Pydantic model.

### 4.4 Module 4: Controlled Python Tool Execution (FR-TOOL)

* **FR-TOOL-001 (Sandboxed In-Memory Execution):** Tools shall operate on the loaded Pandas/Polars DataFrame within an isolated execution worker with strict resource ceilings (CPU 2 cores, RAM 2GB per worker).
* **FR-TOOL-002 (Descriptive Statistics Tool):** `descriptive_statistics(columns: List[str])` shall return count, mean, median, mode, standard deviation, variance, skewness, kurtosis, and quartiles.
* **FR-TOOL-003 (Group Aggregation Tool):** `group_analysis(groupby_cols: List[str], agg_col: str, agg_func: Literal['sum', 'mean', 'median', 'count', 'min', 'max'])` shall compute grouped metrics.
* **FR-TOOL-004 (Trend Analysis Tool):** `trend_analysis(date_col: str, value_col: str, interval: Literal['D', 'W', 'M', 'Q', 'Y'])` shall aggregate time series data.
* **FR-TOOL-005 (Hypothesis Testing Tools):**
  * `t_test(group_col: str, metric_col: str, group_a: str, group_b: str)`: Returns mean difference, $t$-statistic, degrees of freedom, $p$-value, and 95% confidence interval.
  * `chi_square_test(col_a: str, col_b: str)`: Returns contingency table, $\chi^2$ statistic, degrees of freedom, and $p$-value.
  * `anova_test(group_col: str, metric_col: str)`: Returns $F$-statistic, between-group variance, and $p$-value.
  * `correlation_analysis(col_a: str, col_b: str, method: Literal['pearson', 'spearman'])`: Returns correlation coefficient $r$ and two-tailed $p$-value.
* **FR-TOOL-006 (Timeout Enforcement):** Any tool execution exceeding 15 seconds shall be terminated, returning an explicit timeout error object to the calling agent.

### 4.5 Module 5: Visualization Engine (FR-VIZ)

* **FR-VIZ-001 (Declarative Chart Specification):** The Visualization Agent shall produce standardized JSON chart specifications compatible with Recharts/Plotly, defining:
  * Chart type (`bar`, `line`, `scatter`, `box`, `heatmap`, `pie`)
  * Data points array (aggregated, maximum 500 points for chart performance)
  * X-axis key, Y-axis keys, labels, colors, and formatting rules
* **FR-VIZ-002 (Visual Best Practices):** The system shall enforce visualization rules:
  * Bar charts for discrete categorical comparisons
  * Line charts for sequential temporal trends
  * Scatter plots for continuous vs. continuous correlation
  * Boxplots for distribution spread and outlier inspection

### 4.6 Module 6: Insight & Recommendation Generation (FR-INSIGHT)

* **FR-INSIGHT-001 (Evidence Anchoring):** The Insight Agent must bind every natural-language claim to a specific `evidence_id` referencing a concrete tool execution result.
* **FR-INSIGHT-002 (Format Consistency):** Insights must be generated with:
  * Direct Headline (e.g., "North America Drove 68% of Total Q3 Revenue Drop")
  * Quantitative Proof (Baseline, New Value, Absolute Change, Percentage Change)
  * Statistical Confidence Note ($p$-value or significance flag)
* **FR-INSIGHT-003 (Actionable Recommendations):** The Recommendation Agent must generate at least 2 and at most 5 concrete, prioritized business recommendations based directly on the validated insights.

### 4.7 Module 7: Reporting & Export (FR-REPORT)

* **FR-REPORT-001 (Markdown Export):** The system shall allow users to export the complete analysis session as an audited, structured Markdown document.
* **FR-REPORT-002 (PDF Export):** The system shall render a styled PDF report including branded header, executive summary, charts (rendered as vector graphics or high-res PNGs), and statistical appendix.

---

## 5. Data Requirements & Schemas

### 5.1 Relational Data Models (PostgreSQL)

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     User        │       │    Workspace    │       │     Dataset     │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (UUID, PK)   │1    * │ id (UUID, PK)   │1    * │ id (UUID, PK)   │
│ email (VARCHAR) │───────│ name (VARCHAR)  │───────│ workspace_id(FK)│
│ hashed_pw (STR) │       │ owner_id (FK)   │       │ file_name (STR) │
│ role (VARCHAR)  │       │ created_at (TS) │       │ file_path (STR) │
└─────────────────┘       └─────────────────┘       │ row_count (INT) │
                                                    │ col_count (INT) │
                                                    │ health_score(FL)│
                                                    └────────┬────────┘
                                                             │ 1
                                                             │ *
                                                    ┌────────┴────────┐
                                                    │ AnalysisSession │
                                                    ├─────────────────┤
                                                    │ id (UUID, PK)   │
                                                    │ dataset_id (FK) │
                                                    │ user_query(TEXT)│
                                                    │ status (VARCHAR)│
                                                    │ created_at (TS) │
                                                    └────────┬────────┘
                                                             │ 1
                                      ┌──────────────────────┴──────────────────────┐
                                      │ *                                           │ *
                               ┌──────┴──────────┐                           ┌──────┴──────────┐
                               │    AgentStep    │                           │  AnalysisReport │
                               ├─────────────────┤                           ├─────────────────┤
                               │ id (UUID, PK)   │                           │ id (UUID, PK)   │
                               │ session_id (FK) │                           │ session_id (FK) │
                               │ agent_name(STR) │                           │ summary (TEXT)  │
                               │ tool_name (STR) │                           │ payload (JSONB) │
                               │ tool_args(JSONB)│                           │ pdf_url (STR)   │
                               │ output (JSONB)  │                           └─────────────────┘
                               │ duration_ms(INT)│
                               └─────────────────┘
```

### 5.2 Tool Return Payload Standard (JSON Schema)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ToolExecutionResult",
  "type": "object",
  "required": ["tool_name", "status", "execution_time_ms", "data", "summary_text"],
  "properties": {
    "tool_name": { "type": "string" },
    "status": { "type": "string", "enum": ["success", "error", "timeout"] },
    "execution_time_ms": { "type": "number" },
    "data": { "type": "object" },
    "summary_text": { "type": "string" },
    "error_message": { "type": ["string", "null"] }
  }
}
```

---

## 6. Input Validations & Integrity Rules

1. **File Upload Validation:**
   * Magic bytes verification must confirm standard CSV or ZIP/Office Open XML formats.
   * Total row count cannot exceed 250,000 rows in MVP.
   * File extension must be lowercase `.csv` or `.xlsx`.
2. **Column Name Sanitization:**
   * Column names with leading/trailing whitespaces must be trimmed.
   * Special characters (`/`, `\`, `.`, `$`, `\n`) must be replaced with underscores.
   * Duplicate column names must be automatically suffixed with `_1`, `_2`.
3. **Query Text Validation:**
   * Must contain at least 5 characters and no more than 1,000 characters.
   * Must pass prompt injection sanitization filters (rejection of system prompt override instructions).

---

## 7. Authentication & Authorization

* **Auth Standard:** Stateless JWT (JSON Web Tokens) with asymmetric RS256 or HS256 encryption.
* **Token Lifespans:** Access tokens expire in 60 minutes; refresh tokens expire in 14 days.
* **Password Hashing:** Passwords must be hashed using `bcrypt` with a minimum cost factor of 12.
* **Session Transport:** Tokens delivered via `Authorization: Bearer <TOKEN>` header or secure `HttpOnly`, `SameSite=Strict` cookies.
* **WebSocket Auth:** WebSockets establish connection using ticket-based handshake or authenticated query token validated upon connection opening.

---

## 8. Error Handling & Edge Cases

| Scenario / Edge Case | System Behavior & Mitigation |
| :--- | :--- |
| **All-Null or Constant Column Selected:** | Tool raises structured validation error (`ConstantColumnError`); Supervisor agent detects error, selects alternative column, and notifies user. |
| **Zero Variance in t-test:** | System catches `ZeroDivisionError` / zero variance exception; returns note stating groups have identical distribution. |
| **Mixed-Type Column (Numbers & Strings):** | Data Understanding agent flags column; coerces invalid values to `NaN` or treats column as categorical with explicit warning log. |
| **LLM Rate-Limit / Quota Exhaustion (429):** | Exponential backoff retry handler (3 attempts: 2s, 4s, 8s). If persistent, gracefully switches to configured fallback LLM provider. |
| **WebSocket Connection Disconnect:** | Frontend maintains client-side reconnect loop (up to 5 attempts). Server buffers state updates in Redis channel keyed by `session_id`. |
| **Out-of-Memory during Aggregation:** | Subprocess worker terminates safely with memory error code; main FastAPI service remains unaffected and returns user-friendly capacity warning. |

---

## 9. Security Requirements

* **SEC-001 (Zero Arbitrary Code):** Python tool calling must use strict function signatures; no dynamic code generators (`eval`, `subprocess`, `os.system`) are allowed in the tool execution layer.
* **SEC-002 (Prompt Injection Resistance):** Agent system prompts must be separated from user input using delimited data brackets and structured JSON schemas.
* **SEC-003 (Credential Isolation):** All LLM provider keys and database credentials must be loaded via encrypted environment variables (`.env`) and never logged or exposed to the client.
* **SEC-004 (CORS Configuration):** Cross-Origin Resource Sharing (CORS) must be restricted to verified client origins. Wildcard `*` is prohibited in staging and production.
* **SEC-005 (At-Rest and In-Transit Encryption):** Datasets at rest must be encrypted via AES-256; all network communications must strictly require TLS 1.3 (HTTPS / WSS).

---

## 10. Performance & Scalability Requirements

* **PERF-001 (Profiling Latency):** 95th percentile latency for profiling a 50MB / 100k row dataset shall not exceed **4.0 seconds**.
* **PERF-002 (Tool Latency):** Individual statistical tool execution (t-test, correlation, aggregation) on 100k rows shall not exceed **800ms**.
* **PERF-003 (Total Query Response Time):** Complete multi-agent analysis loop (Supervisor -> Tools -> Insights -> Visualizations) shall complete within **30 seconds** for 90% of requests.
* **PERF-004 (Concurrent Queries):** The backend shall support at least 25 concurrent active analysis sessions per backend instance without socket starvation or memory degradation.
* **PERF-005 (Frontend Responsiveness):** Web UI time to interactive (TTI) shall be $< 1.5$ seconds; chart re-rendering upon filter change shall execute at 60fps ($< 16\text{ms}$).

---

## 11. Software Acceptance Criteria (Testable Verification)

1. **FR-INGEST Verification:** Upload 20 disparate CSV and XLSX files containing varied encodings, delimiters, and missing values. 100% must parse successfully or report explicit line-error diagnostics.
2. **BR-001 Verification:** Execute 100 test queries. Compare every numeric value in the final report against the tool output JSON. Discrepancy rate must be exactly **0.00%**.
3. **FR-TOOL Statistical Correctness:** Benchmark Python tool statistical results against standard R / SciPy reference outputs. Numerical tolerance must be $\le 10^{-6}$.
4. **SEC-001 Verification:** Run security pen-test attempting prompt injection, SQL injection, and path traversal via file upload. Zero vulnerabilities allowed.
5. **Load Test Verification:** Run Locust load test simulating 25 concurrent users executing simultaneous queries; error rate must remain below 1.0%.
