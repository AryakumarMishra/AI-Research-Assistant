# AI Research Assistant

An intelligent research agent built with LangGraph and FastAPI that searches the web and academic papers (arXiv) to answer your questions with cited sources.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![React](https://img.shields.io/badge/React-18+-61DAFB)

## Features

- **Web Search**: Tavily Search API integration for current information
- **Academic Papers**: arXiv search for research papers
- **Intelligent Synthesis**: LLM-powered report generation with citations
- **Iterative Research**: Automatically performs multiple search iterations
- **Modern UI**: React frontend with dark theme
- **Source Tracking**: View all sources and findings in sidebar

## Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- LangGraph - Agent orchestration with state graphs
- LangChain - LLM integration
- Groq - Fast LLM inference (Llama 3.1)
- Tavily + arXiv - Search providers

**Frontend:**
- React 18 + Vite
- Lucide React icons
- CSS custom properties for theming

## Project Structure

```
AI_Research_Assistant/
├── backend/
│   ├── main.py              # FastAPI app + LangGraph workflow
│   ├── core/
│   │   ├── tools.py         # Search & calculator tools
│   │   └── get_llm.py       # LLM configuration
│   └── state/
│       └── research_state.py # TypedDict state definition
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.jsx         # Main app with API integration
│   │   └── index.css       # Dark theme styles
│   ├── package.json
│   └── vite.config.js      # Dev server + proxy config
├── .env                    # API keys (Groq)
└── README.md
```

## Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- Groq API key

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn langgraph langchain langchain-groq \
    langchain-community python-dotenv arxiv

# Set environment variable
export GROQ_API_KEY="your-groq-api-key"

# Start backend
uvicorn backend.main:app --reload
```

Backend runs at: `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:3000`

## Usage

1. Open the frontend in your browser (`http://localhost:3000`)
2. Type your research question in the chat input
3. The agent will:
   - Search the web (Tavily)
   - Search academic papers (arXiv)
   - Synthesize findings into a report
   - Display sources and findings in the sidebar

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/chat` | POST | Main research endpoint |

### POST /chat

**Request:**
```json
{
  "message": "Your research question"
}
```

**Response:**
```json
{
  "response": "Synthesized research report...",
  "sources": [...],
  "findings": [...]
}
```

## Agent Architecture

The research agent uses a LangGraph state machine:

```
START → chat → router decides:
  ├─ tool_calls? → tools → extract → chat (loop, max 2 iterations)
  ├─ iteration≥2? → synthesize → END
  └─ else → END
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key for LLM inference |
