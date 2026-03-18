# run_agent.py
import sys
import os
from dotenv import load_dotenv
from strands import Agent
from strands_tools.browser import AgentCoreBrowser
from bedrock_agentcore.tools.browser_client import BrowserClient as ABC

load_dotenv()

BROWSER_ID = os.getenv('BROWSER_TOOL_ARN').split('/')[-1]
REGION = os.getenv('AWS_REGION', 'us-east-1')

# Get instructions from command line argument
instructions = sys.argv[1]

# Track ALL sessions created
session_capture = {
    'sessions': [],
    'session_id': None,
    'live_view_url': None
}

async def patched(self):
    if not self._playwright:
        raise RuntimeError("Playwright not initialized")
    
    session_client = ABC(region=self.region)
    session_id = session_client.start(
        identifier=self.identifier,
        session_timeout_seconds=self.session_timeout
    )
    
    # Track ALL sessions
    session_capture['sessions'].append(session_client)
    session_capture['session_id'] = session_id
    session_capture['live_view_url'] = session_client.generate_live_view_url(expires=300)
    
    # Only print live view URL for first session
    if len(session_capture['sessions']) == 1:
        print(f"SESSION_ID:{session_id}", flush=True)
        print(f"LIVE_VIEW_URL:{session_capture['live_view_url']}", flush=True)
    else:
        print(f"NEW_SESSION:{session_id}", flush=True)
    
    cdp_url, cdp_headers = session_client.generate_ws_headers()
    browser = await self._playwright.chromium.connect_over_cdp(
        endpoint_url=cdp_url,
        headers=cdp_headers
    )
    return browser

# Apply patch
AgentCoreBrowser.create_browser_session = patched

# Create browser and agent
browser_tool = AgentCoreBrowser(
    region=REGION,
    identifier=BROWSER_ID
)

agent = Agent(
    model="global.anthropic.claude-sonnet-4-6",
    tools=[browser_tool.browser],
    trace_attributes={
        "session.id": f"browser-session-{os.urandom(4).hex()}",
        "tags": ["browser", "watch-tracker"],
    }
)

# Run agent
response = agent(instructions)

# Print result with markers
print("", flush=True)
print("RESULT_START", flush=True)
print(str(response), flush=True)
print("RESULT_END", flush=True)
print("", flush=True)

# Stop ALL browser sessions
total = len(session_capture.get('sessions', []))
print(f"Stopping {total} browser session(s)...", flush=True)

for i, client in enumerate(session_capture.get('sessions', [])):
    try:
        client.stop()
        print(f"SESSION_STOPPED:session {i+1} of {total} stopped", flush=True)
    except Exception as e:
        print(f"SESSION_STOP_ERROR:session {i+1} - {str(e)}", flush=True)

print("All sessions terminated", flush=True)