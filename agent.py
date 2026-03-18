# agent.py
import os
from dotenv import load_dotenv
from strands import Agent
from strands_tools.browser import AgentCoreBrowser
from bedrock_agentcore.tools.browser_client import BrowserClient

load_dotenv()

BROWSER_ID = os.getenv('BROWSER_TOOL_ARN').split('/')[-1]
REGION = os.getenv('AWS_REGION', 'us-east-1')

# Step 1: Start browser session via BrowserClient to get live view URL
browser_client = BrowserClient(region=REGION)
browser_client.start(identifier=BROWSER_ID)

print(f"✅ Browser session started: {browser_client.session_id}")

# Step 2: Get live view URL
live_view_url = browser_client.generate_live_view_url(expires=300)
print(f"🖥️  Live view URL: {live_view_url[:80]}...")

# Step 3: Create AgentCoreBrowser using the SAME session
browser_tool = AgentCoreBrowser(
    region=REGION,
    identifier=BROWSER_ID
)

# Step 4: Create agent with browser tool
agent = Agent(
    model="global.anthropic.claude-sonnet-4-6",
    tools=[browser_tool.browser]
)

# Step 5: Run agent
response = agent("Go to https://www.ebay.com and search for Rolex Submariner 126610LN. Give me the first 3 listings with prices.")

print(response)

# Step 6: Stop session
browser_client.stop()
print("✅ Session stopped")