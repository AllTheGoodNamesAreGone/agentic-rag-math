Agentic RAG implementation of a Math Tutor

An intelligent mathematics tutoring system built with LangGraph, featuring hybrid knowledge retrieval and cost-optimized AI agents.

## Features

- **Intelligent Routing**: Automatically decides between knowledge base and web search
- **Hybrid Knowledge Base**: Combines curated problems with public datasets (GSM8K, MATH)
- **Cost Optimized**: Uses GPT-3.5-turbo for routing, GPT-4o-mini for generation
- **Free Web Search**: DuckDuckGo integration (no API costs)
- **Safety Guardrails**: Input/output validation for educational content
- **Real-time Feedback**: Human-in-the-loop learning system
- **Usage Tracking**: Monitor API costs and token usage

## Quick Start

### 1. Setup Environment

```bash
# Clone and navigate
git clone <your-repo>
cd math-agentic-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
