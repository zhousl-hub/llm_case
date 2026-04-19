# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI Agent project based on LangChain implementing the **ReAct (Reasoning + Acting)** pattern. The agent can autonomously think, plan, and use tools to complete complex tasks like analyzing Excel data, answering document questions, sending emails, and generating reports.

## Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable for HNSWLIB (required for chromadb)
export HNSWLIB_NO_NATIVE=1

# Configure .env with API keys (copy from demo.env)
OPENAI_API_KEY=sk-xxxx
SILICONFLOW_API_KEY=sk-xxxx  # For GLM-5 via Aliyun DashScope
```

### Run
```bash
# Run the custom ReActAgent implementation
python main.py

# Run using LangChain's native AgentExecutor
python main_lc.py
```

## Architecture

### Core Components

| Module | Purpose |
|--------|---------|
| `Agent/ReAct.py` | Core agent engine implementing ReAct loop (thought → action → observation) |
| `Agent/Action.py` | Pydantic model for action structure (name + args) |
| `Models/Factory.py` | Factory pattern for creating LLM (GPT/GLM-5/Azure) and Embedding models |
| `Tools/` | Tool implementations wrapped as LangChain StructuredTools |

### ReAct Loop Flow
1. Agent receives task → LLM thinks and decides which tool to use
2. Action parsed from LLM output (JSON format in ```json blocks)
3. Tool executed → Observation added to short-term memory (agent_scratchpad)
4. Loop continues until FINISH action or max_thought_steps reached

### Available Tools
- `AskDocument`: RAG-based PDF/Word document Q&A using ChromaDB
- `GenerateDocument`: Generate formal documents
- `SendEmail`: Send emails to specified addresses
- `InspectExcel`: Preview Excel structure (columns + first n rows)
- `ListDirectory`: List files in working directory
- `AnalyseExcel`: Generate and execute Python code to analyze Excel data
- `FINISH`: End task and return final answer

### Key Files
- `prompts/main/main.txt`: Main agent prompt defining behavior, constraints, and output format
- `prompts/tools/excel_analyser.txt`: Prompt for Python code generation
- `data/`: Working directory containing sample Excel files and PDFs

### Two Entry Points
- `main.py`: Custom ReActAgent implementation with manual step execution
- `main_lc.py`: Uses LangChain's `create_react_agent` and `AgentExecutor`

## Model Selection
Edit `ChatModelFactory.get_model()` call in main.py:
- `"gpt-4o"` / `"gpt-3.5-turbo"`: OpenAI via `OPENAI_API_KEY`
- `"glm-5"`: GLM-5 via Aliyun DashScope using `SILICONFLOW_API_KEY`

## Constraints from Prompts
- Maximum 20 thought steps (`max_thought_steps=20`)
- Each step uses exactly one tool
- Must use FINISH to end task
- Never print full file contents (prohibited)
- No assumptions - all info must come from actual data sources
- Do not ask user questions - autonomously complete tasks