import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

# GitHub API — lets us read public repo data without scraping
# Free, no cost, just needs your token for higher rate limits
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Headers for every GitHub API request
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Our AI brain — same as news_hawk
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY
)


def get_company_repos(org_name: str) -> list:
    """
    Fetch all public repositories of a GitHub organization.
    
    GitHub organizations are company accounts — microsoft, atlassian, 
    google, etc. all have public org accounts with their open source code.
    
    Args:
        org_name: GitHub org username e.g. "microsoft", "atlassian"
    
    Returns:
        List of repos with name, stars, last updated, description
    """
    
    print(f"   Fetching repos for: {org_name}...")
    
    # GitHub API endpoint for org repos
    # sorted by push date = most recently updated first
    url = f"https://api.github.com/orgs/{org_name}/repos"
    params = {
        "sort": "pushed",      # most recently active first
        "direction": "desc",
        "per_page": 30,        # top 30 repos
        "type": "public"       # only public repos
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code != 200:
        print(f"   Error fetching repos: {response.status_code}")
        return []
    
    repos = response.json()
    print(f"   Found {len(repos)} public repos")
    return repos


def get_recent_commits(org_name: str, repo_name: str, days_back: int = 7) -> int:
    """
    Count how many commits a repo got in the last N days.
    
    A sudden spike in commits = team is working hard on something.
    This is the key signal we're looking for.
    
    Args:
        org_name: GitHub org e.g. "microsoft"
        repo_name: specific repo e.g. "vscode"
        days_back: how many days to look back
    
    Returns:
        Number of commits in that time period
    """
    
    # Calculate date N days ago in GitHub's expected format
    since_date = (datetime.now() - timedelta(days=days_back)).isoformat() + "Z"
    
    url = f"https://api.github.com/repos/{org_name}/{repo_name}/commits"
    params = {
        "since": since_date,
        "per_page": 100   # max per page
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code != 200:
        return 0
    
    commits = response.json()
    
    # If it's a list, return count. If error object, return 0
    if isinstance(commits, list):
        return len(commits)
    return 0


def find_active_repos(org_name: str) -> list:
    """
    Find the most actively developed repos for a company.
    
    We get all repos, count recent commits for each,
    and return the top 5 most active ones.
    
    Args:
        org_name: GitHub org name
    
    Returns:
        List of top 5 most active repos with commit counts
    """
    
    repos = get_company_repos(org_name)
    
    if not repos:
        return []
    
    active_repos = []
    
    # Check commit activity for each repo
    # We only check top 15 to avoid hitting GitHub rate limits
    for repo in repos[:15]:
        repo_name = repo.get("name", "")
        commits_this_week = get_recent_commits(org_name, repo_name)
        
        active_repos.append({
            "name": repo_name,
            "description": repo.get("description", "No description"),
            "stars": repo.get("stargazers_count", 0),
            "commits_this_week": commits_this_week,
            "language": repo.get("language", "Unknown"),
            "last_pushed": repo.get("pushed_at", "")
        })
    
    # Sort by most commits this week = most active first
    active_repos.sort(key=lambda x: x["commits_this_week"], reverse=True)
    
    # Return top 5 most active
    return active_repos[:5]


def analyze_github_activity(org_name: str, active_repos: list) -> dict:
    """
    Feed GitHub activity data to Llama and get strategic insights.
    
    The AI looks at which repos are active and interprets
    what the company might be building or focusing on.
    
    Args:
        org_name: company name
        active_repos: list of active repos from find_active_repos()
    
    Returns:
        Strategic intelligence report
    """
    
    if not active_repos:
        return {
            "competitor": org_name,
            "threat_level": "LOW",
            "key_signals": [],
            "recommended_actions": [],
            "summary": "No public GitHub activity found"
        }
    
    # Format repo data for the AI to read
    repos_text = ""
    for repo in active_repos:
        repos_text += f"""
        Repo: {repo['name']}
        Description: {repo['description']}
        Commits this week: {repo['commits_this_week']}
        Stars: {repo['stars']}
        Primary language: {repo['language']}
        ---"""
    
    system_prompt = """You are a senior competitive intelligence analyst 
    specializing in technology companies. You analyze GitHub activity to 
    understand what products and features companies are secretly building.
    
    High commit counts = active development = something is being built.
    New repos = new product or major initiative.
    Stars spike = community excitement = important project.
    
    Always respond in valid JSON only. No markdown. No backticks."""
    
    user_prompt = f"""
    Analyze this GitHub activity for {org_name} from the last 7 days.
    
    {repos_text}
    
    Based on which repos are most active and what they're about,
    what is {org_name} currently building or focusing on?
    
    Respond with ONLY this JSON:
    {{
        "competitor": "{org_name}",
        "most_active_repo": "repo name",
        "what_they_are_building": "one sentence about what this activity suggests",
        "key_signals": [
            {{
                "signal": "specific observation about repo activity",
                "strategic_implication": "what this means competitively",
                "urgency": "HIGH/MEDIUM/LOW"
            }}
        ],
        "threat_level": "HIGH/MEDIUM/LOW",
        "threat_reasoning": "why this activity level is or isn't threatening",
        "recommended_actions": [
            "specific action to take based on this intel"
        ],
        "summary": "2-3 sentence executive summary"
    }}
    """
    
    print(f"   Llama is analyzing {org_name} GitHub activity...")
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    # Parse JSON response
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
            "competitor": org_name,
            "raw_analysis": response.content,
            "threat_level": "UNKNOWN",
            "key_signals": [],
            "recommended_actions": []
        }


def run_github_watcher(competitors: list) -> list:
    """
    Main function — runs full GitHub Watcher pipeline.
    
    Args:
        competitors: list of GitHub org names e.g. ["microsoft", "atlassian"]
    
    Returns:
        List of intelligence reports
    """
    
    print("\n" + "="*50)
    print("GITHUB WATCHER AGENT ACTIVATED")
    print("="*50)
    
    all_reports = []
    
    for org_name in competitors:
        print(f"\nProcessing: {org_name}")
        
        # Step 1: Find most active repos
        print(f"   Finding active repos...")
        active_repos = find_active_repos(org_name)
        
        # Step 2: Analyze with AI
        report = analyze_github_activity(org_name, active_repos)
        
        # Step 3: Add metadata
        report["generated_at"] = datetime.now().isoformat()
        report["source"] = "github_watcher"
        report["active_repos"] = active_repos
        
        all_reports.append(report)
        print(f"   Report done — Threat: {report.get('threat_level', 'UNKNOWN')}")
    
    print("\n" + "="*50)
    print(f"GITHUB WATCHER COMPLETE — {len(all_reports)} reports")
    print("="*50 + "\n")
    
    return all_reports


# ── TEST ─────────────────────────────────────────
if __name__ == "__main__":
    from competitors_config import COMPETITORS
    github_orgs = [c["github_org"] for c in COMPETITORS]
    reports = run_github_watcher(github_orgs)
    
    for report in reports:
        print(f"\n{'='*60}")
        print(f"COMPETITOR: {report.get('competitor')}")
        print(f"THREAT LEVEL: {report.get('threat_level')}")
        print(f"BUILDING: {report.get('what_they_are_building', 'N/A')}")
        print(f"SUMMARY: {report.get('summary', 'N/A')}")
        print(f"\nKEY SIGNALS:")
        for signal in report.get('key_signals', []):
            print(f"  - {signal.get('signal')}")
            print(f"    -> {signal.get('strategic_implication')}")
        print(f"\nRECOMMENDED ACTIONS:")
        for action in report.get('recommended_actions', []):
            print(f"  -> {action}")
        print(f"\nMOST ACTIVE REPOS:")
        for repo in report.get('active_repos', [])[:3]:
            print(f"  {repo['name']}: {repo['commits_this_week']} commits this week")
        print('='*60)
