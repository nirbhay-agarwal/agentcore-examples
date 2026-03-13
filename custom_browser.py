# custom_browser.py
import os
import boto3
from strands import tool

class CustomBrowserTool:
    """Wrapper for your custom AgentCore Browser"""
    
    def __init__(self):
        self.client = boto3.client(
            'bedrock-agentcore',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        # Extract just the browser ID from the full ARN
        # ARN format: arn:aws:bedrock-agentcore:us-east-1:841021276485:browser-custom/watch_watcher-4Rt8tEdQ7a
        full_arn = os.getenv('BROWSER_TOOL_ARN')
        self.browser_id = full_arn.split('/')[-1] if '/' in full_arn else full_arn
        print(f"🔧 Initialized browser tool with ID: {self.browser_id}")
    
    def start_session(self):
        """Start a browser session"""
        try:
            response = self.client.start_browser_session(
                browserIdentifier=self.browser_id,
                name=f"watch-search-{os.urandom(4).hex()}",
                sessionTimeoutSeconds=3600,
                viewPort={
                    'height': 1080,
                    'width': 1920
                }
            )
            return response
        except Exception as e:
            print(f"❌ Error starting session: {e}")
            raise


@tool
def search_watch_on_website(website_url: str, search_query: str) -> str:
    """
    Search for a watch on a website using your custom AgentCore browser.
    
    Args:
        website_url: The website to search (e.g., "https://www.ebay.com")
        search_query: The watch model to search for
    
    Returns:
        str: Search results with prices and details
    """
    
    browser_tool = CustomBrowserTool()
    
    try:
        # Start browser session
        session = browser_tool.start_session()
        session_id = session.get('sessionId')
        
        print(f"✅ Browser session started!")
        print(f"   Session ID: {session_id}")
        
        result = f"""
✅ Successfully connected to your custom browser!

Browser ID: {browser_tool.browser_id}
Session ID: {session_id}

Searching {website_url} for: {search_query}

Session details: {session}

Now the browser session is active and ready. 
Next step: We need to send browsing commands to this session to navigate and extract data.
"""
        return result
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Full error: {error_msg}")
        return f"❌ Error connecting to custom browser: {error_msg}"