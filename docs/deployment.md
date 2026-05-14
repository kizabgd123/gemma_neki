---
title: "Deployment Guide"
description: "Installation, configuration, and environment setup for production use."
keywords: ["deployment", "setup", "installation", "environment variables"]
robots: "index, follow"
---

# Deployment Guide

> **Quick Reference**
> - **Platform**: Linux / macOS / Docker
> - **Min Requirements**: 2 vCPU, 4GB RAM (8GB recommended for parallel swarming)
> - **Python Version**: 3.10+
> - **Health Check**: `python3 gemini-run.py "health check"`

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 1 Core | 2+ Cores |
| RAM | 2GB | 8GB (for large DAGs) |
| Disk | 100MB | 1GB+ (for SQLite growth) |
| Runtime | Python 3.10 | Python 3.12 |

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GOOGLE_API_KEY` | Primary Gemini API access key. | Yes | — |
| `MISTRAL_API_KEY` | Fallback Mistral API access key. | Yes | — |
| `KAGGLE_USERNAME` | For `KaggleAgent` operations. | Optional | — |
| `KAGGLE_KEY` | For `KaggleAgent` operations. | Optional | — |

:::warning Security
Never commit `.env` files to source control. Use a secrets manager (e.g., AWS Secrets Manager, GitHub Secrets) in production environments.
:::

## Local Setup

Follow these steps to get the system running on your local workstation.

```bash
# Step 1: Clone the repository
git clone https://github.com/your-org/ai-workflow-orchestrator.git
cd ai-workflow-orchestrator

# Step 2: Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Step 3: Install dependencies
pip install google-generativeai mistralai pandas numpy pytest

# Step 4: Configure environment
cp .env.example .env
# Edit .env with your actual API keys

# Step 5: Verify installation
export PYTHONPATH=.
pytest tests/
```

## Running Your First Workflow

Use the main entrypoint `gemini-run.py` to trigger the orchestrator.

```bash
python3 gemini-run.py "Research and implement a secure JWT authentication module."
```

## CI/CD Pipeline

The project uses a standard 4-gate verification pipeline:

```mermaid
graph LR
    A["🔀 Git Push"] --> B["🧪 Unit Tests (Pytest)"]
    B --> C["⚖️ Debate Simulation"]
    C --> D["📦 Build Docker Image"]
    D --> E["🚀 Deploy to Staging"]
```

---

## See Also
- [System Architecture](architecture.md)
- [CLI Help](cli-help.md)
