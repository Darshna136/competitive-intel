import os
import json
import hashlib
import requests
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# Local file to store pricing snapshots
# Later this moves to PostgreSQL in Day 6
SNAPSHOTS_FILE = "db/price_snapshots.json"


def load_snapshots() -> dict:
    """
    Load previously saved pricing snapshots from local file.
    
    Snapshots = what pricing looked like last time we checked.
    We compare current pricing against this to detect changes.
    """
    try:
        with open(SNAPSHOTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_snapshot(company_name: str, pricing_text: str):
    """
    Save current pricing page as snapshot for future comparison.
    We use MD5 hash to quickly detect if anything changed.
    """
    snapshots = load_snapshots()
    snapshots[company_name] = {
        "content": pricing_text,
        "hash": hashlib.md5(pricing_text.encode()).hexdigest(),
        "captured_at": datetime.now().isoformat()
    }
    os.makedirs("db", exist_ok=True)
    with open(SNAPSHOTS_FILE, "w") as f:
        json.dump(snapshots, f, indent=2)


def scrape_pricing_page(company: dict) -> str:
    """
    Scrape the pricing page of a competitor website.
    
    Uses pricing_url from config if available,
    otherwise falls back to website/pricing.
    
    Args:
        company: competitor dict from competitors_config.py
    
    Returns:
        Clean text content of pricing page
    """
    website = company.get("website", "")
    pricing_path = company.get("pricing_url", f"{website}/pricing")
    pricing_url = f"https://{pricing_path}"
    
    print(f"   Scraping: {pricing_url}")
    
    headers = {
        # Pretend to be a real browser — some sites block bots
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(pricing_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"   Could not access {pricing_url} — status {response.status_code}")
            return ""
        
        # BeautifulSoup parses the raw HTML into readable structure
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove noise — scripts, styles, nav, footer
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        
        # Extract clean visible text
        text = soup.get_text(separator=" ", strip=True)
        
        # Limit to 3000 chars — enough for any pricing page
        return text[:3000]
        
    except Exception as e:
        print(f"   Error scraping {pricing_url}: {e}")
        return ""


def detect_changes(company_name: str, current_text: str) -> dict:
    """
    Compare current pricing page with last saved snapshot.
    
    Uses MD5 hashing — if hash changed, page content changed.
    Fast and reliable way to detect any modification.
    
    Args:
        company_name: company being checked
        current_text: freshly scraped pricing page text
    
    Returns:
        Dict with change_detected boolean and details
    """
    snapshots = load_snapshots()
    current_hash = hashlib.md5(current_text.encode()).hexdigest()
    
    if company_name not in snapshots:
        # First time scanning — save baseline, nothing to compare yet
        save_snapshot(company_name, current_text)
        return {
            "change_detected": False,
            "reason": "First time scanning — baseline saved",
            "previous_hash": None,
            "current_hash": current_hash
        }
    
    previous = snapshots[company_name]
    previous_hash = previous.get("hash", "")
    
    if current_hash == previous_hash:
        return {
            "change_detected": False,
            "reason": "No changes detected since last scan",
            "previous_hash": previous_hash,
            "current_hash": current_hash,
            "last_checked": previous.get("captured_at")
        }
    
    # Page changed — save new snapshot for next comparison
    save_snapshot(company_name, current_text)
    return {
        "change_detected": True,
        "reason": "Pricing page content has changed since last scan",
        "previous_hash": previous_hash,
        "current_hash": current_hash,
        "last_changed": previous.get("captured_at")
    }


def analyze_pricing_with_ai(company: dict, pricing_text: str, change_info: dict) -> dict:
    """
    Feed pricing page content to Llama for strategic analysis.
    
    AI extracts current plans, prices, and interprets
    what the pricing strategy means competitively.
    
    Args:
        company: competitor dict from config
        pricing_text: scraped pricing page content
        change_info: output from detect_changes()
    
    Returns:
        Strategic pricing intelligence report
    """
    company_name = company["name"]
    company_desc = company["description"]
    change_detected = change_info.get("change_detected", False)
    
    if not pricing_text:
        return {
            "competitor": company_name,
            "threat_level": "UNKNOWN",
            "pricing_summary": "Could not access pricing page",
            "change_detected": False,
            "plans_detected": [],
            "key_signals": [],
            "recommended_actions": [],
            "summary": "Pricing page could not be accessed"
        }
    
    system_prompt = """You are a competitive pricing analyst at a strategy firm.
    You analyze competitor pricing pages to extract strategic insights.
    
    Key principles you apply:
    - Price cuts = losing customers OR aggressive growth push
    - Price hikes = confident in retention OR targeting enterprise
    - New tiers = targeting new customer segments  
    - Free tier changes = growth strategy shift
    - Feature removal from lower tiers = pushing upgrades
    
    Always respond in valid JSON only. No markdown. No backticks."""
    
    change_context = (
        "IMPORTANT: A change was detected on this pricing page since last scan. Analyze what likely changed."
        if change_detected
        else "No change detected since last scan. Analyze current baseline pricing."
    )
    
    user_prompt = f"""
    Analyze the pricing page for {company_name}.
    Company context: {company_desc}
    {change_context}
    
    Pricing page content:
    {pricing_text[:2000]}
    
    Respond with ONLY this JSON:
    {{
        "competitor": "{company_name}",
        "plans_detected": [
            {{
                "plan_name": "name of pricing tier",
                "price": "price or Free or Custom",
                "target_customer": "who this plan targets"
            }}
        ],
        "pricing_strategy": "one sentence about their overall pricing approach",
        "change_detected": {str(change_detected).lower()},
        "change_analysis": "what likely changed and strategic reason (or No change detected)",
        "key_signals": [
            {{
                "signal": "specific pricing observation",
                "strategic_implication": "what this means competitively",
                "urgency": "HIGH/MEDIUM/LOW"
            }}
        ],
        "threat_level": "HIGH/MEDIUM/LOW",
        "threat_reasoning": "why this pricing is or is not threatening",
        "recommended_actions": [
            "specific pricing action your company should consider"
        ],
        "summary": "2-3 sentence executive summary of pricing intelligence"
    }}
    """
    
    print(f"   Llama is analyzing {company_name} pricing...")
    
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
            "change_detected": change_detected,
            "plans_detected": [],
            "key_signals": [],
            "recommended_actions": []
        }


def run_price_watcher(competitors: list) -> list:
    """
    Main function — runs Price Watcher for all competitors.
    
    Args:
        competitors: list of competitor dicts from config
    
    Returns:
        List of pricing intelligence reports
    """
    print("\n" + "="*50)
    print("PRICE WATCHER AGENT ACTIVATED")
    print("="*50)
    
    all_reports = []
    
    for company in competitors:
        company_name = company["name"]
        print(f"\nProcessing: {company_name}")
        
        # Step 1: Scrape pricing page using config URL
        pricing_text = scrape_pricing_page(company)
        
        # Step 2: Detect changes vs last snapshot
        change_info = detect_changes(company_name, pricing_text)
        
        # Step 3: AI analysis
        report = analyze_pricing_with_ai(company, pricing_text, change_info)
        
        # Step 4: Add metadata
        report["generated_at"] = datetime.now().isoformat()
        report["source"] = "price_watcher"
        report["change_info"] = change_info
        
        all_reports.append(report)
        
        change_flag = "⚠️  CHANGED" if change_info.get("change_detected") else "✅ No change"
        print(f"   {change_flag} — Threat: {report.get('threat_level', 'UNKNOWN')}")
    
    print("\n" + "="*50)
    print(f"PRICE WATCHER COMPLETE — {len(all_reports)} reports")
    print("="*50 + "\n")
    
    return all_reports


# ── TEST ─────────────────────────────────────────
if __name__ == "__main__":
    from competitors_config import COMPETITORS
    
    reports = run_price_watcher(COMPETITORS)
    
    for report in reports:
        print(f"\n{'='*60}")
        print(f"COMPETITOR:       {report.get('competitor')}")
        print(f"THREAT LEVEL:     {report.get('threat_level')}")
        print(f"CHANGE DETECTED:  {report.get('change_detected')}")
        print(f"PRICING STRATEGY: {report.get('pricing_strategy', 'N/A')}")
        print(f"\nPLANS DETECTED:")
        for plan in report.get('plans_detected', []):
            print(f"  - {plan.get('plan_name')}: {plan.get('price')}")
        print(f"\nSUMMARY: {report.get('summary', 'N/A')}")
        print(f"\nRECOMMENDED ACTIONS:")
        for action in report.get('recommended_actions', []):
            print(f"  -> {action}")
        print('='*60)