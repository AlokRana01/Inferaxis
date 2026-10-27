# Inferaxis Backend Service

FastAPI asynchronous backend core for the Inferaxis Autonomous AI Data Intelligence platform.

## Local Development Setup (Windows PowerShell)

### 1. Prerequisites
- Python 3.11+ (Python 3.13 supported)
- Git

### 2. Create and Activate Virtual Environment
```powershell
# Navigate to the backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment (PowerShell)
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install backend dependencies in editable mode with development tools
pip install -e ".[dev]"
```

### 4. Run Development Server
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Run Test Suite
```powershell
pytest
```
