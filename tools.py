# tools.py
from strands_tools.browser import AgentCoreBrowser
import os

# Initialize the AgentCore Browser tool
def get_browser_tool():
    """Initialize and return the browser tool"""
    browser_instance = AgentCoreBrowser(region=os.getenv('AWS_REGION', 'us-east-1'))
    return browser_instance.browser