# agent.py
import os
from dotenv import load_dotenv
from strands import Agent
from strands_tools.browser import AgentCoreBrowser

# Load your AWS credentials from .env file
load_dotenv()

# Initialize browser tool directly
browser_tool = AgentCoreBrowser(region=os.getenv('AWS_REGION', 'us-east-1'))

# Create the agent
def create_watch_agent():
    """
    Creates our watch tracking agent with AgentCore Browser
    """
    agent = Agent(
        model="global.anthropic.claude-sonnet-4-6",
        tools=[browser_tool.browser]
    )
    
    return agent

# Function to search for watches
def track_watch(watch_model: str):
    """
    Track prices for a specific watch model
    """
    print(f"\n🔍 Searching for: {watch_model}")
    print("⏳ This may take a moment...\n")
    
    agent = create_watch_agent()
    
    # Use eBay - simpler site
    prompt = f"""
Visit https://www.ebay.com and search for "{watch_model}".

Look at the first 3 results and tell me:
- Price
- Title

Keep it simple. If the site is slow or has issues, just tell me what you can see.
"""
    
    response = agent(prompt)
    return response

# Test
if __name__ == "__main__":
    print("✅ Starting browser test...\n")
    result = track_watch("Rolex Submariner 126610LN")
    print("\n📊 Result:")
    print(result)