import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# Import all 4 agents
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.news_hawk import run_news_hawk
from agents.github_watcher import run_github_watcher
from agents.job_spy import run_job_spy
from agents.price_watcher import run_price_watcher
from agents.competitors_config import COMPETITORS

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)


def collect_all_intelligence() -> dict:
    """
    Run all 4 agents and collect their reports.
    
    Each agent runs independently and returns its reports.
    We organize everything by company name so synthesizer
    can easily find all intel about one company.
    
    Returns:
        Dict organized by company name with all agent reports
    """
    
    print("\n" + "="*60)
    print("SYNTHESIZER ACTIVATED — Running all agents...")
    print("="*60)
    
    # Prepare inputs for each agent
    company_names = [c["name"] for c in COMPETITORS]
    github_orgs = [c["github_org"] for c in COMPETITORS]
    
    # Run all 4 agents
    # In production these would run in parallel
    # For now sequential is fine
    print("\n[1/4] Running News Hawk...")
    news_reports = run_news_hawk(company_names)
    
    print("\n[2/4] Running GitHub Watcher...")
    github_reports = run_github_watcher(github_orgs)
    
    print("\n[3/4] Running Job Spy...")
    job_reports = run_job_spy(company_names)
    
    print("\n[4/4] Running Price Watcher...")
    price_reports = run_price_watcher(COMPETITORS)
    
    # Organize all reports by company name
    # So we can easily get all intel about "Notion" in one place
    intelligence = {}
    
    for company in COMPETITORS:
        name = company["name"]
        intelligence[name] = {
            "company": company,
            "news": {},
            "github": {},
            "jobs": {},
            "pricing": {}
        }
    
    # Map news reports to companies
    for report in news_reports:
        name = report.get("competitor")
        if name in intelligence:
            intelligence[name]["news"] = report
    
    # Map github reports — github uses org names not company names
    # So we match by index position
    for i, report in enumerate(github_reports):
        if i < len(COMPETITORS):
            name = COMPETITORS[i]["name"]
            if name in intelligence:
                intelligence[name]["github"] = report
    
    # Map job reports
    for report in job_reports:
        name = report.get("competitor")
        if name in intelligence:
            intelligence[name]["jobs"] = report
    
    # Map pricing reports
    for report in price_reports:
        name = report.get("competitor")
        if name in intelligence:
            intelligence[name]["pricing"] = report
    
    return intelligence


def synthesize_company_brief(company_name: str, intel: dict) -> dict:
    """
    Take all intelligence about one company and synthesize
    into a single strategic brief using Llama.
    
    This is the magic — AI connects dots across all sources:
    "They're hiring ML engineers AND committing heavily to AI repos
     AND news shows AI product announcement = HIGH THREAT, launching soon"
    
    Args:
        company_name: e.g. "Notion"
        intel: all agent reports for this company
    
    Returns:
        Synthesized strategic brief
    """
    
    company_info = intel.get("company", {})
    news = intel.get("news", {})
    github = intel.get("github", {})
    jobs = intel.get("jobs", {})
    pricing = intel.get("pricing", {})
    
    # Build a comprehensive context for the AI
    context = f"""
    COMPANY: {company_name}
    DESCRIPTION: {company_info.get('description', 'N/A')}
    INDUSTRY: {company_info.get('industry', 'N/A')}
    
    ━━━ NEWS INTELLIGENCE ━━━
    Threat Level: {news.get('threat_level', 'N/A')}
    Summary: {news.get('summary', 'N/A')}
    Key Signals: {json.dumps(news.get('key_signals', []), indent=2)}
    
    ━━━ GITHUB ACTIVITY ━━━
    Threat Level: {github.get('threat_level', 'N/A')}
    What They Are Building: {github.get('what_they_are_building', 'N/A')}
    Most Active Repo: {github.get('most_active_repo', 'N/A')}
    Summary: {github.get('summary', 'N/A')}
    
    ━━━ HIRING INTELLIGENCE ━━━
    Threat Level: {jobs.get('threat_level', 'N/A')}
    Predicted Roadmap: {jobs.get('predicted_roadmap', 'N/A')}
    Hiring Patterns: {json.dumps(jobs.get('hiring_patterns', []), indent=2)}
    
    ━━━ PRICING INTELLIGENCE ━━━
    Threat Level: {pricing.get('threat_level', 'N/A')}
    Pricing Strategy: {pricing.get('pricing_strategy', 'N/A')}
    Change Detected: {pricing.get('change_detected', False)}
    Change Analysis: {pricing.get('change_analysis', 'N/A')}
    Plans: {json.dumps(pricing.get('plans_detected', []), indent=2)}
    """
    
    system_prompt = """You are the Chief Intelligence Officer at a top strategy firm.
    You receive intelligence from 4 different sources about a competitor
    and synthesize it into one definitive strategic brief.
    
    Your superpower is finding CONVERGENCE — when multiple independent 
    sources point to the same conclusion, that conclusion is highly reliable.
    
    Example of convergence:
    - News: "Company X announced AI initiative"  
    - GitHub: "Heavy commits to AI repo this week"
    - Jobs: "Hiring 20 ML engineers"
    → All 3 point to AI → CONFIRMED HIGH THREAT
    
    Always respond in valid JSON only. No markdown. No backticks."""
    
    user_prompt = f"""
    Synthesize all intelligence about {company_name} into one strategic brief.
    
    {context}
    
    Look for signal convergence across sources.
    Calculate an overall threat score (0-100).
    
    Respond with ONLY this JSON:
    {{
        "competitor": "{company_name}",
        "overall_threat_score": <number 0-100>,
        "overall_threat_level": "HIGH/MEDIUM/LOW",
        "convergence_signals": [
            {{
                "finding": "what multiple sources agree on",
                "sources": ["news", "github", "jobs", "pricing"],
                "confidence": "HIGH/MEDIUM/LOW",
                "implication": "what this means strategically"
            }}
        ],
        "top_3_risks": [
            "most critical risk from this competitor right now"
        ],
        "predicted_moves": [
            "what this competitor will likely do in next 3-6 months"
        ],
        "recommended_actions": [
            "specific urgent action your company should take"
        ],
        "executive_summary": "3-4 sentence definitive summary of this competitor's current strategic position and threat level",
        "urgency": "ACT NOW/MONITOR CLOSELY/WATCH"
    }}
    """
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    try:
        raw_text = response.content.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "competitor": company_name,
            "overall_threat_score": 0,
            "overall_threat_level": "UNKNOWN",
            "raw_analysis": response.content,
            "convergence_signals": [],
            "top_3_risks": [],
            "recommended_actions": []
        }


def generate_morning_briefing(company_briefs: list) -> str:
    """
    Take all company briefs and generate one morning briefing.
    
    This is the final output — what a CEO or strategy team
    reads every morning over coffee.
    
    Args:
        company_briefs: list of synthesized briefs per company
    
    Returns:
        Formatted morning briefing as string
    """
    
    # Sort companies by threat score — highest threat first
    sorted_briefs = sorted(
        company_briefs,
        key=lambda x: x.get("overall_threat_score", 0),
        reverse=True
    )
    
    today = datetime.now().strftime("%A, %B %d %Y")
    
    briefing = f"""
{"="*65}
        🎯 COMPETITIVE INTELLIGENCE WAR ROOM
        Morning Briefing — {today}
        Generated by AI Agent System
{"="*65}

"""
    
    # Overall threat summary
    high_threats = [b for b in sorted_briefs if b.get("overall_threat_level") == "HIGH"]
    briefing += f"⚡ THREAT SUMMARY: {len(high_threats)} HIGH threat competitors detected\n"
    briefing += f"📊 Companies monitored: {len(sorted_briefs)}\n"
    briefing += "\n" + "-"*65 + "\n"
    
    # Each company brief
    for brief in sorted_briefs:
        threat_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(
            brief.get("overall_threat_level"), "⚪"
        )
        urgency_emoji = {"ACT NOW": "🚨", "MONITOR CLOSELY": "⚠️", "WATCH": "👁️"}.get(
            brief.get("urgency"), "📌"
        )
        
        briefing += f"""
{threat_emoji} {brief.get('competitor', 'Unknown').upper()}
   Threat Score: {brief.get('overall_threat_score', 0)}/100
   Urgency: {urgency_emoji} {brief.get('urgency', 'N/A')}

   EXECUTIVE SUMMARY:
   {brief.get('executive_summary', 'N/A')}

   TOP RISKS:"""
        
        for risk in brief.get('top_3_risks', []):
            briefing += f"\n   ⚠️  {risk}"
        
        briefing += "\n\n   PREDICTED MOVES:"
        for move in brief.get('predicted_moves', []):
            briefing += f"\n   🔮 {move}"
        
        briefing += "\n\n   ACTION REQUIRED:"
        for action in brief.get('recommended_actions', []):
            briefing += f"\n   ✅ {action}"
        
        # Show convergence signals if any
        convergence = brief.get('convergence_signals', [])
        if convergence:
            briefing += "\n\n   SIGNAL CONVERGENCE:"
            for signal in convergence[:2]:
                sources = ", ".join(signal.get('sources', []))
                briefing += f"\n   🎯 {signal.get('finding')} [{sources}]"
        
        briefing += f"\n\n{'-'*65}\n"
    
    briefing += f"\n{'='*65}\n"
    briefing += "End of Morning Briefing\n"
    briefing += f"{'='*65}\n"
    
    return briefing


def run_synthesizer():
    """
    Master function — runs everything end to end.
    
    1. Runs all 4 agents
    2. Synthesizes per-company briefs
    3. Generates morning briefing
    4. Saves to file
    5. Prints to terminal
    """
    
    # Step 1: Collect intelligence from all agents
    all_intelligence = collect_all_intelligence()
    
    print("\n" + "="*60)
    print("SYNTHESIZING INTELLIGENCE...")
    print("="*60)
    
    # Step 2: Synthesize brief for each company
    company_briefs = []
    for company_name, intel in all_intelligence.items():
        print(f"\nSynthesizing: {company_name}...")
        brief = synthesize_company_brief(company_name, intel)
        company_briefs.append(brief)
        print(f"   Threat Score: {brief.get('overall_threat_score', 0)}/100")
    
    # Step 3: Generate morning briefing
    print("\nGenerating morning briefing...")
    briefing = generate_morning_briefing(company_briefs)
    
    # Step 4: Save briefing to file
    os.makedirs("db", exist_ok=True)
    filename = f"db/briefing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(briefing)
    
    # Step 5: Print to terminal
    print(briefing)
    print(f"Briefing saved to: {filename}")
    
    return company_briefs, briefing


if __name__ == "__main__":
    run_synthesizer()
