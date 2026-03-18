# run_agent.py
import sys
import json
import os
from dotenv import load_dotenv
from strands import Agent
from strands_tools.browser import AgentCoreBrowser
from bedrock_agentcore.tools.browser_client import BrowserClient
import urllib.parse

load_dotenv()

BROWSER_ID = os.getenv('BROWSER_TOOL_ARN').split('/')[-1]
REGION = os.getenv('AWS_REGION', 'us-east-1')

# Get instructions from command line argument
instructions = sys.argv[1]

# Patch to capture live view URL
from bedrock_agentcore.tools.browser_client import BrowserClient as ABC
session_capture = {}
original_create = AgentCoreBrowser.create_browser_session

async def patched(self):
    if not self._playwright:
        raise RuntimeError("Playwright not initialized")
    
    session_client = ABC(region=self.region)
    session_id = session_client.start(
        identifier=self.identifier,
        session_timeout_seconds=self.session_timeout
    )
    
    session_capture['session_id'] = session_id
    session_capture['live_view_url'] = session_client.generate_live_view_url(expires=300)
    
    # Print session info immediately so Streamlit can read it
    print(f"SESSION_ID:{session_id}", flush=True)
    print(f"LIVE_VIEW_URL:{session_capture['live_view_url']}", flush=True)
    
    cdp_url, cdp_headers = session_client.generate_ws_headers()
    browser = await self._playwright.chromium.connect_over_cdp(
        endpoint_url=cdp_url,
        headers=cdp_headers
    )
    return browser

AgentCoreBrowser.create_browser_session = patched

# Create browser and agent
browser_tool = AgentCoreBrowser(
    region=REGION,
    identifier=BROWSER_ID
)

agent = Agent(
    model="global.anthropic.claude-sonnet-4-6",
    tools=[browser_tool.browser]
)

# Run agent
response = agent(instructions)

# Print result as JSON so Streamlit can parse it
print(f"RESULT:{str(response)}", flush=True)