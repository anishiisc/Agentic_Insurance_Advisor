# Insurance Policy Advisor - AI Agent Demo

🛡️ **Bima Buddy** - An AI-powered insurance advisor for the Indian market

## Overview

This is a full-stack teaching demonstration of an **agentic AI application** that helps users find the right insurance policy. The application features:

- **Multi-turn conversations** with context awareness
- **Tool calling** (agentic behavior) for searching insurance products
- **Input/Output guardrails** for safety
- **React frontend** with Tailwind CSS
- **FastAPI backend** with session management

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | FastAPI + Python 3.9+ |
| AI | Claude API (Anthropic) |
| Database | JSON files (no DB setup required) |

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Anthropic API key

### Setup

1. **Clone the repository**
   ```bash
   cd insurance-advisor
   ```

2. **Run the setup script**
   ```bash
   chmod +x scripts/*.sh
   ./scripts/init_project.sh
   ```

3. **Add your API key**
   
   Edit `backend/.env`:
   ```
   ANTHROPIC_API_KEY=your-actual-api-key
   ```

4. **Start the application**
   ```bash
   ./scripts/run_all.sh
   ```

5. **Open in browser**
   - Frontend: http://localhost:5173
   - API Docs: http://localhost:8000/docs

## Project Structure

```
insurance-advisor/
├── backend/
│   ├── main.py          # FastAPI entry point
│   ├── agent.py         # AI agent logic
│   ├── tools.py         # Tool definitions
│   ├── guardrails.py    # Safety checks
│   ├── config.py        # Configuration
│   └── data/
│       └── policies.json
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   └── ...
│
└── scripts/
    ├── init_project.sh
    ├── run_backend.sh
    ├── run_frontend.sh
    ├── run_all.sh
    ├── test_backend.sh
    └── test_frontend.sh
```

## Scripts

| Script | Description |
|--------|-------------|
| `init_project.sh` | Initialize project and install dependencies |
| `run_backend.sh` | Start the FastAPI backend server |
| `run_frontend.sh` | Start the React development server |
| `run_all.sh` | Start both backend and frontend |
| `test_backend.sh` | Run backend API tests |
| `test_frontend.sh` | Run frontend build tests |

## Insurance Categories

The demo covers four insurance types:

1. **Health Insurance** - Individual, Family Floater, Senior Citizen, Super Top-up
2. **Term Life Insurance** - Pure term protection plans
3. **Motor Insurance** - Car and Two-wheeler (Comprehensive & Third Party)
4. **Travel Insurance** - Domestic and International

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Send message and get response |
| `/history/{session_id}` | GET | Get conversation history |
| `/session/{session_id}` | DELETE | Clear a session |
| `/health` | GET | Health check |

## Teaching Concepts

This project demonstrates:

1. **Agentic AI Architecture** - Tool calling, multi-turn reasoning
2. **Full-Stack Development** - React + FastAPI integration
3. **Prompt Engineering** - System prompts, persona design
4. **Guardrails** - Input validation, output safety
5. **Session Management** - Conversation context handling
6. **API Design** - RESTful endpoints with Pydantic models

## Learning Exercises

See the accompanying LaTeX handout for:
- Detailed code explanations
- Architecture diagrams
- Student exercises
- Discussion questions

## License

Educational use only. Not for production deployment.

## Author

Dr. Anish Roychowdhury  
Plaksha University
