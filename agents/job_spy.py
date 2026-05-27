import os
import json
from datetime import datetime
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)


def search_job_postings(company_name: str) -> list:
    """
    Search for recent job postings from a company.
    
    We use Tavily to search job boards — LinkedIn, Indeed, Glassdoor.
    We're looking for patterns in WHAT roles they're hiring for,
    not just that they're hiring.
    
    Args:
        company_name: e.g. "Razorpay", "Microsoft", "Atlassian"
    
    Returns:
        List of search results about job postings
    """
    
    print(f"   Searching job postings for: {company_name}...")
    
    # We search multiple job-related queries to get better coverage
    queries = [
        f"{company_name} hiring engineers 2026 site:linkedin.com",
        f"{company_name} job openings engineering product 2026",
        f"{company_name} careers new roles machine learning AI"
    ]
    
    all_results = []
    
    for query in queries:
        results = tavily.search(
            query=query,
            max_results=3,
            search_depth="basic"
        )
        all_results.extend(results.get("results", []))
    
    print(f"   Found {len(all_results)} job related results")
    return all_results


def analyze_jobs_with_ai(company_name: str, job_results: list) -> dict:
    """
    Feed job posting data to Llama and extract hiring patterns.
    
    The AI looks for:
    - Which departments are hiring most?
    - What tech stack appears repeatedly?
    - What product areas are mentioned?
    - What does this predict about their roadmap?
    
    Args:
        company_name: company being analyzed
        job_results: raw search results from search_job_postings()
    
    Returns:
        Strategic intelligence report about hiring patterns
    """
    
    if not job_results:
        return {
            "competitor": company_name,
            "threat_level": "LOW",
            "hiring_patterns": [],
            "predicted_roadmap": "No job data found",
            "key_signals": [],
            "recommended_actions": []
        }
    
    # Combine all job results into readable text for AI
    jobs_text = ""
    for i, result in enumerate(job_results, 1):
        jobs_text += f"""
        Result {i}: {result.get('title', 'No title')}
        Content: {result.get('content', '')[:400]}
        ---"""
    
    system_prompt = """You are a competitive intelligence analyst who specializes 
    in reading hiring patterns to predict company roadmaps.
    
    Your key insight: Companies hire 3-6 months before launching features.
    Hiring patterns = future product roadmap.
    
    Look for:
    - Clusters of similar roles (10 ML engineers = AI feature coming)
    - New tech stacks appearing (hiring Rust engineers = performance overhaul)
    - New product areas (hiring payments engineers = payments feature)
    - Seniority patterns (hiring senior = mature product, junior = scaling)
    
    Always respond in valid JSON only. No markdown. No backticks."""
    
    user_prompt = f"""
    Analyze these job posting results for {company_name}.
    Extract hiring patterns and predict their product roadmap.
    
    {jobs_text}
    
    Respond with ONLY this JSON:
    {{
        "competitor": "{company_name}",
        "hiring_patterns": [
            {{
                "pattern": "what type of roles they are hiring",
                "volume": "how many/how aggressively",
                "implication": "what product/feature this predicts"
            }}
        ],
        "predicted_roadmap": "one paragraph about what they will likely launch in next 6 months based on hiring",
        "key_signals": [
            {{
                "signal": "specific hiring observation",
                "strategic_implication": "what this means for competitors",
                "urgency": "HIGH/MEDIUM/LOW"
            }}
        ],
        "threat_level": "HIGH/MEDIUM/LOW",
        "threat_reasoning": "why this hiring pattern is or isn't threatening",
        "recommended_actions": [
            "specific action your company should take"
        ],
        "summary": "2-3 sentence executive summary of hiring intelligence"
    }}
    """
    
    print(f"   Llama is analyzing {company_name} hiring patterns...")
    
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
        result = json.loads(raw_text)
        return result
    except json.JSONDecodeError:
        return {
            "competitor": company_name,
            "raw_analysis": response.content,
            "threat_level": "UNKNOWN",
            "hiring_patterns": [],
            "recommended_actions": []
        }


def run_job_spy(competitors: list) -> list:
    """
    Main function — runs Job Spy pipeline for all competitors.
    
    Args:
        competitors: list of company names
    
    Returns:
        List of hiring intelligence reports
    """
    
    print("\n" + "="*50)
    print("JOB SPY AGENT ACTIVATED")
    print("="*50)
    
    all_reports = []
    
    for company in competitors:
        print(f"\nProcessing: {company}")
        
        # Step 1: Search job postings
        job_results = search_job_postings(company)
        
        # Step 2: AI analysis
        report = analyze_jobs_with_ai(company, job_results)
        
        # Step 3: Add metadata
        report["generated_at"] = datetime.now().isoformat()
        report["source"] = "job_spy"
        
        all_reports.append(report)
        print(f"   Report done — Threat: {report.get('threat_level', 'UNKNOWN')}")
    
    print("\n" + "="*50)
    print(f"JOB SPY COMPLETE — {len(all_reports)} reports")
    print("="*50 + "\n")
    
    return all_reports


# ── TEST ─────────────────────────────────────────
if __name__ == "__main__":
    from competitors_config import COMPETITORS
    company_names = [c["name"] for c in COMPETITORS]
    reports = run_job_spy(company_names)
    
    for report in reports:
        print(f"\n{'='*60}")
        print(f"COMPETITOR: {report.get('competitor')}")
        print(f"THREAT LEVEL: {report.get('threat_level')}")
        print(f"\nPREDICTED ROADMAP:")
        print(f"  {report.get('predicted_roadmap', 'N/A')}")
        print(f"\nHIRING PATTERNS:")
        for pattern in report.get('hiring_patterns', []):
            print(f"  - {pattern.get('pattern')}")
            print(f"    Predicts: {pattern.get('implication')}")
        print(f"\nKEY SIGNALS:")
        for signal in report.get('key_signals', []):
            print(f"  - {signal.get('signal')}")
            print(f"    -> {signal.get('strategic_implication')}")
        print(f"\nRECOMMENDED ACTIONS:")
        for action in report.get('recommended_actions', []):
            print(f"  -> {action}")
        print('='*60)