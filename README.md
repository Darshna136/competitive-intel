# 🎯 AI Competitive Intelligence War Room

An autonomous multi-agent AI system that monitors competitors 24/7 and delivers strategic intelligence briefings every morning — automatically.

Built with LangGraph, Groq LLaMA 3.3, Tavily, FastAPI, and React.

---

## 🤖 How It Works

5 specialized AI agents run in parallel, each with a distinct mission:

| Agent | Mission |
|---|---|
| 🦅 News Hawk | Searches internet for competitor news and extracts strategic insights |
| 🐙 GitHub Watcher | Monitors competitor code activity to detect what they're building |
| 🕵️ Job Spy | Analyzes hiring patterns to predict competitor roadmap 3-6 months ahead |
| 💰 Price Watcher | Detects pricing page changes and interprets strategic meaning |
| 🧠 Synthesizer | Combines all agent outputs into one morning intelligence briefing |

---

## 🏗️ Architecture

User → React Dashboard → FastAPI Backend
                              ↓
                    LangGraph Orchestrator
                    ↙    ↙    ↘    ↘
              News  GitHub  Jobs  Price
              Hawk  Watch   Spy   Watch
                    ↘    ↘    ↙    ↙
                      Synthesizer Agent
                           ↓
                   Morning Briefing 🎯

---

## 🛠️ Tech Stack

**Backend**
- Python + FastAPI
- LangGraph (multi-agent orchestration)
- Groq API — LLaMA 3.3 70B (AI brain)
- Tavily API (web search)
- GitHub REST API

**Frontend**
- React + TypeScript
- Tailwind CSS
- Recharts
- React Router

---

## 📊 Sample Output

    🎯 COMPETITIVE INTELLIGENCE WAR ROOM
    Morning Briefing — May 27 2026

    ⚡ THREAT SUMMARY: 4 HIGH threat competitors detected

    🔴 ATLASSIAN — Threat Score: 85/100 — ACT NOW
       → AI features added to Standard plan (PRICE CHANGE DETECTED)
       → 47 commits to AI repo this week (GITHUB SIGNAL)
       → Hiring 20 ML engineers (JOB SIGNAL)
       CONVERGENCE: 3 sources confirm AI product launch imminent

---

## 🚀 Running Locally

1. Clone the repo

        git clone https://github.com/Darshna136/competitive-intel.git
        cd competitive-intel

2. Setup backend

        python -m venv venv
        venv\Scripts\activate
        pip install -r requirements.txt

3. Add API keys — Create .env file with

        GROQ_API_KEY=your_groq_key
        TAVILY_API_KEY=your_tavily_key
        GITHUB_TOKEN=your_github_token

4. Run backend

        uvicorn api.main:app --reload --port 8000

5. Run frontend

        cd client
        npm install
        npm run dev

6. Open dashboard at http://localhost:5173

---

## 💡 Key Engineering Decisions

**Why LangGraph over simple chains?**
LangGraph allows conditional routing — if GitHub API fails, orchestrator degrades gracefully and synthesizes from remaining agents.

**Why Groq over OpenAI?**
LLaMA 3.3 70B on Groq gives faster inference at zero cost — critical for running 5 agents sequentially without timeouts.

**Signal Convergence Logic**
Single-source signals are weak. When 3 independent agents (news + github + jobs) point to the same conclusion, confidence is HIGH. The synthesizer weights convergent signals 3x higher.

---

## 📁 Project Structure

    competitive-intel/
    ├── agents/
    │   ├── news_hawk.py
    │   ├── github_watcher.py
    │   ├── job_spy.py
    │   ├── price_watcher.py
    │   └── competitors_config.py
    ├── orchestrator/
    │   └── synthesizer.py
    ├── api/
    │   └── main.py
    ├── client/
    │   └── src/
    │       ├── pages/
    │       │   ├── WarRoom.tsx
    │       │   └── CompetitorDetail.tsx
    │       └── components/
    │           ├── ThreatBadge.tsx
    │           └── StatCard.tsx
    └── README.md

---

## 🎯 Target Use Cases

- Product teams — Know what competitors are building before they announce
- Strategy teams — Weekly intelligence briefings without manual research
- Sales teams — Real-time competitive positioning data
- Investors — Portfolio company competitive monitoring

---

Built as a demonstration of multi-agent AI systems for enterprise competitive intelligence.