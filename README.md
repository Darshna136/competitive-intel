# AI Competitive Intelligence System

An autonomous multi-agent system that monitors competitor companies and generates strategic intelligence briefings.

## What it does

Five specialized agents collect data from different sources:

- **News Hawk** — searches recent news and extracts strategic insights
- **GitHub Watcher** — monitors competitor repository activity
- **Job Spy** — analyzes hiring patterns to predict product roadmap
- **Price Watcher** — detects changes on competitor pricing pages
- **Synthesizer** — combines all signals into one intelligence briefing

Agents are orchestrated using LangGraph. When multiple independent sources point to the same conclusion, the synthesizer weights those signals higher — this is called signal convergence.

## Tech Stack

- Python, FastAPI, LangGraph
- Groq API (LLaMA 3.3 70B)
- Tavily API (web search)
- GitHub REST API
- React, TypeScript, Tailwind CSS
