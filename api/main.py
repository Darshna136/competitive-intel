import os
import sys
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path so we can import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.competitors_config import COMPETITORS
from agents.news_hawk import run_news_hawk
from agents.github_watcher import run_github_watcher
from agents.job_spy import run_job_spy
from agents.price_watcher import run_price_watcher
from orchestrator.synthesizer import run_synthesizer

# Initialize FastAPI app
app = FastAPI(
    title="Competitive Intelligence API",
    description="AI-powered competitive intelligence system",
    version="1.0.0"
)

# CORS — allows React frontend to talk to this server
# Without this browser blocks the connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store latest briefing in memory
# In production this would be in PostgreSQL
latest_briefing = {
    "generated_at": None,
    "company_briefs": [],
    "raw_briefing": ""
}


# ── MODELS ───────────────────────────────────────
class CompetitorAdd(BaseModel):
    """Schema for adding a new competitor via API"""
    name: str
    github_org: str
    description: str
    industry: str
    website: str
    pricing_url: str = ""


# ── ROUTES ───────────────────────────────────────

@app.get("/")
def root():
    """Health check — confirms server is running"""
    return {
        "status": "running",
        "message": "Competitive Intelligence API is live",
        "version": "1.0.0"
    }


@app.get("/api/competitors")
def get_competitors():
    """
    Return list of all tracked competitors.
    React dashboard uses this to show competitor list.
    """
    return {
        "competitors": COMPETITORS,
        "total": len(COMPETITORS)
    }


@app.get("/api/briefing/latest")
def get_latest_briefing():
    """
    Return the most recently generated briefing.
    This is what the War Room dashboard displays.
    """
    if not latest_briefing["generated_at"]:
        return {
            "status": "no_briefing",
            "message": "No briefing generated yet. Call /api/briefing/generate first.",
            "data": None
        }
    
    return {
        "status": "success",
        "generated_at": latest_briefing["generated_at"],
        "company_briefs": latest_briefing["company_briefs"],
        "total_companies": len(latest_briefing["company_briefs"])
    }


@app.post("/api/briefing/generate")
def generate_briefing():
    """
    Run all agents and generate fresh briefing.
    This takes 2-3 minutes — runs all 4 agents.
    React dashboard calls this and shows loading state.
    """
    try:
        print("Generating fresh briefing...")
        company_briefs, raw_briefing = run_synthesizer()
        
        # Store in memory
        latest_briefing["generated_at"] = datetime.now().isoformat()
        latest_briefing["company_briefs"] = company_briefs
        latest_briefing["raw_briefing"] = raw_briefing
        
        return {
            "status": "success",
            "message": "Briefing generated successfully",
            "generated_at": latest_briefing["generated_at"],
            "company_briefs": company_briefs,
            "total_companies": len(company_briefs)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate briefing: {str(e)}"
        )


@app.get("/api/competitor/{company_name}")
def get_competitor_intel(company_name: str):
    """
    Get detailed intelligence for one specific company.
    React uses this for the Competitor Profile page.
    """
    # Find company in config
    company = next(
        (c for c in COMPETITORS if c["name"].lower() == company_name.lower()),
        None
    )
    
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Competitor '{company_name}' not found"
        )
    
    # Find their brief in latest briefing
    brief = next(
        (b for b in latest_briefing["company_briefs"]
         if b.get("competitor", "").lower() == company_name.lower()),
        None
    )
    
    return {
        "company": company,
        "brief": brief,
        "has_brief": brief is not None
    }


@app.get("/api/agents/news/{company_name}")
def run_news_for_company(company_name: str):
    """
    Run News Hawk for a single company on demand.
    """
    try:
        reports = run_news_hawk([company_name])
        return {
            "status": "success",
            "company": company_name,
            "report": reports[0] if reports else {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/github/{github_org}")
def run_github_for_company(github_org: str):
    """
    Run GitHub Watcher for a single org on demand.
    """
    try:
        reports = run_github_watcher([github_org])
        return {
            "status": "success",
            "org": github_org,
            "report": reports[0] if reports else {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
def get_stats():
    """
    Return system stats for dashboard header.
    """
    high_threats = [
        b for b in latest_briefing["company_briefs"]
        if b.get("overall_threat_level") == "HIGH"
    ]
    
    avg_score = 0
    if latest_briefing["company_briefs"]:
        scores = [
            b.get("overall_threat_score", 0)
            for b in latest_briefing["company_briefs"]
        ]
        avg_score = sum(scores) / len(scores)
    
    return {
        "total_competitors": len(COMPETITORS),
        "high_threats": len(high_threats),
        "average_threat_score": round(avg_score, 1),
        "last_updated": latest_briefing["generated_at"],
        "agents_running": 4
    }