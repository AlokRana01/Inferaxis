# Inferaxis

### Autonomous AI for Evidence-Based Data Intelligence

> **Status: 🚧 Under Active Development**

Inferaxis is an AI-powered autonomous data intelligence platform designed to transform natural-language questions and raw datasets into **evidence-backed analysis, visualizations, insights, and recommendations**.

The project combines **Agentic AI, Data Science, Machine Learning, Statistical Analysis, Explainable AI, and Full-Stack Engineering** into a single production-oriented platform.

Inferaxis is currently in the early development stage. The architecture and core product are being built incrementally, with the goal of developing a complete AI-powered data scientist rather than a simple chatbot.

---

## What is Inferaxis?

Traditional AI data analysis can follow a simple pattern:

```text
Dataset → LLM → Answer
```

Inferaxis is being designed around a more rigorous Data Science workflow:

```text
Dataset
   ↓
Data Understanding
   ↓
Data Quality
   ↓
Analysis Planning
   ↓
Controlled Python Tools
   ↓
Statistical Validation
   ↓
Evidence
   ↓
Insights
   ↓
Visualization
   ↓
Recommendations
   ↓
Report
```

The core principle is:

> **The AI reasons about the analysis. Python performs the analysis.**

The LLM should determine what needs to be investigated, which tools should be used, which columns are relevant, and how the results should be interpreted.

Actual calculations, statistical tests, data processing, machine learning, and visualization preparation are performed by controlled Python tools.

---

# Vision

Inferaxis aims to become an **AI Data Scientist that can investigate data rather than simply talk about it.**

A user should eventually be able to upload a dataset and ask:

> **"Why did revenue decrease in Q3?"**

Instead of immediately generating an answer, Inferaxis should:

1. Understand the dataset.
2. Inspect its structure and quality.
3. Understand the user's question.
4. Create an analysis plan.
5. Select appropriate analytical tools.
6. Perform exploratory analysis.
7. Perform relevant statistical analysis.
8. Generate appropriate visualizations.
9. Investigate potential drivers.
10. Validate important findings.
11. Build evidence-backed insights.
12. Generate recommendations.
13. Present the analysis interactively.
14. Generate a professional report.

---

# Core Architecture

```text
                         ┌──────────────────────┐
                         │         User         │
                         │ Dataset + Question   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Supervisor Agent    │
                         │ Analysis Planning    │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
      │ Data         │      │ Data Quality │      │ EDA /        │
      │ Agent        │      │ Agent        │      │ Statistics   │
      └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   ▼
                        ┌──────────────────────┐
                        │ Controlled Python    │
                        │ Data Science Tools   │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ Evidence & Results   │
                        └──────────┬───────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                ▼                  ▼                  ▼
         ┌────────────┐    ┌────────────┐    ┌──────────────┐
         │ Insights   │    │ Charts     │    │ Recommen-    │
         │            │    │            │    │ dations      │
         └──────┬─────┘    └──────┬─────┘    └──────┬───────┘
                └──────────────────┼──────────────────┘
                                   ▼
                        ┌──────────────────────┐
                        │ React + TypeScript   │
                        │ Analysis Workspace   │
                        └──────────────────────┘
```

---

# Why Inferaxis?

Inferaxis is intentionally different from a generic AI chatbot.

The platform is being designed around five principles:

### 1. Evidence Before Conclusions

Important findings should be supported by actual analytical results.

### 2. LLMs Should Not Invent Numbers

The LLM should not calculate numerical results itself.

Python tools should perform the calculations.

### 3. Controlled Tool Execution

Agents should interact with predefined Data Science tools instead of executing arbitrary Python code.

### 4. Transparent Analysis

The system should make the analytical process inspectable.

```text
Question
   ↓
Analysis Plan
   ↓
Agent
   ↓
Tool
   ↓
Result
   ↓
Evidence
   ↓
Insight
```

### 5. Correlation Is Not Causation

Inferaxis should distinguish between:

* Observation
* Correlation
* Statistical association
* Prediction
* Causal claims

Causal claims should only be made when the methodology provides appropriate support.

---

# Main Product Modes

## AI Data Analyst

The first major mode focuses on autonomous data analysis.

Example questions:

```text
Why did sales decrease?

Which region performs best?

Which products generate the most revenue?

What factors are associated with customer churn?

Which customer segment has the highest value?

What caused the increase in operating costs?

Are there unusual patterns in the dataset?

What are the strongest relationships between variables?
```

The system should determine which analyses are relevant to the question instead of running every possible analysis.

---

## AI ML Scientist

A second mode will extend Inferaxis into machine learning.

Planned workflow:

```text
Dataset
   ↓
Data Quality
   ↓
Target Detection
   ↓
Feature Engineering
   ↓
Train/Test Split
   ↓
Model Selection
   ↓
Model Training
   ↓
Model Comparison
   ↓
Evaluation
   ↓
Explainability
   ↓
Prediction
```

Potential models include:

* Linear Regression
* Logistic Regression
* Decision Tree
* Random Forest
* Gradient Boosting
* XGBoost
* Other appropriate Scikit-learn models

Planned explainability capabilities:

* SHAP
* Feature Importance
* Partial Dependence where appropriate

---

# Multi-Agent System

Inferaxis will use a specialized multi-agent architecture orchestrated through **LangGraph**.

| Agent                    | Responsibility                                                   |
| ------------------------ | ---------------------------------------------------------------- |
| Supervisor Agent         | Understands the request and orchestrates the workflow            |
| Data Understanding Agent | Understands dataset structure and schema                         |
| Data Quality Agent       | Detects missing values, duplicates, inconsistencies and outliers |
| EDA Agent                | Performs exploratory analysis                                    |
| Statistical Agent        | Performs appropriate statistical analysis                        |
| Visualization Agent      | Selects appropriate visualizations                               |
| Insight Agent            | Converts analytical results into evidence-backed findings        |
| Recommendation Agent     | Converts findings into practical recommendations                 |
| Report Agent             | Generates a professional analysis report                         |

The architecture may evolve as development progresses.

---

# Controlled Data Science Engine

Agents will interact with controlled Python tools.

## Data Tools

```python
load_dataset()
inspect_dataset()
detect_data_types()
profile_dataset()
calculate_missing_values()
detect_duplicates()
detect_outliers()
```

## Analysis Tools

```python
descriptive_statistics()
group_analysis()
correlation_analysis()
trend_analysis()
segmentation_analysis()
```

## Statistical Tools

```python
pearson_test()
spearman_test()
t_test()
chi_square_test()
anova_test()
```

## Visualization Tools

```python
create_bar_chart()
create_line_chart()
create_histogram()
create_boxplot()
create_scatterplot()
create_heatmap()
```

## Machine Learning Tools

```python
train_model()
compare_models()
evaluate_model()
feature_importance()
shap_analysis()
```

The exact tool interface and implementation will be established during development.

---

# Technology Stack

## Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* shadcn/ui
* TanStack Query
* Zustand
* React Router
* Recharts / Plotly.js

## Backend

* Python
* FastAPI
* Pydantic
* Uvicorn
* SQLAlchemy

## Agentic AI

* LangGraph
* LLM tool/function calling
* Configurable LLM provider

Example environment configuration:

```env
LLM_PROVIDER=
LLM_API_KEY=
LLM_MODEL=
```

API credentials will never be hard-coded.

## Data Science & Machine Learning

* Pandas
* NumPy
* SciPy
* Scikit-learn
* XGBoost
* SHAP

## Database

* PostgreSQL

## Communication

* REST APIs
* WebSockets

## Engineering

* Git
* Docker
* Automated testing
* Logging
* API documentation

---

# Planned User Interface

Inferaxis will use a modern web-based interface rather than Streamlit.

## Dashboard

Planned features:

* Recent datasets
* Recent analyses
* Analysis statistics
* Quick Start
* Dataset history

## Dataset Workspace

Users will eventually be able to:

* Upload CSV files
* Preview datasets
* Inspect columns
* View data types
* View missing values
* View quality metrics
* Explore dataset statistics

## AI Analysis Workspace

The main workspace will contain:

### Question Input

```text
Why did revenue decrease in Q3?
```

### Agent Activity

```text
AI Analysis

✓ Supervisor Agent
✓ Data Understanding Agent
✓ Data Quality Agent
✓ EDA Agent
⏳ Statistical Analysis Agent
○ Visualization Agent
○ Insight Agent
○ Recommendation Agent
○ Report Agent
```

Agent progress will eventually be streamed to the frontend through WebSockets.

### Analysis Results

Results will include:

* Findings
* Charts
* Statistical evidence
* Supporting metrics
* Confidence
* Recommendations

---

# Example Analysis

Suppose a user uploads:

```text
sales_data.csv
```

and asks:

> **Why did revenue decrease in Q3?**

Inferaxis could create an analytical workflow:

```text
User Question
      ↓
Supervisor
      ↓
Data Understanding
      ↓
Data Quality
      ↓
EDA
      ↓
Statistical Analysis
      ↓
Visualization
      ↓
Evidence
      ↓
Insight
      ↓
Recommendation
      ↓
Report
```

The final result might contain evidence such as:

```text
Q3 Revenue Analysis

Revenue Change:
-18.4%

Observed Contributors:

West Region
Revenue: -27%

Product Category A
Revenue: -31%

Average Order Quantity
Change: -14%

Trend:
The decline began in July.

Supporting Evidence:
Multiple independent analyses support the finding.

Recommended Investigation:
Review inventory availability, pricing,
and promotional changes in the West region
during July–September.
```

These numbers are only an example.

In the actual application, numerical values must always come from the dataset and controlled Python analysis tools.

---

# MVP

The first usable MVP will intentionally focus on the core experience.

## Frontend

* React + TypeScript
* Dashboard
* CSV upload
* Dataset preview
* Question input
* Analysis workspace
* Agent progress
* Findings
* Charts

## Backend

* FastAPI
* Dataset upload API
* Dataset profiling
* Data quality analysis
* Analysis API

## AI

* LangGraph
* Supervisor Agent
* Data Understanding Agent
* Data Quality Agent
* EDA Agent
* Insight Agent

## Data Science

* Pandas
* NumPy
* SciPy
* Basic visualization

## Database

* PostgreSQL

### MVP intentionally excludes

* Advanced authentication
* Enterprise features
* Complex deployment
* Full ML automation
* Every possible statistical test
* All future integrations

The goal is to build the **core experience first**.

---

# Development Roadmap

Inferaxis will be developed incrementally.

```text
Phase 1
Project Foundation
       ↓
Phase 2
Dataset Management
       ↓
Phase 3
Data Quality Engine
       ↓
Phase 4
First AI Agents
       ↓
Phase 5
EDA + Statistics + Visualization
       ↓
Phase 6
Evidence & Insight Engine
       ↓
Phase 7
React AI Workspace
       ↓
Phase 8
ML Scientist Mode
       ↓
Phase 9
Reporting
       ↓
Phase 10
Production Polish
```

## Phase 1 — Project Foundation

* Git repository
* React + TypeScript + Vite
* Tailwind CSS
* FastAPI
* PostgreSQL
* Environment configuration
* Frontend/backend connection

**Goal:** React successfully communicates with FastAPI.

---

## Phase 2 — Dataset Management

* CSV upload
* File validation
* Dataset storage
* Dataset preview
* Schema detection
* Basic profiling

**Goal:** Users can upload and inspect a dataset.

---

## Phase 3 — Data Quality Engine

* Missing values
* Duplicate detection
* Data types
* Inconsistent categories
* Outlier detection
* Quality score

**Goal:** Produce a reliable dataset-quality report.

---

## Phase 4 — First AI Agents

Implement:

* Supervisor Agent
* Data Understanding Agent
* Data Quality Agent

**Goal:** Connect LLM reasoning with controlled Python tools.

---

## Phase 5 — EDA & Statistical Intelligence

Add:

* EDA Agent
* Statistical Agent
* Visualization Agent

**Goal:** Inferaxis can automatically investigate a dataset.

---

## Phase 6 — Evidence & Insight Engine

Add:

* Insight Agent
* Root Cause Analysis
* Evidence tracking
* Confidence scoring

**Goal:** Produce evidence-backed findings.

---

## Phase 7 — React AI Workspace

Build the complete analysis interface.

Include:

* User question
* Agent activity
* Charts
* Findings
* Evidence
* Recommendations

---

## Phase 8 — ML Scientist Mode

Add:

* Target detection
* Feature engineering
* Model selection
* Model training
* Evaluation
* SHAP
* Predictions

---

## Phase 9 — Reporting

Add:

* Professional reports
* PDF export
* Analysis history

---

## Phase 10 — Production Polish

Potential additions:

* Authentication
* Docker
* Testing
* Logging
* Security hardening
* API documentation
* Deployment
* Architecture documentation
* Demo datasets
* Screenshots

---

# Planned Project Structure

```text
inferaxis/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── layouts/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── store/
│   │   ├── types/
│   │   └── utils/
│   │
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── agents/
│   │   ├── tools/
│   │   ├── workflows/
│   │   ├── models/
│   │   ├── database/
│   │   ├── services/
│   │   ├── config/
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── .env.example
│
├── data/
│
├── tests/
│
├── docs/
│   └── PROJECT_MASTER_CONTEXT.md
│
├── docker-compose.yml
│
├── README.md
│
└── .gitignore
```

The structure is a starting point and may evolve as the architecture becomes more mature.

---

# API Architecture

Planned API structure:

## Dataset

```http
POST /api/datasets/upload
GET  /api/datasets
GET  /api/datasets/{dataset_id}
```

## Analysis

```http
POST /api/analysis/start
GET  /api/analysis/{analysis_id}
GET  /api/analysis/{analysis_id}/status
GET  /api/analysis/{analysis_id}/insights
GET  /api/analysis/{analysis_id}/charts
```

## Reports

```http
POST /api/reports/{analysis_id}/generate
GET  /api/reports/{report_id}
```

The API design may change during implementation.

---

# Database

PostgreSQL will be used for persistent application data.

Planned entities include:

### Users

```text
id
name
email
created_at
```

### Datasets

```text
id
user_id
filename
size
row_count
column_count
upload_time
quality_score
```

### Analysis Jobs

```text
id
dataset_id
question
status
created_at
completed_at
```

### Agent Runs

```text
id
analysis_id
agent_name
status
started_at
completed_at
output
```

### Insights

```text
id
analysis_id
title
description
evidence
confidence
```

### Reports

```text
id
analysis_id
report_path
created_at
```

The schema will evolve with the implementation.

---

# Security

Because Inferaxis will eventually process user-uploaded datasets, security is an important part of the architecture.

Planned protections include:

* File type validation
* File size limits
* Filename sanitization
* Temporary file management
* Input validation
* CORS configuration
* Environment-based secrets
* SQL injection protection
* Resource and execution limits
* Safe analytical tool execution
* API authentication
* Protection against malicious datasets

### Important Rule

> **Inferaxis must never execute arbitrary Python code supplied by a user.**

---

# Error Handling

The application should gracefully handle:

* Invalid CSV files
* Empty datasets
* Unsupported file types
* Extremely large datasets
* Missing columns
* Corrupted data
* Unsupported statistical analysis
* Model training failures
* LLM API failures
* Agent failures
* Timeouts

Errors should be presented to users in understandable language rather than exposing raw backend exceptions.

---

# Observability

Inferaxis is intended to provide visibility into the analytical pipeline.

The system will eventually track:

```text
Analysis ID
      ↓
Agent Execution
      ↓
Tool Calls
      ↓
Execution Time
      ↓
Tool Results
      ↓
Failures
      ↓
Generated Findings
```

This will help with debugging, auditing, reproducibility, and understanding how an insight was produced.

---

# Development Principles

The following principles will guide development:

1. **Build incrementally.**
2. **Do not build the entire system at once.**
3. **React + TypeScript remains the primary frontend.**
4. **Python + FastAPI remains the backend.**
5. **Streamlit will not be used as the primary frontend.**
6. **Python performs Data Science calculations.**
7. **LLMs reason about analysis rather than inventing numerical results.**
8. **Important findings should have supporting evidence.**
9. **Correlation should not automatically be interpreted as causation.**
10. **Use Pydantic for structured backend data.**
11. **Keep frontend and backend loosely coupled through APIs.**
12. **Never hard-code API keys.**
13. **Use modular and reusable code.**
14. **Add testing progressively.**
15. **Preserve working functionality when introducing changes.**
16. **Document major architectural decisions.**
17. **Keep the project GitHub-ready throughout development.**

---

# Future Possibilities

Potential future capabilities include:

* Excel support
* SQL database analysis
* Natural-language SQL
* Multiple dataset analysis
* Automated forecasting
* Anomaly detection
* Time-series analysis
* Automated ML
* Model monitoring
* RAG over business documentation
* Team collaboration
* Role-based access
* Saved AI analyst sessions
* Scheduled analysis
* Slack/email notifications
* Cloud deployment
* Enterprise data connectors

These features are intentionally outside the initial MVP.

---

# Portfolio Objective

Inferaxis is being developed as a portfolio-level project to demonstrate the ability to move beyond notebook-based Data Science and build a complete AI-powered product.

The project aims to demonstrate:

| Area             | Technologies                  |
| ---------------- | ----------------------------- |
| Frontend         | React, TypeScript             |
| Backend          | Python, FastAPI               |
| Agentic AI       | LangGraph, LLMs, Tool Calling |
| Data Science     | Pandas, NumPy, SciPy          |
| Machine Learning | Scikit-learn, XGBoost         |
| Explainable AI   | SHAP                          |
| Database         | PostgreSQL                    |
| Communication    | REST API, WebSockets          |
| Engineering      | Docker, Testing, Git          |
| Architecture     | Multi-Agent System            |

---

# Current Status

| Component             | Status           |
| --------------------- | ---------------- |
| Product Concept       | ✅ Defined        |
| Product Name          | ✅ Inferaxis         |
| Core Architecture     | ✅ Initial design |
| GitHub Repository     | 🚧 Started       |
| Frontend              | ⏳ Not started    |
| Backend               | ⏳ Not started    |
| Database              | ⏳ Not started    |
| Agent System          | ⏳ Not started    |
| Data Science Engine   | ⏳ Not started    |
| AI Analysis Workspace | ⏳ Not started    |
| ML Scientist Mode     | ⏳ Planned        |
| Reporting             | ⏳ Planned        |
| Production Deployment | ⏳ Planned        |

> **Inferaxis is currently a work in progress and is not production-ready.**

The repository will evolve continuously as development progresses.

---

# Project Status

```text
🚧 INFERAXIS
Autonomous AI for Evidence-Based Data Intelligence

Current Stage:
Project Foundation / Initial Development

Next Milestone:
Phase 1 — Project Foundation
```

---

# Disclaimer

Inferaxis is an experimental and educational portfolio project under active development.

Architecture, features, APIs, agent responsibilities, UI design, and technology choices may change as the project evolves.

The current repository represents the **development starting point**, not a finished production application.

---

# License

License information will be added as the project reaches a stable release stage.

---

## Inferaxis

> **Autonomous AI for Evidence-Based Data Intelligence.**

Built to explore the intersection of **Agentic AI, Data Science, Machine Learning, Statistical Reasoning, Explainable AI, and Full-Stack Engineering.**
