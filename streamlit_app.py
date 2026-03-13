# streamlit_app.py
import streamlit as st
import os
from dotenv import load_dotenv
from agent import create_watch_agent
from custom_browser import CustomBrowserTool
import time
from datetime import datetime
import urllib.parse

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Watch Price Tracker",
    page_icon="⌚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-size: 1.2rem;
        padding: 0.5rem;
        border-radius: 10px;
    }
    .log-box {
        background-color: #0e1117;
        padding: 1rem;
        border-radius: 10px;
        font-family: monospace;
        font-size: 0.9rem;
        max-height: 400px;
        overflow-y: auto;
        color: #00ff00;
        border: 2px solid #1f77b4;
    }
    .log-entry {
        margin: 0.3rem 0;
        color: #00ff00;
    }
    .browser-view {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #1f77b4;
        min-height: 400px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">⌚ Watch Price Tracker</h1>', unsafe_allow_html=True)
st.markdown("### Track luxury watch prices across multiple websites with AI-powered browsing")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Browser tool info
    browser_id = os.getenv('BROWSER_TOOL_ARN', '').split('/')[-1]
    st.info(f"🔧 **Browser Tool:**\n`{browser_id}`")
    
    # Log group info
    log_group = f'/aws/vendedlogs/bedrock-agentcore/browser-custom/USAGE_LOGS/{browser_id}'
    st.info(f"📊 **Logs:**\n`{log_group}`")
    
    # S3 bucket
    st.info(f"📹 **Recordings:**\n`s3://watch-watcher/`")
    
    st.divider()
    
    # Session info
    if 'session_count' not in st.session_state:
        st.session_state.session_count = 0
    
    st.metric("Sessions Created", st.session_state.session_count)

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔍 Search for a Watch")
    
    # Watch model input
    watch_model = st.text_input(
        "Watch Model",
        value="Rolex Submariner 126610LN",
        placeholder="Enter watch model (e.g., Rolex Submariner 126610LN)"
    )
    
    # Website selection
    website = st.selectbox(
        "Website to Search",
        ["eBay", "Jomashop"],
        index=0
    )
    
    # Search button
    search_button = st.button("🚀 Start Search", type="primary")

with col2:
    st.subheader("📊 Quick Stats")
    st.metric("Browser Status", "🟢 Ready")
    st.metric("Model", "Claude 3.5 Sonnet")

# Create two columns for logs and browser view
st.divider()
col_logs, col_browser = st.columns([1, 1])

with col_logs:
    st.subheader("📋 Live Activity Log")
    log_placeholder = st.empty()

with col_browser:
    st.subheader("🖥️ Live Browser View")
    browser_placeholder = st.empty()

result_placeholder = st.empty()

# Initialize session state
if 'logs' not in st.session_state:
    st.session_state.logs = []

if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None

# Function to add log
def add_log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    emoji = "📊" if level == "INFO" else "✅" if level == "SUCCESS" else "❌" if level == "ERROR" else "🔧"
    log_entry = f"{emoji} [{timestamp}] {message}"
    st.session_state.logs.append(log_entry)
    
    # Keep only last 20 logs
    if len(st.session_state.logs) > 20:
        st.session_state.logs = st.session_state.logs[-20:]

# Display logs with proper styling
def display_logs():
    logs_html = "<div class='log-box'>"
    for log in reversed(st.session_state.logs):
        logs_html += f"<div class='log-entry'>{log}</div>"
    logs_html += "</div>"
    log_placeholder.markdown(logs_html, unsafe_allow_html=True)

# Display browser view
def display_browser_view(session_id=None, status="idle", live_view_url=None):
    if status == "idle":
        browser_html = """
        <div class='browser-view'>
            <h3>🌐 Browser Status: Idle</h3>
            <p style='color: #666;'>Click "Start Search" to begin browsing</p>
            <div style='margin-top: 2rem;'>
                <img src='https://via.placeholder.com/600x300/f0f2f6/1f77b4?text=Browser+Ready' style='max-width: 100%; border-radius: 5px;'/>
            </div>
        </div>
        """
    elif status == "active" and live_view_url:
        # Show live DCV view in iframe
        encoded_url = urllib.parse.quote(live_view_url, safe='')
        browser_html = f"""
        <div class='browser-view' style='padding: 0; min-height: 500px;'>
            <iframe 
                src='dcv_viewer.html?url={encoded_url}' 
                width='100%' 
                height='500px' 
                frameborder='0'
                style='border-radius: 10px;'
            ></iframe>
            <p style='margin-top: 0.5rem; color: #666; font-size: 0.9rem; text-align: center;'>
                🟢 Live Browser View - Session: {session_id}
            </p>
        </div>
        """
    elif status == "active":
        browser_html = f"""
        <div class='browser-view'>
            <h3>🟢 Browser Active</h3>
            <p style='color: #666;'>Session ID: <code>{session_id}</code></p>
            <div style='margin-top: 1rem; padding: 1rem; background: white; border-radius: 5px;'>
                <p><strong>Browser is navigating...</strong></p>
                <p style='color: #999; font-size: 0.9rem;'>Getting live view URL...</p>
                <div style='margin-top: 1rem;'>
                    <div style='background: linear-gradient(90deg, #1f77b4 0%, #1f77b4 50%, #e0e0e0 50%); height: 20px; border-radius: 10px; animation: loading 2s infinite;'></div>
                </div>
            </div>
        </div>
        """
    else:  # completed
        browser_html = f"""
        <div class='browser-view'>
            <h3>✅ Session Completed</h3>
            <p style='color: #666;'>Session ID: <code>{session_id}</code></p>
            <div style='margin-top: 1rem; padding: 1rem; background: #e8f5e9; border-radius: 5px;'>
                <p><strong>Recording uploaded to S3</strong></p>
                <p style='font-size: 0.9rem; margin-top: 0.5rem;'>
                    📹 Check bucket: <code>watch-watcher</code>
                </p>
            </div>
            <a href='https://us-east-1.console.aws.amazon.com/s3/buckets/watch-watcher' target='_blank' style='display: inline-block; margin-top: 1rem; padding: 0.5rem 1rem; background: #1f77b4; color: white; text-decoration: none; border-radius: 5px;'>
                View in S3 →
            </a>
        </div>
        """
    
    browser_placeholder.markdown(browser_html, unsafe_allow_html=True)

# Handle search
if search_button:
    if not watch_model:
        st.error("⚠️ Please enter a watch model")
    else:
        # Clear previous logs and state
        st.session_state.logs = []
        st.session_state.session_count += 1
        st.session_state.current_session_id = None
        
        add_log(f"Starting search for: {watch_model}")
        add_log(f"Website: {website}")
        display_logs()
        display_browser_view(status="idle")
        
        try:
            # Create agent
            add_log("Initializing AI agent...")
            display_logs()
            
            agent = create_watch_agent()
            
            add_log("Agent initialized successfully", "SUCCESS")
            display_logs()
            
            # Create prompt
            website_urls = {
                "eBay": "https://www.ebay.com",
                "Jomashop": "https://www.jomashop.com"
            }
            
            site_url = website_urls[website]
            
            add_log(f"Connecting to browser tool...")
            display_logs()
            
            # Get browser tool to fetch live view later
            browser_tool = CustomBrowserTool()
            
            prompt = f"""
Use the search_watch_on_website tool to search for "{watch_model}" on {site_url}.

Extract the first 3 results with prices and conditions.
"""
            
            add_log("Browser session starting...", "INFO")
            display_logs()
            display_browser_view(status="active", session_id="Starting...")
            
            # Stream the response in a thread to allow UI updates
            with st.spinner("🤖 Agent is working..."):
                # Start agent (this will create session)
                response = agent(prompt)
            
            # Try to extract session ID from console output or response
            response_text = str(response)
            session_id = None
            
            # Look for session ID in response
            if "Session ID:" in response_text:
                for line in response_text.split('\n'):
                    if "Session ID:" in line:
                        session_id = line.split("Session ID:")[-1].strip().split()[0]
                        break
            
            if session_id:
                st.session_state.current_session_id = session_id
                add_log(f"Session created: {session_id}", "SUCCESS")
                
                # Try to get live view URL
                add_log("Getting live view URL...", "INFO")
                display_logs()
                
                live_view_url = browser_tool.get_live_view_url(session_id)
                
                if live_view_url:
                    add_log("Live view URL obtained", "SUCCESS")
                    display_logs()
                    display_browser_view(status="active", session_id=session_id, live_view_url=live_view_url)
                    time.sleep(5)  # Give time to view browser
                else:
                    add_log("Could not get live view URL", "ERROR")
                    display_logs()
                    display_browser_view(status="active", session_id=session_id)
            
            add_log("Agent completed search", "SUCCESS")
            display_logs()
            
            # Show completed state
            if session_id:
                display_browser_view(status="completed", session_id=session_id)
            
            # Display results
            result_placeholder.success("✅ Search completed!")
            st.divider()
            st.subheader("🎯 Results")
            
            # Display response
            st.markdown(response_text)
            
            # Show session info with links
            if st.session_state.current_session_id:
                st.info(f"""
                📹 **Session Recording Available**
                
                Session ID: `{st.session_state.current_session_id}`
                
                Recording is being uploaded to S3. It will be available in 1-2 minutes.
                
                [View S3 Bucket →](https://us-east-1.console.aws.amazon.com/s3/buckets/watch-watcher)
                
                [View CloudWatch Logs →](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups)
                """)
            
        except Exception as e:
            add_log(f"Error: {str(e)}", "ERROR")
            display_logs()
            display_browser_view(status="idle")
            result_placeholder.error(f"❌ Error: {str(e)}")
else:
    # Show idle state
    display_browser_view(status="idle")

# Always display current logs
display_logs()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>Powered by AWS Bedrock AgentCore | Built with Strands & Streamlit</p>
</div>
""", unsafe_allow_html=True)