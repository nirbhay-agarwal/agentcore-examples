# agent.py
import os
import urllib.parse
from dotenv import load_dotenv
from strands import Agent
from strands_tools.browser import AgentCoreBrowser
from bedrock_agentcore.tools.browser_client import BrowserClient

load_dotenv()

BROWSER_ID = os.getenv('BROWSER_TOOL_ARN').split('/')[-1]
REGION = os.getenv('AWS_REGION', 'us-east-1')

# Patch AgentCoreBrowser to capture the session client
original_create_session = AgentCoreBrowser.create_browser_session
session_client_ref = {}

async def patched_create_browser_session(self):
    """Intercept session creation to capture live view URL"""
    from bedrock_agentcore.tools.browser_client import BrowserClient as AgentCoreBrowserClient
    
    if not self._playwright:
        raise RuntimeError("Playwright not initialized")

    # Create session client
    session_client = AgentCoreBrowserClient(region=self.region)
    session_id = session_client.start(
        identifier=self.identifier, 
        session_timeout_seconds=self.session_timeout
    )

    print(f"✅ Browser session started: {session_id}")

    # Generate and store live view URL
    live_view_url = session_client.generate_live_view_url(expires=300)
    session_client_ref['session_id'] = session_id
    session_client_ref['live_view_url'] = live_view_url
    session_client_ref['client'] = session_client

    encoded_url = urllib.parse.quote(live_view_url, safe='')
    print(f"\n🖥️  Open this in your browser:")
    print(f"http://localhost:8080/dcv_viewer.html?url={encoded_url}\n")

    # Continue with CDP connection
    cdp_url, cdp_headers = session_client.generate_ws_headers()
    browser = await self._playwright.chromium.connect_over_cdp(
        endpoint_url=cdp_url, 
        headers=cdp_headers
    )

    return browser

# Apply patch
AgentCoreBrowser.create_browser_session = patched_create_browser_session

# Initialize browser tool with YOUR custom browser
browser_tool = AgentCoreBrowser(
    region=REGION,
    identifier=BROWSER_ID
)

# Create agent
agent = Agent(
    model="global.anthropic.claude-sonnet-4-6",
    tools=[browser_tool.browser]
)

# Run agent
response = agent("Go to https://www.ebay.com and search for Rolex Submariner 126610LN. Give me the first 3 listings with prices.")

print(response)