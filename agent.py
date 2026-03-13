# agent.py
import os
from dotenv import load_dotenv
from strands import Agent
from custom_browser import search_watch_on_website

# Load your AWS credentials from .env file
load_dotenv()


# Create the agent with custom browser tool
def create_watch_agent():
    """
    Creates our watch tracking agent with YOUR custom browser
    """
    agent = Agent(
        model="global.anthropic.claude-sonnet-4-6",
        tools=[search_watch_on_website]  # Use your custom browser tool
    )
    
    return agent

# Function to search for watches
def track_watch(watch_model: str, website: str = "ebay"):
    """
    Track prices for a specific watch model
    """
    
    print(f"\n🔍 Searching for: {watch_model}")
    print(f"🌐 Website: {website}")
    print("⏳ This may take a moment...\n")
    
    agent = create_watch_agent()
    
    sites = {
        "ebay": "https://www.ebay.com",
        "jomashop": "https://www.jomashop.com",
    }
    
    site_url = sites.get(website.lower(), sites["ebay"])
    
    prompt = f"""
Use the search_watch_on_website tool to search for "{watch_model}" on {site_url}.

Extract the first 3 results with prices and conditions.
"""
    
    try:
        response = agent(prompt)
        result_text = str(response)
        return response
    except Exception as e:
        raise

# Test
if __name__ == "__main__":
    print("✅ Starting watch tracker with YOUR custom browser...\n")
    result = track_watch("Rolex Submariner 126610LN", "ebay")
    print("\n📊 Result:")
    print(result)
