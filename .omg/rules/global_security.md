---
description: Global safety and authentication rules for AI Workflow Orchestrator.
alwaysApply: true
---

# Global Security Rules

- **Credential Protection**: Never log, print, or commit secrets, API keys, or sensitive credentials.
- **API Verification**: MANDATORY to ask user if LLM/API keys are available/set before any action requiring them.
- **No Mocks**: Simulations are prohibited. Use real services and models.
- **Authenticity**: System must operate with real data and models only.
