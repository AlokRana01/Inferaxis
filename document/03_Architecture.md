# System Architecture Document (SAD)

## Project: Inferaxis — Autonomous AI for Evidence-Based Data Intelligence
**Document Version:** 1.0.0  
**Status:** Approved Architecture Baseline  
**Target Release:** MVP (Phase 1)  
**Author:** Inferaxis Core Engineering & Infrastructure Team  
**Last Updated:** October 2026  

---

## 1. Architectural Overview & Design Principles

Inferaxis is engineered as an asynchronous, event-driven, multi-tier system that decouples **high-level probabilistic reasoning** (LLM-based multi-agent orchestration) from **deterministic quantitative computation** (sandboxed Python Data Science tools).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          HIGH-LEVEL SYSTEM CONTOUR                          │
│                                                                             │
│   [ Client Browser ]                                                        │
│           │                                                                 │
│           ▼ (HTTPS / WSS)                                                   │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Reverse Proxy / API Gateway (Nginx / Caddy)                         │   │
│   └───────────────────┬─────────────────────────────────────────────────┘   │
│                       │                                                     │
│       ┌───────────────┴───────────────┐                                     │
│       ▼                               ▼                                     │
│   [ React + Vite SPA ]         [ FastAPI Asynchronous Backend ]             │
│   • TypeScript                 • REST Endpoints & WebSocket Server          │
│   • Zustand + TanStack Query   • Pydantic v2 Schema Validation              │
│   • Recharts Studio            • SQLAlchemy 2.0 Async ORM                   │
│                                       │                                     │
│                      ┌────────────────┴────────────────┐                    │
│                      ▼                                 ▼                    │
│              [ LangGraph Engine ]              [ Storage Subsystem ]        │
│              • Supervisor Graph                • PostgreSQL 16 (Metadata)   │
│              • Sub-Agent State Machine         • Redis 7 (Pub/Sub & Cache)  │
│              • Controlled Tool Runner          • Local/S3 Dataset Storage   │
│                      │                                                      │
│                      ▼                                                      │
│              [ Controlled Python Tools ]                                    │
│              • Pandas / NumPy / SciPy                                       │
│              • Statsmodels / Scikit-learn                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core Architectural Principles:
1. **Separation of Reasoning and Computation:** The LLM decides *what* to analyze and *which* tools to invoke. Python scripts perform *all* mathematical calculations, aggregations, statistical tests, and chart binning.
2. **Controlled Tool Invocations (Zero `eval()`):** The system strictly forbids running arbitrary user or LLM code. All operations execute through pre-defined, typed, and sandboxed functional tools.
3. **Reactive Real-Time Streaming:** The multi-agent workflow communicates intermediate agent deliberations and tool results to the client via WebSockets, eliminating user waiting anxiety.
4. **Stateless Scalability:** The backend API and LangGraph execution nodes are stateless; all session states reside in PostgreSQL and Redis.
5. **Practicality Over Over-Engineering:** Avoid heavy distributed clusters (e.g., Spark, Kubernetes) for MVP; prioritize high-throughput async Python, Polars/Pandas multi-threading, and clean containerized Docker services.

---

## 2. Technology Stack Selection

| Component Layer | Technology | Version | Rationale & Selection Criteria |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | **React** + **TypeScript** | React 18.3, TS 5.4 | Industry-standard developer experience, type safety, rich ecosystem for data visualization. |
| **Build Tool** | **Vite** | 5.x | Ultra-fast HMR (Hot Module Replacement), optimized ES-module production builds. |
| **UI Styling** | **Tailwind CSS** + **shadcn/ui** | Tailwind 3.4 | Accessible, themeable UI components with zero runtime overhead and modern dark-mode aesthetics. |
| **State Management** | **Zustand** + **TanStack Query** | Zustand 4.5, Query 5.x | TanStack Query manages server cache and async fetching; Zustand handles local workspace UI state. |
| **Data Visualization** | **Recharts** + **Plotly.js** | Recharts 2.12 | Recharts provides declarative, responsive SVG charts; Plotly handles advanced statistical boxplots and heatmaps. |
| **Backend API** | **FastAPI** | 0.111+ | High-performance asynchronous Python framework, native OpenAPI schema generation, Pydantic v2 validation. |
| **Async Server** | **Uvicorn** / **Gunicorn** | Uvicorn 0.30+ | ASGI production server supporting async WebSocket connections and high concurrent throughput. |
| **Agentic Framework** | **LangGraph** | 0.0.60+ | Graph-based stateful multi-agent orchestration with conditional branching, cyclic loops, and checkpointing. |
| **LLM Provider Abstraction**| **LangChain Core** | 0.2+ | Seamless switching between OpenAI (GPT-4o), Anthropic (Claude 3.5 Sonnet), and Google (Gemini 1.5 Pro). |
| **Data Science Engine** | **Pandas**, **NumPy**, **SciPy** | Modern 2.x | Benchmark libraries for tabular manipulations, linear algebra, and hypothesis testing. |
| **Relational Database** | **PostgreSQL** | 16-alpine | ACID-compliant relational storage for users, datasets, session metadata, tool logs, and reports. |
| **ORM / Migration** | **SQLAlchemy** + **Alembic** | SQLAlchemy 2.0 (asyncpg) | Fully async database access with type annotations and automated migration management. |
| **Event Broker / Cache** | **Redis** | 7-alpine | In-memory message bus for WebSocket streaming pub/sub and LLM prompt response caching. |
| **Containerization** | **Docker** & **Docker Compose** | 24+ | Reproducible, cross-platform local development and single-command deployment. |

---

## 3. System Component Architecture

```
                                  ┌───────────────────────────┐
                                  │      Client (Browser)     │
                                  │   React 18 + TypeScript   │
                                  └─────────────┬─────────────┘
                                                │
                          REST (HTTPS)          │          WebSockets (WSS)
                     ┌──────────────────────────┼──────────────────────────┐
                     │                          │                          │
                     ▼                          ▼                          ▼
        ┌─────────────────────────┐┌─────────────────────────┐┌─────────────────────────┐
        │   Dataset Ingestion     ││   Session & Query API   ││  Real-Time Stream Hub   │
        │   POST /api/v1/datasets ││   POST /api/v1/queries  ││  WS /ws/analysis/{id}   │
        └────────────┬────────────┘└────────────┬────────────┘└────────────┬────────────┘
                     │                          │                          │
                     ▼                          ▼                          ▼
  ┌───────────────────────────────────────────────────────────────────────────────────────┐
  │                              FASTAPI BACKEND CORE                                      │
  │  ┌───────────────────────┐  ┌────────────────────────┐  ┌──────────────────────────┐  │
  │  │ Pydantic Validation   │  │ Auth Middleware (JWT)  │  │ Background Tasks Manager │  │
  │  └───────────────────────┘  └────────────────────────┘  └──────────────────────────┘  │
  └──────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │
                                             ▼
  ┌───────────────────────────────────────────────────────────────────────────────────────┐
  │                            LANGGRAPH MULTI-AGENT RUNTIME                              │
  │                                                                                       │
  │                 ┌─────────────────────────────────────────────────┐                   │
  │                 │                Supervisor Agent                 │                   │
  │                 │    (Question Decomposition & Plan Graph)        │                   │
  │                 └────────────────────────┬────────────────────────┘                   │
  │                                          │                                            │
  │        ┌───────────────────┬─────────────┴───────┬───────────────────┐                │
  │        ▼                   ▼                     ▼                   ▼                │
  │  ┌───────────┐       ┌───────────┐         ┌───────────┐       ┌───────────┐          │
  │  │ Data      │       │ Data      │         │ EDA &     │       │ Insight & │          │
  │  │ Profiler  │       │ Quality   │         │ Stats     │       │ Report    │          │
  │  │ Agent     │       │ Agent     │         │ Agent     │       │ Agent     │          │
  │  └─────┬─────┘       └─────┬─────┘         └─────┬─────┘       └─────┬─────┘          │
  │        │                   │                     │                   │                │
  │        └───────────────────┼─────────────────────┼───────────────────┘                │
  │                            ▼                     │                                    │
  │            ┌───────────────────────────────┐     │                                    │
  │            │ Controlled Python Tool Runner │     │                                    │
  │            └───────────────┬───────────────┘     │                                    │
  │                            │                     │                                    │
  └────────────────────────────┼─────────────────────┼────────────────────────────────────┘
                               │                     │
                               ▼                     ▼
                 ┌────────────────────────┐   ┌────────────────────────┐
                 │ Storage & Database     │   │ Event Bus & Cache      │
                 │ • PostgreSQL 16        │   │ • Redis 7 Pub/Sub      │
                 │ • Local File Store     │   │ • LLM Response Cache   │
                 └────────────────────────┘   └────────────────────────┘
```

---

## 4. Multi-Agent Orchestration Flow (LangGraph)

The analytical journey is governed by a directed acyclic graph (DAG) with feedback loops compiled in **LangGraph**.

```mermaid
graph TD
    Start([User Question + Dataset]) --> Sup[Supervisor Agent]
    Sup --> Plan{Generate Analysis Plan}
    Plan --> DataCheck[Data Understanding & Quality Agent]
    DataCheck --> QualityOK{Data Quality Sufficient?}
    
    QualityOK -- No --> CleanWarn[Issue Quality Warning / Filter Step]
    CleanWarn --> EDA[EDA Agent: Aggregations & Distribution]
    QualityOK -- Yes --> EDA
    
    EDA --> ToolEDA[Execute Controlled EDA Tools]
    ToolEDA --> StatAgent[Statistical Agent]
    
    StatAgent --> ToolStat[Execute Hypothesis Tests & Correlation]
    ToolStat --> VizAgent[Visualization Agent]
    
    VizAgent --> ToolViz[Generate Declarative Chart Specs]
    ToolViz --> InsightAgent[Insight Agent: Evidence Synthesis]
    
    InsightAgent --> RecAgent[Recommendation Agent]
    RecAgent --> RepAgent[Report Agent: Final Summary]
    RepAgent --> End([WebSocket Stream Final Payload])
```

### Agent State Schema:
```python
class InferaxisAnalysisState(TypedDict):
    session_id: str
    user_query: str
    dataset_id: str
    dataset_schema: Dict[str, Any]
    data_quality_report: Dict[str, Any]
    analysis_plan: List[Dict[str, Any]]
    active_agent: str
    executed_tools: List[Dict[str, Any]]
    statistical_findings: List[Dict[str, Any]]
    chart_specifications: List[Dict[str, Any]]
    synthesized_insights: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    executive_report_markdown: str
    error: Optional[str]
```

---

## 5. Controlled Python Tool Harness

To maintain zero hallucination, LLM agents do not write and execute arbitrary Python strings. Instead, they interact with a pre-registered tool harness:

```python
# Architecture Concept: Typed Controlled Tool Registry
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class TTestInput(BaseModel):
    group_col: str = Field(description="Column defining binary groups")
    metric_col: str = Field(description="Continuous metric column to compare")
    group_a: str = Field(description="Value for first group")
    group_b: str = Field(description="Value for second group")

class ToolExecutionResult(BaseModel):
    tool_name: str
    status: Literal["success", "error"]
    execution_time_ms: float
    data: dict
    summary_text: str

def execute_t_test(df: pd.DataFrame, params: TTestInput) -> ToolExecutionResult:
    # 1. Clean missing values for target columns
    sub_df = df[[params.group_col, params.metric_col]].dropna()
    a_vals = sub_df[sub_df[params.group_col] == params.group_a][params.metric_col]
    b_vals = sub_df[sub_df[params.group_col] == params.group_b][params.metric_col]
    
    # 2. Perform independent two-sample t-test via scipy
    t_stat, p_val = scipy.stats.ttest_ind(a_vals, b_vals, equal_var=False)
    
    # 3. Return strictly structured payload
    return ToolExecutionResult(
        tool_name="t_test",
        status="success",
        execution_time_ms=12.4,
        data={
            "t_statistic": float(t_stat),
            "p_value": float(p_val),
            "mean_a": float(a_vals.mean()),
            "mean_b": float(b_vals.mean()),
            "count_a": int(len(a_vals)),
            "count_b": int(len(b_vals)),
            "is_significant_95": bool(p_val < 0.05)
        },
        summary_text=f"Group {params.group_a} mean={a_vals.mean():.2f} vs {params.group_b} mean={b_vals.mean():.2f}, p={p_val:.4e}"
    )
```

---

## 6. Data Flow Architecture

The lifecycle of an analysis request proceeds across 6 distinct phases:

1. **Ingest Phase:** User uploads `sales_q3.csv` through the React UI $\rightarrow$ Sent via `POST /api/v1/datasets/upload` $\rightarrow$ FastAPI saves file to disk/S3 $\rightarrow$ Spawns worker to parse metadata and calculate baseline profile $\rightarrow$ Profile returned to UI.
2. **Inquiry Phase:** User types *"Why did sales drop in the East region?"* $\rightarrow$ UI dispatches request via `POST /api/v1/analysis/start` $\rightarrow$ Session record created in PostgreSQL with status `RUNNING` $\rightarrow$ Client opens WebSocket connection to `/ws/analysis/{session_id}`.
3. **Planning Phase:** Supervisor Agent inspects user question and column schemas $\rightarrow$ Determines that `region == 'East'` filtering is needed, followed by month-over-month trend analysis and ANOVA across product categories $\rightarrow$ Emits `PLAN_CREATED` event over WebSocket.
4. **Execution Phase:** Agents trigger corresponding Python tools in sequence $\rightarrow$ Tool harness executes calculations on the cached DataFrame $\rightarrow$ Each step emits `AGENT_STEP_COMPLETE` with payload and duration.
5. **Synthesis Phase:** Insight Agent synthesizes results, checks statistical significance, flags anomalies, and generates chart specifications $\rightarrow$ Recommendation Agent generates strategic suggestions.
6. **Delivery & Persistence:** Complete session payload stored in PostgreSQL $\rightarrow$ WebSocket transmits `ANALYSIS_COMPLETE` event $\rightarrow$ Frontend renders interactive charts, evidence cards, and executive report.

---

## 7. Storage & Relational Database Design

```sql
-- Core Schema Definitions (PostgreSQL 16)

CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(1024) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    row_count INT NOT NULL,
    column_count INT NOT NULL,
    health_score NUMERIC(5,2),
    schema_metadata JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE analysis_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    user_query TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE agent_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    step_type VARCHAR(50) NOT NULL, -- 'THOUGHT', 'TOOL_CALL', 'OBSERVATION'
    tool_name VARCHAR(100),
    tool_payload JSONB,
    tool_result JSONB,
    duration_ms INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE analysis_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES analysis_sessions(id) ON DELETE CASCADE UNIQUE,
    executive_summary TEXT NOT NULL,
    insights_payload JSONB NOT NULL,
    chart_payload JSONB NOT NULL,
    recommendations_payload JSONB NOT NULL,
    raw_markdown TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_datasets_workspace ON datasets(workspace_id);
CREATE INDEX idx_sessions_dataset ON analysis_sessions(dataset_id);
CREATE INDEX idx_agent_steps_session ON agent_steps(session_id);
```

---

## 8. API Specifications & WebSocket Protocol

### 8.1 REST Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login` | Authenticate user and return JWT bearer token. |
| `POST` | `/api/v1/datasets/upload` | Upload `.csv` or `.xlsx` file (multipart form data). |
| `GET` | `/api/v1/datasets/{id}/profile` | Retrieve automated data quality scorecard and schema. |
| `POST` | `/api/v1/analysis/start` | Submit natural-language question; creates session ID. |
| `GET` | `/api/v1/analysis/{id}/report` | Retrieve completed report, insights, and chart specs. |
| `GET` | `/api/v1/analysis/{id}/export/pdf`| Download generated executive PDF document. |

### 8.2 WebSocket Event Contract (`/ws/analysis/{session_id}`)

Every event over the WebSocket is transmitted as a JSON object:

```json
{
  "event": "AGENT_STEP",
  "session_id": "8f3b6c2d-9e12-4a7b-bc43-1a2b3c4d5e6f",
  "timestamp": "2026-10-02T04:12:08.120Z",
  "data": {
    "agent": "StatisticalAgent",
    "status": "RUNNING_TOOL",
    "tool": "t_test",
    "message": "Testing sales difference between East and West regions..."
  }
}
```

Event Types:
* `SESSION_INITIATED`: Handshake confirmed, session queued.
* `PLAN_CREATED`: Supervisor published the multi-step execution DAG.
* `AGENT_STEP`: Individual agent starting or completing a specific task.
* `TOOL_EXECUTED`: Python tool finished with execution time and summary.
* `INSIGHT_EMITTED`: An evidence-backed insight card generated.
* `ANALYSIS_COMPLETE`: Full analysis finalized; renders report view.
* `ANALYSIS_ERROR`: An unrecoverable exception occurred with error details.

---

## 9. Security Architecture

1. **Defense-in-Depth Python Isolation:** Python tools execute in a constrained process with no network access (`socket` module disabled) and no file system write privileges outside a designated `/tmp/session_scratch` directory.
2. **Strict Parameter Validation:** All tool arguments are deserialized through Pydantic v2 classes with strict type enforcement; input parameters with invalid types are rejected before reaching Python math libraries.
3. **Prompt Hardening:** LLM system instructions use delimiter guards (e.g., `<system_context>`, `<user_question>`) and explicitly instruct the model to ignore any instructions embedded in data column values.
4. **Data Privacy:** Raw row-level microdata is never piped into LLM prompts. Only schema summaries, column names, and computed aggregate statistics are ever sent to the LLM API.
5. **Stateless JWT Security:** High-entropy JWT tokens with 1-hour expiration and cryptographic verification at every API gateway entry point.

---

## 10. Deployment & Infrastructure Architecture

### 10.1 Docker Compose Environment (Production / Staging)

```yaml
version: '3.8'

services:
  reverse-proxy:
    image: caddy:2.8-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./caddy/Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
    depends_on:
      - frontend
      - backend

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - VITE_API_URL=https://api.inferaxis.local
    expose:
      - "80"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql+asyncpg://inferaxis_user:secure_pwd@postgres:5432/inferaxis_db
      - REDIS_URL=redis://redis:6379/0
      - LLM_PROVIDER=openai
      - LLM_API_KEY=${LLM_API_KEY}
      - STORAGE_PATH=/app/storage
    volumes:
      - dataset_storage:/app/storage
    depends_on:
      - postgres
      - redis
    expose:
      - "8000"

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=inferaxis_user
      - POSTGRES_PASSWORD=secure_pwd
      - POSTGRES_DB=inferaxis_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    expose:
      - "5432"

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    expose:
      - "6379"

volumes:
  postgres_data:
  redis_data:
  dataset_storage:
  caddy_data:
```

---

## 11. Monitoring, Observability & Scalability

1. **Structured Logging:** FastAPI and Python tool harnesses output structured JSON logs with correlation IDs (`session_id`, `request_id`, `agent_name`).
2. **Agent Observability:** Integrated with **Langfuse / OpenTelemetry** to track agent token consumption, LLM latency, tool failure rates, and reasoning trace trees.
3. **Application Metrics:** Prometheus exporter on `/metrics` tracking:
   * Active WebSocket connections
   * Tool execution duration histogram
   * LLM API request duration and status codes
   * Database connection pool utilization
4. **Horizontal Scalability Path:**
   * FastAPI backend instances can scale horizontally behind Caddy/Nginx load balancer.
   * Redis Pub/Sub ensures WebSocket events route across multiple backend workers seamlessly.
   * Heavy analytical tool execution can transition to an asynchronous **Celery / ARQ worker pool** as dataset sizes exceed 1 million rows in future phases.
