import os
import json
from datetime import datetime
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

claude = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def search_competitor_news(competitor_name: str, days_back: int = 7) -> list:
    print(f"Searching news for: {competitor_name}...")
    results = tavily.search(
        query=f"{competitor_name} company news product launch funding 2026",
        max_results=5,
        search_depth="advanced",
        include_raw_content=True
    )
    articles = results.get("results", [])
    print(f"   Found {len(articles)} articles")
    return articles

def analyze_news_with_claude(competitor_name: str, articles: list) -> dict:
    if not articles:
        return {
            "competitor": competitor_name,
            "insights": "No recent news found",
            "threat_level": "LOW",
            "key_signals": [],
            "recommendations": []
        }
    articles_text = ""
    for i, article in enumerate(articles, 1):
        articles_text += f"""
        Article {i}: {article.get('title', 'No title')}
        URL: {article.get('url', '')}
        Content: {article.get('content', '')[:500]}
        ---
        """
    system_prompt = """You are a senior competitive intelligence analyst at a top strategy consulting firm.
    Your job is to read news about competitors and extract STRATEGIC insights not summaries.
    Always respond in valid JSON format only. No extra text before or after the JSON."""

    user_prompt = f"""
    Analyze these recent news articles about {competitor_name} and extract strategic intelligence.
    {articles_text}
    Respond with ONLY this JSON structure (no markdown, no backticks, just raw JSON):
    {{
        "competitor": "{competitor_name}",
        "key_signals": [
            {{
                "signal": "one sentence describing what happened",
                "strategic_implication": "what this means for competitors",
                "urgency": "HIGH/MEDIUM/LOW"
            }}
        ],
        "threat_level": "HIGH/MEDIUM/LOW",
        "threat_reasoning": "one sentence explaining the threat level",
        "recommended_actions": [
            "specific action your company should take"
        ],
        "summary": "2-3 sentence executive summary of the competitive situation"
    }}
    """
    print(f"Gemini is analyzing {competitor_name} news...")
    response = claude.invoke([
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
        print(f"   Could not parse response, returning raw text")
        return {
            "competitor": competitor_name,
            "raw_analysis": response.content,
            "threat_level": "UNKNOWN",
            "key_signals": [],
            "recommended_actions": []
        }

def run_news_hawk(competitors: list) -> list:
    print("\n" + "="*50)
    print("NEWS HAWK AGENT ACTIVATED")
    print("="*50)
    all_reports = []
    for competitor in competitors:
        print(f"\nProcessing: {competitor}")
        articles = search_competitor_news(competitor)
        report = analyze_news_with_claude(competitor, articles)
        report["generated_at"] = datetime.now().isoformat()
        report["source"] = "news_hawk"
        all_reports.append(report)
        print(f"   Report generated - Threat Level: {report.get('threat_level', 'UNKNOWN')}")
    print("\n" + "="*50)
    print(f"NEWS HAWK COMPLETE - {len(all_reports)} reports generated")
    print("="*50 + "\n")
    return all_reports

if __name__ == "__main__":
    from competitors_config import COMPETITORS
    company_names = [c["name"] for c in COMPETITORS]
    reports = run_news_hawk(company_names)
    for report in reports:
        print(f"\n{'='*60}")
        print(f"COMPETITOR: {report.get('competitor')}")
        print(f"THREAT LEVEL: {report.get('threat_level')}")
        print(f"SUMMARY: {report.get('summary', 'N/A')}")
        print(f"\nKEY SIGNALS:")
        for signal in report.get('key_signals', []):
            print(f"  - {signal.get('signal')}")
            print(f"    -> {signal.get('strategic_implication')}")
        print(f"\nRECOMMENDED ACTIONS:")
        for action in report.get('recommended_actions', []):
            print(f"  -> {action}")
        print('='*60)
