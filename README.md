# competitive-intel

Stop manually googling your competitors every morning.

This system runs five agents in parallel — news, GitHub, hiring, and pricing — and folds everything into one briefing. Built with LangGraph, Groq (LLaMA 3.3 70B), and Tavily.

---

## what it does

Point it at a list of competitors. It will:

- search for recent news and extract what actually matters strategically (not summaries — implications)
- scan their public GitHub activity to figure out what they're building
- look at their hiring patterns to predict what they'll ship in the next 3–6 months
- check if their pricing page changed
- run a synthesizer over all four outputs and produce one briefing, sorted by threat level

When multiple agents flag the same company for the same reason independently, the synthesizer weights that signal higher. One source saying something is noise. Three saying it is a signal.

---

## agents

```
competitors_config.py
        │
        ├── News Hawk       → Tavily search → LLaMA analysis → strategic signals
        ├── GitHub Watcher  → GitHub REST API → commit activity → what are they building
        ├── Job Spy         → Tavily search → hiring patterns → roadmap prediction
        └── Price Watcher   → BeautifulSoup scrape → hash diff → pricing changes
                │
                └── Synthesizer → signal convergence → morning briefing
```

---

## setup

**1. Clone and create a virtual environment**
```bash
git clone https://github.com/Darshna136/competitive-intel.git
cd competitive-intel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Set up your API keys**

Create a `.env` file in the root:
```
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
GITHUB_TOKEN=your_github_token
```

Get your keys here:
- Groq → https://console.groq.com
- Tavily → https://tavily.com
- GitHub token → Settings → Developer settings → Personal access tokens (read-only is fine)

**3. Configure your competitors**

Edit `agents/competitors_config.py` and replace the defaults with your actual competitors:
```python
COMPETITORS = [
    {
        "name": "CompanyName",
        "github_org": "their-github-org",
        "description": "what they do",
        "industry": "their space",
        "website": "theirsite.com",
        "pricing_url": "theirsite.com/pricing"
    },
]
```

**4. Run**
```bash
# start the API
uvicorn api.main:app --reload

# or run individual agents directly
python agents/news_hawk.py
python agents/github_watcher.py
python agents/job_spy.py
python agents/price_watcher.py

# full briefing
python orchestrator/synthesizer.py
```

---

## api endpoints

| method | endpoint | what it does |
|--------|----------|--------------|
| GET | `/api/competitors` | list tracked competitors |
| POST | `/api/briefing/generate` | run all agents, generate briefing (takes 2–3 min) |
| GET | `/api/briefing/latest` | fetch the last generated briefing |
| GET | `/api/competitor/{name}` | intel for one specific company |
| GET | `/api/agents/news/{name}` | run news hawk on demand |
| GET | `/api/agents/github/{org}` | run github watcher on demand |
| GET | `/api/stats` | dashboard stats — threat counts, scores |

---

## known limitations

- **Price watcher false positives** — modern pricing pages have dynamic content (tokens, A/B tests, personalization) so the hash diff will sometimes flag a "change" when nothing meaningful changed. Working on diffing the text content instead of the raw HTML hash.
- **Job spy is approximate** — Tavily scrapes LinkedIn indirectly, so you're getting partial data at best. Good enough for directional signals, not a replacement for dedicated hiring data.
- **GitHub watcher only sees public repos** — private development activity is invisible, which means early-stage stealth work won't show up.
- **No scheduler yet** — briefing generation is triggered manually via the API. APScheduler-based morning delivery is on the roadmap.

---

## roadmap

- [ ] scheduled daily briefings via APScheduler
- [ ] React dashboard for browsing briefings visually
- [ ] email delivery of morning briefing
- [ ] Slack/Discord webhook support
- [ ] persistent storage (PostgreSQL) instead of flat files

---

## stack

| layer | tech |
|-------|------|
| agents | Python |
| orchestration | LangGraph |
| LLM | Groq — LLaMA 3.3 70B |
| web search | Tavily |
| github data | GitHub REST API |
| api | FastAPI |
| frontend (wip) | React, TypeScript, Tailwind |