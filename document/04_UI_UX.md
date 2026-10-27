# UI/UX Specification Document

## Project: Inferaxis — Autonomous AI for Evidence-Based Data Intelligence
**Document Version:** 2.0.0 (Updated to Reference UI Design)  
**Status:** Approved UI/UX Design System & Master Blueprint  
**Target Release:** MVP (Phase 1)  
**Author:** Inferaxis Product Design & Experience Group  
**Last Updated:** October 2026  

---

## 1. Design Philosophy & Master Visual Layout: The Bento Grid Style ("Banto Style")

Inferaxis adopts the modern **Bento Grid (Banto Style)** design architecture—inspired by traditional Japanese bento boxes, featuring compartmentalized, modular cells that organize complex, multi-modal data intelligence into clean, scannable, and interactive visual containers.

### Core Pillars of the Bento Grid ("Banto Style") System:
1. **Compartmentalized Modularity:** Each analytic dimension (Metrics, Natural Language Inquiry, Recent Files, Multi-Agent Activity, Statistical Insights, Trend Charts, Data Quality, and Quick Actions) lives in its own dedicated, self-contained Bento card.
2. **Harmonious Asymmetry:** The dashboard avoids monotonous equal grids by utilizing deliberate proportional spans:
   * **Row 1:** 4 equal metric pill containers (`grid-cols-4`).
   * **Row 2:** Wide 2-span Hero Query box (`col-span-2`) paired with a compact 1-span Recent Datasets card (`col-span-1`).
   * **Row 3:** Balanced 3-column cockpit (`grid-cols-3`): Live Agent Timeline, Featured Insight + Chart, and Data Quality Donut + Quick Action grid.
3. **Soft Elevation & Tactile Radii:** Generous border radii (`rounded-2xl` / 16px), 1px subtle slate borders (`border-slate-200/80`), soft ambient shadows, and micro-hover lifts (`hover:-translate-y-0.5 transition-transform`).
4. **Information Density with Cognitive Calm:** Packs extensive investigative telemetry without clutter or visual fatigue.


```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                         INFERAXIS DESKTOP WORKSPACE LAYOUT                                     │
├──────────────┬──────────────────────────────────────────────────────────────────────────────────────────────┤
│ SIDEBAR      │ TOP BAR: Welcome back, [User]! │ [Search datasets, analyses...]    [🔔 Notifications] [☀️/🌙] │
│ (Dark Navy)  ├──────────────────────────────────────────────────────────────────────────────────────────────┤
│              │ SUMMARY METRIC CARDS:                                                                        │
│ • Logo       │ [Total Datasets: 12]  [Total Analyses: 8]  [Key Insights: 24]  [Reports Generated: 5]        │
│ • Dashboard  ├───────────────────────────────────────────────────────────────┬──────────────────────────────┤
│ • Datasets   │ HERO: "Ask a question about your data"                        │ RECENT DATASETS:             │
│ • Analysis   │ [ Upload / Type prompt: "Why did revenue decrease in Q3?" ]   │ • sales_data.csv (125k rows) │
│ • Insights   │ [ Start Analysis → ] • Supported: CSV, XLSX (Max: 50MB)      │ • customer_churn.csv         │
│ • Reports    │ 🤖 3D Agentic Avatar & Holographic Data Cards                 │ • financial_data.csv         │
│              ├──────────────────────────────┬───────────────────────────────┼──────────────────────────────┤
│ [AI-Powered  │ AGENT ACTIVITY (● Live)      │ KEY INSIGHTS & REVENUE TREND  │ DATA QUALITY & QUICK ACTIONS │
│  Promo Box]  │ ✓ Supervisor Agent (00:18)   │ ★ "Revenue down 18.4% in Q3"  │ ⭕ Donut: 91/100 ("Good")     │
│              │ ✓ Data Understanding (00:32) │ • 4 Impact Metric Pills       │ • Missing: 2.3% • Dups: 1.1% │
│ [User Badge: │ ✓ Data Quality (01:12)       │ 📈 Interactive Area/Line Chart│ ---------------------------- │
│  John Doe    │ ⟳ EDA Agent (02:34 Active)   │   ($0 to $600k across months) │ 4 Quick Action Cards:        │
│  MSc Data]   │ ○ Stats / Viz / Insights     │   Tooltip: $284,320 (-18.4%)  │ [Upload] [Insights] [Report] │
└──────────────┴──────────────────────────────┴───────────────────────────────┴──────────────────────────────┘
```

---

## 2. Design Tokens & Design System

### 2.1 Dual-Theme Architecture (Light Canvas with Dark Sidebar Default)
The reference UI introduces a high-contrast hybrid: a deep navy navigation sidebar paired with a clean, airy, high-contrast canvas that reduces visual fatigue while highlighting data visualizations.

```
  Left Navigation Sidebar (Deep Navy / Slate):
  [#0B132B - Sidebar Base]    [#1E293B - Card Surface]    [#334155 - Borders]
  
  Main Workspace Canvas (Light / Neutral):
  [#F8FAFC - Canvas Base]     [#FFFFFF - Card White]      [#E2E8F0 - Card Borders]
  
  Semantic Accent Palette:
  [#2563EB - Royal Blue CTA]  [#10B981 - Emerald Success] [#8B5CF6 - Purple AI Sparkle]
  [#F59E0B - Amber Reports]   [#EF4444 - Rose Metric Drop]
```

| Token Name | Hex Code | HSL Value | Purpose & Usage |
| :--- | :--- | :--- | :--- |
| `sidebar-bg` | `#0B132B` / `#0F172A` | `hsl(222, 47%, 11%)` | Primary left navigation background |
| `sidebar-text-active` | `#FFFFFF` | `hsl(0, 0%, 100%)` | Active sidebar label with subtle blue highlight pill |
| `sidebar-text-muted` | `#94A3B8` | `hsl(215, 20%, 65%)` | Inactive sidebar menu items |
| `canvas-bg` | `#F8FAFC` | `hsl(210, 40%, 98%)` | Main application background |
| `card-surface` | `#FFFFFF` | `hsl(0, 0%, 100%)` | Elevated widget surfaces, shadow: `0 1px 3px rgba(0,0,0,0.06)` |
| `card-border` | `#E2E8F0` | `hsl(214, 32%, 91%)` | 1px border around cards and input containers |
| `primary-blue` | `#2563EB` | `hsl(221, 83%, 53%)` | Primary button CTA, active sparklines, key chart lines |
| `success-green` | `#10B981` | `hsl(158, 64%, 52%)` | Data Quality score (91/100), completed agent checkmarks |
| `accent-purple` | `#8B5CF6` | `hsl(258, 90%, 66%)` | AI Analysis badge, ML Scientist mode, Insights sparklines |
| `warning-amber` | `#F59E0B` | `hsl(38, 92%, 50%)` | Reports generated, missing values alert |
| `danger-rose` | `#EF4444` | `hsl(0, 84%, 60%)` | Negative deltas (`-18.4%`, `-31%`), critical warnings |
| `text-primary` | `#0F172A` | `hsl(222, 47%, 11%)` | Primary headers, numeric counters |
| `text-secondary` | `#64748B` | `hsl(215, 16%, 47%)` | Subtitles, row metadata, file size text |

### 2.2 Typography Hierarchy
* **Primary Sans:** `Inter`, `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
* **Numeric & Monospace:** `Inter` (tabular figures `font-variant-numeric: tabular-nums`) & `JetBrains Mono` for code/data columns.

| Token | Size / Line Height | Weight | Applied To |
| :--- | :--- | :--- | :--- |
| `title-greeting` | 24px / 32px | Bold (700) | "Welcome back, John!" |
| `metric-counter` | 28px / 36px | Bold (700) | Top 4 metric card values (`12`, `8`, `24`, `5`) |
| `card-header` | 16px / 24px | SemiBold (600) | "Agent Activity", "Key Insights", "Data Quality" |
| `body-base` | 14px / 20px | Regular (400) | Hero description, insight summary narrative |
| `meta-caption` | 12px / 16px | Regular (400) | "125,000 rows • 18 columns", timestamp tags |
| `chip-tag` | 11px / 14px | SemiBold (600) | "● Live", "High Confidence", "AI ANALYSIS" |

---

## 3. Detailed Layout & Screen Architecture

### 3.1 Left Navigation Rail (`Sidebar`)
* **Width:** Fixed 260px desktop width.
* **Branding Header:**
  * Hexagonal / interconnected AI node glyph.
  * Application Title: **Agentic Data Scientist**
  * Sub-branding: *"Your Autonomous AI Data Scientist"*
* **Navigation Menu (Vertical Stack):**
  1. `Dashboard` — Home icon, highlighted with rounded blue-tinted container (`bg-blue-600/10 text-blue-400 font-medium`).
  2. `Datasets` — Layered database discs icon.
  3. `Analysis` — Multi-branch sparkle / node graph icon.
  4. `Insights` — Glowing lightbulb icon.
  5. `Reports` — Document / clipboard icon.
* **Bottom Promotional Card:**
  * Subtle gradient backdrop (`from-blue-900/40 to-indigo-900/20`).
  * Icon: Glowing sparkle badge.
  * Headline: *"AI-Powered Data Analysis"*
  * Copy: *"From your data to actionable insights."*
* **User Profile Footer:**
  * User Initials Avatar: Circular badge `JD` on dark slate backing.
  * User Name: **John Doe**
  * Qualification / Subtitle: *"MSc Data Science"*
  * Dropdown Caret: Downward chevron for workspace / account switching.

---

### 3.2 Top Header Bar (`Header`)
* **Greeting & Subtitle (Left):**
  * `h1`: *"Welcome back, John!"*
  * Subtext: *"Turn your data into insights with the power of AI agents."*
* **Global Controls (Right):**
  * Search Bar: Embedded magnifying glass icon + placeholder *"Search datasets, analyses, insights..."* (`w-72 rounded-lg bg-slate-100/80 px-3 py-1.5 text-sm`).
  * Notification Bell: Bell icon with red unread indicator dot (`#EF4444`).
  * Theme Toggle: Sun / Moon icon button for switching between Hybrid Light and Full Dark Mode.

---

### 3.3 Top Summary Metric Cards (4-Column Grid)
Each card features an icon on a soft pastel background, large metric count, trend indicator, and a sleek SVG sparkline curve:

| Card Title | Metric | Trend Indicator | Visual Element | Accent Tint |
| :--- | :---: | :---: | :--- | :--- |
| **Total Datasets** | `12` | ↗ `+2 this week` | Soft blue sparkline curve | Light Blue (`bg-blue-50 text-blue-600`) |
| **Total Analyses** | `8` | ↗ `+3 this week` | Emerald sparkline curve | Light Emerald (`bg-emerald-50 text-emerald-600`) |
| **Key Insights** | `24` | ↗ `+6 this week` | Purple sparkline curve | Light Purple (`bg-purple-50 text-purple-600`) |
| **Reports Generated** | `5` | ↗ `+2 this week` | Amber sparkline curve | Light Amber (`bg-amber-50 text-amber-600`) |

---

### 3.4 Middle Tier: AI Hero Input & Recent Datasets

```
┌─────────────────────────────────────────────────────────────┬────────────────────────────────┐
│ HERO AI QUERY & UPLOAD BOX (2/3 Grid Width)                 │ RECENT DATASETS (1/3 Grid)     │
│                                                             │                                │
│ [✨ AI ANALYSIS]                                            │ Recent Datasets      View all →│
│ Ask a question about your data                              ├────────────────────────────────┤
│ Upload a dataset and ask anything in natural language.      │ [CSV] sales_data.csv           │
│ Our AI agents will analyze, find insights, and give you     │       125,000 rows • 18 cols   │
│ an evidence-based answer.                                   │       2 hours ago          ... │
│                                                             ├────────────────────────────────┤
│ ┌──────────────────────────────────────────┬──────────────┐ │ [CSV] customer_churn.csv       │
│ │ ⤒  e.g. Why did revenue decrease in Q3?  │Start Analysis│ │       10,542 rows • 12 cols    │
│ └──────────────────────────────────────────┴──────────────┘ │       1 day ago            ... │
│ Supported formats: CSV, XLSX • Max size: 50MB               ├────────────────────────────────┤
│                                     [ 🤖 3D Robot Avatar &  │ [CSV] financial_data.csv       │
│                                       Holographic Charts ]  │       8,921 rows • 15 cols     │
│                                                             │       2 days ago           ... │
│                                                             ├────────────────────────────────┤
│                                                             │ [XLSX] ecommerce_data.csv      │
│                                                             │        50,000 rows • 20 cols   │
│                                                             │        3 days ago          ... │
└─────────────────────────────────────────────────────────────┴────────────────────────────────┘
```

#### Hero Query Card (`HeroQueryCard`):
* **Badge:** Pill badge `AI ANALYSIS` with sparkle icon in light violet.
* **Headline:** *"Ask a question about your data"* (20px, bold).
* **Description:** *"Upload a dataset and ask anything in natural language. Our AI agents will analyze, find insights, and give you an evidence-based answer."*
* **Search / Upload Input Bar:**
  * Upload Icon button (`↑`) for immediate file selection.
  * Input field with placeholder: *"e.g. Why did revenue decrease in Q3?"*
  * Action Button: Blue button *"Start Analysis →"* with subtle hover lift.
* **Footer Metadata:** *"Supported formats: CSV, XLSX • Max size: 50MB"*
* **Hero Illustration:** 3D friendly AI Assistant robot with floating holographic charts and statistical graphs.

#### Recent Datasets Card (`RecentDatasetsCard`):
* **Header:** Section Title *"Recent Datasets"* + Text Link *"View all →"* (`text-blue-600 text-sm font-medium`).
* **Dataset List Items:**
  * File Icon Badges: Color-coded file tags:
    * `CSV` in Emerald Green (`sales_data.csv`)
    * `CSV` in Royal Blue (`customer_churn.csv`)
    * `CSV` in Forest Green (`financial_data.csv`)
    * `XLSX` in Violet (`ecommerce_data.csv`)
  * Item Details: Title, Row & Column count (`125,000 rows • 18 columns`), and relative timestamp (`2 hours ago`).
  * Quick Actions: Three-dots context menu (`...`) for inspect, download, or delete.

---

### 3.5 Bottom Tier: Live Cockpit (3-Column Grid)

```
┌──────────────────────────────┬───────────────────────────────┬──────────────────────────────┐
│ AGENT ACTIVITY (1/3 Width)   │ KEY INSIGHTS & CHARTS (1/3)   │ DATA QUALITY & ACTIONS (1/3) │
├──────────────────────────────┼───────────────────────────────┼──────────────────────────────┤
│ Agent Activity ● Live View → │ Key Insights        View all →│ Data Quality                 │
│                              │                               │                              │
│ ✓ Supervisor Agent   00:18 ✓ │ 📉 Revenue decreased by 18.4% │      ╭───────╮  Missing: 2.3%│
│   Analyzing your request...  │    in Q3     [High Confidence]│     │ 91/100  │  Dups:    1.1%│
│                              │ The decline is primarily      │      ╰───────╯  Incon:   0.8%│
│ ✓ Data Understanding 00:32 ✓ │ driven by West region (-27%), │        Good     Outlier: 0.6%│
│   Inspecting structure...    │ Product Category A (-31%)...  ├──────────────────────────────┤
│                              │                               │ Quick Actions                │
│ ✓ Data Quality Agent 01:12 ✓ │ [-18.4%] [-27%] [-31%] [-14%] │ ┌────────────┐┌────────────┐ │
│   Checking missing values... │ ───────────────────────────── │ │[⤒] Upload  ││[💡] View    │ │
│                              │ Revenue Trend       Monthly ▾ │ │    Dataset ││    Insights │ │
│ ⟳ EDA Agent          02:34 ⟳ │ $600k ──┐                     │ └────────────┘└────────────┘ │
│   Exploring distributions... │ $400k   └──● $284k (-18.4%)   │ ┌────────────┐┌────────────┐ │
│                              │ $200k                         │ │[📄] Generate││[⬡] ML Sci- │ │
│ ○ Statistics Agent   Pending │    Jan  Mar  May  Jul  Sep    │ │    Report  ││    entist   │ │
│ ○ Visualization AgentPending │                               │ └────────────┘└────────────┘ │
│ ○ Insight Agent      Pending │                               │                              │
└──────────────────────────────┴───────────────────────────────┴──────────────────────────────┘
```

#### Column 1: Agent Activity (`AgentActivityTimeline`):
* **Header:** Title *"Agent Activity"*, green pulsing badge `● Live`, and link *"View details →"*.
* **Live Step Timeline:**
  * **Supervisor Agent:** *"Analyzing your request..."* — Duration: `00:18`, Status: Emerald checkmark ✓.
  * **Data Understanding Agent:** *"Inspecting dataset structure..."* — Duration: `00:32`, Status: Emerald checkmark ✓.
  * **Data Quality Agent:** *"Checking for missing values, duplicates..."* — Duration: `01:12`, Status: Emerald checkmark ✓.
  * **EDA Agent:** *"Exploring data patterns and distributions..."* — Duration: `02:34`, Status: Active pulsing blue circle ⟳.
  * **Statistics Agent:** *"Running statistical analysis..."* — Status: Hollow dim gray circle (Pending).
  * **Visualization Agent:** *"Creating relevant charts..."* — Status: Pending.
  * **Insight Agent:** *"Generating key findings..."* — Status: Pending.

#### Column 2: Key Insights & Deep Trend Chart (`InsightsChartWidget`):
* **Header:** Title *"Key Insights"* + link *"View all →"*.
* **Featured Finding Card:**
  * Trend-down icon + headline: *"Revenue decreased by 18.4% in Q3"*
  * Confidence Chip: Green pill badge `High Confidence`.
  * Diagnostic Summary: *"The decline is primarily driven by the West region (-27%), Product Category A (-31%), and a 14% decrease in average order quantity. The trend started in July."*
  * 4 Key Metric Breakdown Pills (with red negative percentage callouts):
    * `Revenue Change: -18.4%`
    * `West Region: -27%`
    * `Product A: -31%`
    * `Avg. Order Qty: -14%`
* **Interactive Chart Component (`RevenueTrendChart`):**
  * Title: *"Revenue Trend"* with period selector dropdown (`Monthly ▾`).
  * Chart Type: Smooth Area Chart with subtle blue gradient fill (`fill="url(#blueGradient)"`), crisp line (`stroke="#3B82F6"`, strokeWidth: 2), and circular data points.
  * Tooltip Card: Dark floating badge hovering on active data point: *"Q3 Revenue: $284,320 (-18.4%)"*.
  * Axes: Y-axis `$0`, `$200k`, `$400k`, `$600k`; X-axis `Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`.

#### Column 3: Data Quality & Quick Actions (`QualityQuickActionsWidget`):
* **Data Quality Card:**
  * Circular Radial Donut Gauge:
    * Score: **`91 / 100`** in bold text.
    * Status Label: **`Good`** in emerald green.
    * Colored track in vibrant teal/emerald (`#10B981`).
  * Right Metric Breakdown:
    * `Missing Values`: **2.3%** (Amber icon)
    * `Duplicates`: **1.1%** (Blue icon)
    * `Inconsistent Data`: **0.8%** (Purple icon)
    * `Outliers`: **0.6%** (Emerald icon)
* **Quick Actions Grid (2x2 Cards):**
  1. **Upload Dataset** — *"Add a new CSV file"* (Emerald green upload icon).
  2. **View Insights** — *"Explore saved insights"* (Purple lightbulb icon).
  3. **Generate Report** — *"Download PDF report"* (Blue document icon).
  4. **ML Scientist Mode** — *"Build predictive models"* (Violet 3D cube icon).

---

## 4. UI Component Hierarchy & React Specifications

```
src/
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx                # Left navy rail with logo, nav, promo, and profile
│   │   ├── Header.tsx                 # Greeting, search, notifications, and theme toggle
│   │   └── AppShell.tsx               # Main container with responsive grid
│   ├── dashboard/
│   │   ├── MetricCard.tsx             # 4 summary cards with sparklines
│   │   ├── HeroQueryCard.tsx          # Natural language question bar & 3D graphic
│   │   ├── RecentDatasetsCard.tsx     # File list with colored badges & timestamps
│   │   ├── AgentActivityTimeline.tsx  # Live multi-agent execution steps & timer
│   │   ├── KeyInsightCard.tsx         # Diagnostic narrative & 4 impact metric chips
│   │   ├── RevenueTrendChart.tsx      # Recharts Area/Line chart with custom tooltip
│   │   ├── DataQualityGauge.tsx       # Donut gauge (91/100) & 4 quality metrics
│   │   └── QuickActionGrid.tsx        # 2x2 action buttons (Upload, Insights, Report, ML)
```

---

## 5. Micro-Interactions & Animation States

1. **Agent Timeline Transitions:**
   * Active step displays a subtle pulsating CSS glow ring (`animate-pulse`).
   * Duration counter increments dynamically (`00:18` $\rightarrow$ `00:19`).
   * On completion, transitions smoothly from blue spinner to emerald checkmark with a subtle scale pop (`transform: scale(1.1) -> scale(1.0)`).
2. **Chart Tooltip Interaction:**
   * Hovering over data points highlights the point with an enlarged ring marker.
   * Tooltip smoothly transitions horizontally without flickering.
3. **Hero Input Focus Effect:**
   * Clicking into *"e.g. Why did revenue decrease in Q3?"* applies an active ring: `ring-2 ring-blue-500/20 border-blue-500`.
   * *"Start Analysis →"* CTA button features a subtle translateX arrow hover effect (`group-hover:translate-x-1`).

---

## 6. Accessibility & Responsive Breakpoints

* **WCAG 2.1 AA Compliance:** Minimum 4.5:1 text-to-background contrast ratio across both light canvas and dark sidebar.
* **Screen Reader Labels:** All icons (notifications, theme toggle, file actions) include explicit `aria-label` attributes.
* **Responsive Breakpoints:**
  * **Desktop Large ($\ge 1440\text{px}$):** Full 3-column bottom layout as shown in the reference design.
  * **Laptop / Tablet Landscape ($1024\text{px} - 1439\text{px}$):** Bottom section wraps Column 3 (Data Quality & Actions) beneath Column 2.
  * **Tablet Portrait ($768\text{px} - 1023\text{px}$):** Collapsible sidebar menu; single-column stacked cards.
  * **Mobile ($< 768\text{px}$):** Sticky bottom navigation; search moves into header modal; charts support horizontal panning.
