# streamlit_app.py
import streamlit as st
import os
import urllib.parse
from dotenv import load_dotenv
from strands import Agent
from strands_tools.browser import AgentCoreBrowser
from bedrock_agentcore.tools.browser_client import BrowserClient
from datetime import datetime

load_dotenv()

BROWSER_ID = os.getenv('BROWSER_TOOL_ARN').split('/')[-1]
REGION = os.getenv('AWS_REGION', 'us-east-1')

# Page config
st.set_page_config(
    page_title="AgentCore Browser",
    page_icon="🌐",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .log-box {
        background-color: #0e1117;
        padding: 1rem;
        border-radius: 10px;
        font-family: monospace;
        font-size: 0.85rem;
        height: 300px;
        overflow-y: auto;
        border: 1px solid #1f77b4;
    }
    .log-entry { 
        color: #00ff00; 
        margin: 0.2rem 0; 
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🌐 AgentCore Browser</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#666;'>Generic AI-powered browser agent - write your own instructions!</p>", unsafe_allow_html=True)

# Initialize session state
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'live_view_url' not in st.session_state:
    st.session_state.live_view_url = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'results' not in st.session_state:
    st.session_state.results = None

# Helper functions
def add_log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    emoji = {
        "INFO": "📊",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "BROWSER": "🌐"
    }.get(level, "📊")
    st.session_state.logs.append(f"{emoji} [{timestamp}] {message}")
    if len(st.session_state.logs) > 50:
        st.session_state.logs = st.session_state.logs[-50:]

def display_logs(placeholder):
    html = "<div class='log-box'>"
    for log in reversed(st.session_state.logs):
        html += f"<div class='log-entry'>{log}</div>"
    html += "</div>"
    placeholder.markdown(html, unsafe_allow_html=True)

# Patch AgentCoreBrowser to capture session
# Use a simple dict to share data between async and Streamlit
session_capture = {}

def patch_browser(browser_tool):
    async def patched(self):
        from bedrock_agentcore.tools.browser_client import BrowserClient as ABC

        if not self._playwright:
            raise RuntimeError("Playwright not initialized")

        session_client = ABC(region=self.region)
        session_id = session_client.start(
            identifier=self.identifier,
            session_timeout_seconds=self.session_timeout
        )

        # Store in simple dict (no Streamlit calls here!)
        session_capture['session_id'] = session_id
        session_capture['live_view_url'] = session_client.generate_live_view_url(expires=300)
        session_capture['client'] = session_client

        # Connect via CDP
        cdp_url, cdp_headers = session_client.generate_ws_headers()
        browser = await self._playwright.chromium.connect_over_cdp(
            endpoint_url=cdp_url,
            headers=cdp_headers
        )

        return browser

    AgentCoreBrowser.create_browser_session = patched
    return session_capture

# ─── LAYOUT ───────────────────────────────────────────────────────────────────

# Top row: Instructions + Config
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📝 Agent Instructions")
    
    # Default instructions
    default_instructions = """Go to https://www.ebay.com and search for "Rolex Submariner 126610LN".

Find the first 3 listings and extract:
- Title
- Price
- Condition
- Seller

Return results in a clear table format."""
    
    instructions = st.text_area(
        "Write your instructions for the browser agent:",
        value=default_instructions,
        height=200,
        placeholder="Tell the agent what to do in the browser..."
    )

with col_right:
    st.subheader("⚙️ Configuration")
    st.info(f"🔧 **Browser:** `{BROWSER_ID}`")
    st.info(f"🤖 **Model:** `claude-sonnet-4-6`")
    st.info(f"🌍 **Region:** `{REGION}`")
    
    if st.session_state.session_id:
        st.success(f"**Session:** `{st.session_state.session_id[:20]}...`")

# Run button
run_button = st.button("🚀 Run Agent", type="primary", use_container_width=True)

st.divider()
st.divider()

# Activity Log - full width
st.subheader("📋 Activity Log")
log_placeholder = st.empty()

# Live Browser View - full width below
st.subheader("🖥️ Live Browser View")
view_placeholder = st.empty()

result_placeholder = st.empty()

# ─── DISPLAY FUNCTIONS ────────────────────────────────────────────────────────

def show_live_view(url=None, status="idle"):
    if status == "idle":
        view_placeholder.markdown("""
        <div style='background:#111; border:1px solid #1f77b4; border-radius:10px; 
                    height:400px; display:flex; align-items:center; justify-content:center;'>
            <p style='color:#666; font-family:monospace;'>
                🌐 Browser view will appear here when agent runs
            </p>
        </div>
        """, unsafe_allow_html=True)

    elif status == "active" and url:
        encoded = urllib.parse.quote(url, safe='')
        local_url = f"http://localhost:8080/dcv_viewer.html?url={encoded}"
        view_placeholder.markdown(f"""
        <div style='background:#000; border:1px solid #00ff00; border-radius:10px; overflow:hidden;'>
            <iframe 
                src="{local_url}"
                width="100%" 
                height="900px" 
                frameborder="0"
                style="display:block;"
                scrolling="no"
            ></iframe>
        </div>
        <p style='color:#666; font-size:0.8rem; margin-top:0.3rem;'>
            🟢 Session: {st.session_state.session_id}
        </p>
        """, unsafe_allow_html=True)

    elif status == "completed":
        view_placeholder.markdown(f"""
        <div style='background:#111; border:1px solid #00ff00; border-radius:10px; 
                    height:400px; display:flex; align-items:center; justify-content:center;
                    flex-direction:column; gap:1rem;'>
            <p style='color:#00ff00; font-family:monospace; font-size:1.2rem;'>
                ✅ Session Completed
            </p>
            <p style='color:#666; font-family:monospace; font-size:0.8rem;'>
                Session: {st.session_state.session_id}
            </p>
            <a href='https://us-east-1.console.aws.amazon.com/s3/buckets/watch-watcher' 
               target='_blank'
               style='color:#1f77b4; font-family:monospace;'>
                📹 View Recording in S3 →
            </a>
        </div>
        """, unsafe_allow_html=True)

# ─── HANDLE RUN ───────────────────────────────────────────────────────────────

if run_button:
    if not instructions.strip():
        st.error("⚠️ Please enter instructions for the agent")
    else:
        # Reset state
        st.session_state.logs = []
        st.session_state.live_view_url = None
        st.session_state.session_id = None

        add_log("Starting agent run...")
        display_logs(log_placeholder)
        show_live_view(status="idle")

        try:
            import subprocess
            import threading

            # Build env with OTEL vars
            env = os.environ.copy()
            env['OTEL_PYTHON_DISTRO'] = 'aws_distro'
            env['OTEL_PYTHON_CONFIGURATOR'] = 'aws_configurator'
            env['OTEL_EXPORTER_OTLP_PROTOCOL'] = 'http/protobuf'
            env['OTEL_TRACES_EXPORTER'] = 'otlp'
            env['OTEL_EXPORTER_OTLP_LOGS_HEADERS'] = 'x-aws-log-group=/agentcore/watch-tracker,x-aws-log-stream=watch-tracker-agent,x-aws-metric-namespace=bedrock-agentcore'
            env['OTEL_RESOURCE_ATTRIBUTES'] = 'service.name=watch-tracker-agent'
            env['AGENT_OBSERVABILITY_ENABLED'] = 'true'

            add_log("Launching agent process with observability...")
            display_logs(log_placeholder)

            # Run agent as subprocess with opentelemetry-instrument
            process = subprocess.Popen(
                ['opentelemetry-instrument', 'python', 'run_agent.py', instructions],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                bufsize=1  # Line buffered
            )

            result_text = ""
            live_view_shown = False

            # Read output line by line
            with st.spinner("🤖 Agent is working..."):
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    # Parse special output lines
                    if line.startswith("SESSION_ID:"):
                        session_id = line.replace("SESSION_ID:", "")
                        st.session_state.session_id = session_id
                        add_log(f"Session: {session_id}", "SUCCESS")
                        display_logs(log_placeholder)

                    elif line.startswith("LIVE_VIEW_URL:"):
                        live_view_url = line.replace("LIVE_VIEW_URL:", "")
                        st.session_state.live_view_url = live_view_url
                        add_log("Live view ready!", "SUCCESS")
                        display_logs(log_placeholder)
                        show_live_view(url=live_view_url, status="active")
                        live_view_shown = True

                    elif line.startswith("RESULT:"):
                        result_text = line.replace("RESULT:", "")
                        add_log("Agent completed!", "SUCCESS")

                    else:
                        # Show other output as logs
                        add_log(line, "INFO")
                        display_logs(log_placeholder)

            process.wait()

            # Show results
            show_live_view(status="completed")
            display_logs(log_placeholder)

            if result_text:
                st.divider()
                st.subheader("🎯 Results")
                st.markdown(result_text)

        except Exception as e:
            add_log(f"Error: {str(e)}", "ERROR")
            display_logs(log_placeholder)
            st.error(f"❌ Error: {str(e)}")

else:
    show_live_view(status="idle")
    display_logs(log_placeholder)

# Footer
st.divider()
st.markdown("""
<p style='text-align:center; color:#444; font-size:0.8rem;'>
    Powered by AWS Bedrock AgentCore | Strands Agents | Amazon DCV
</p>
""", unsafe_allow_html=True)