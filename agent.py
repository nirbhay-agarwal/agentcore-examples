# agent.py
import os
from dotenv import load_dotenv
from strands import Agent
from strands_tools.browser import AgentCoreBrowser

# Load your AWS credentials
load_dotenv()

# Use the built-in AgentCoreBrowser (it handles everything automatically)
browser_tool = AgentCoreBrowser(region=os.getenv('AWS_REGION', 'us-east-1'))

def create_watch_agent():
    """Creates agent with working browser"""
    agent = Agent(
        model="global.anthropic.claude-sonnet-4-6",
        tools=[browser_tool.browser]  # This tool actually browses
    )
    return agent

def track_watch(watch_model: str, website: str = "ebay"):
    print(f"\n🔍 Searching for: {watch_model}")
    print(f"🌐 Website: {website}\n")
    
    agent = create_watch_agent()
    
    sites = {
        "ebay": "https://www.ebay.com",
        "jomashop": "https://www.jomashop.com",
    }
    
    site_url = sites.get(website.lower(), sites["ebay"])
    
    prompt = f"""
Go to {site_url} and search for "{watch_model}".

Find the first 3 listings and extract:
- Title
- Price
- Condition

Give me real data from the actual website.
"""
    
    response = agent(prompt)
    return response

if __name__ == "__main__":
    result = track_watch("Rolex Submariner 126610LN", "ebay")
    print("\n📊 Result:")
    print(result)