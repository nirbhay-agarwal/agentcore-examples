# custom_browser.py
import os
import boto3
from strands import tool
import json
from datetime import datetime
import time

class CustomBrowserTool:
    """Wrapper for your custom AgentCore Browser with full observability and browsing"""
    
    def __init__(self):
        self.client = boto3.client(
            'bedrock-agentcore',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # CloudWatch Logs client
        self.logs_client = boto3.client(
            'logs',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        full_arn = os.getenv('BROWSER_TOOL_ARN')
        self.browser_id = full_arn.split('/')[-1] if '/' in full_arn else full_arn
        
        self.log_group = f'/aws/vendedlogs/bedrock-agentcore/browser-custom/USAGE_LOGS/{self.browser_id}'
        self.log_stream = f'agent-spans-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
        
        self._setup_logging()
        
        print(f"🔧 Initialized browser tool with ID: {self.browser_id}")
        print(f"📊 Logging to: {self.log_group}")
        self.log_span("BROWSER_INIT", f"Initialized browser: {self.browser_id}")
    
    def _setup_logging(self):
        try:
            self.logs_client.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.log_stream
            )
            print(f"✅ Created log stream: {self.log_stream}")
        except:
            pass
    
    def log_span(self, span_name: str, message: str, metadata: dict = None):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'span_name': span_name,
            'browser_id': self.browser_id,
            'message': message,
        }
        
        if metadata:
            log_entry['metadata'] = metadata
        
        print(f"📊 SPAN [{span_name}]: {message}")
        
        try:
            self.logs_client.put_log_events(
                logGroupName=self.log_group,
                logStreamName=self.log_stream,
                logEvents=[{
                    'timestamp': int(datetime.now().timestamp() * 1000),
                    'message': json.dumps(log_entry)
                }]
            )
        except:
            pass
    
    def start_session(self, website_url: str, search_query: str):
        """Start a browser session"""
        try:
            self.log_span("SESSION_START_REQUEST", 
                         f"Requesting browser session for {website_url}",
                         {'website': website_url, 'query': search_query})
            
            response = self.client.start_browser_session(
                browserIdentifier=self.browser_id,
                name=f"watch-search-{os.urandom(4).hex()}",
                sessionTimeoutSeconds=3600,
                viewPort={
                    'height': 1080,
                    'width': 1920
                }
            )
            
            session_id = response.get('sessionId')
            
            self.log_span("SESSION_STARTED", 
                         f"Browser session created: {session_id}",
                         {'session_id': session_id})
            
            return response
            
        except Exception as e:
            self.log_span("SESSION_ERROR", f"Failed to start session: {str(e)}")
            raise
    
    def get_live_view_url(self, session_id: str):
        """Get presigned URL for DCV live view"""
        try:
            self.log_span("LIVE_VIEW_REQUEST", f"Getting live view URL for session {session_id}")
            
            response = self.client.get_browser_session(
                browserIdentifier=self.browser_id,
                sessionId=session_id
            )
            
            # Check multiple possible field names
            live_view_url = (response.get('liveViewUrl') or 
                            response.get('connectionUrl') or 
                            response.get('liveViewEndpoint') or
                            response.get('streamUrl'))
            
            if not live_view_url:
                # Print full response to see what's available
                print(f"Full response: {response}")
                self.log_span("LIVE_VIEW_URL_ERROR", f"No live view URL in response. Keys: {response.keys()}")
                return None
            
            self.log_span("LIVE_VIEW_URL_OBTAINED", f"Live view URL retrieved")
            return live_view_url
            
        except Exception as e:
            self.log_span("LIVE_VIEW_ERROR", f"Failed to get live view URL: {str(e)}")
            print(f"⚠️  Error details: {e}")
            return None
    
    
    
    def stop_session(self, session_id: str):
        """Stop browser session"""
        try:
            self.log_span("SESSION_STOP_REQUEST", 
                         f"Stopping browser session: {session_id}")
            
            response = self.client.stop_browser_session(
                browserIdentifier=self.browser_id,
                sessionId=session_id
            )
            
            self.log_span("SESSION_STOPPED", 
                         f"Browser session stopped. Recording will be uploaded to S3.")
            
            print(f"✅ Session stopped: {session_id}")
            print(f"📹 Recording will be uploaded to S3 shortly")
            
            return response
            
        except Exception as e:
            self.log_span("SESSION_STOP_ERROR", f"Failed to stop session: {str(e)}")
            raise


@tool
def search_watch_on_website(website_url: str, search_query: str) -> str:
    """
    Search for a watch on a website using your custom AgentCore browser.
    """
    
    browser_tool = CustomBrowserTool()
    session_id = None
    
    try:
        browser_tool.log_span("TOOL_INVOKED", f"search_watch_on_website called")
        
        # Start browser session
        session = browser_tool.start_session(website_url, search_query)
        session_id = session.get('sessionId')
        
        print(f"✅ Browser session started!")
        print(f"   Session ID: {session_id}")
        
        browser_tool.log_span("SESSION_ACTIVE", f"Session {session_id} is active for live viewing")
        
        # Keep session alive for viewing
        time.sleep(10)  # Give time to view in UI
        
        # Stop session
        browser_tool.stop_session(session_id)
        
        result = f"""
✅ Browser session created and ready!

Session ID: {session_id}
Website: {website_url}
Search Query: {search_query}

View the live session in AWS Console or in the Streamlit live view panel.
Session recording will be uploaded to S3.
"""
        return result
        
    except Exception as e:
        if session_id:
            try:
                browser_tool.stop_session(session_id)
            except:
                pass
        return f"❌ Error: {str(e)}"