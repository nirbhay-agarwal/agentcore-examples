# agent.py
import os
from dotenv import load_dotenv
from strands import Agent

# Load your AWS credentials from .env file
load_dotenv()

# Create the agent (simple version for now)
def create_watch_agent():
    """
    Creates our watch tracking agent
    """
    # For now, we create a basic agent without tools
    # We'll add the browser tool in Step 3
    agent = Agent(
        model="anthropic.claude-3-5-sonnet-20241022-v2:0"  # Using Claude via Bedrock
    )
    
    return agent

# Function to search for watches
def track_watch(watch_model: str):
    """
    Track prices for a specific watch model
    
    Args:
        watch_model: The watch you want to search for (e.g., "Rolex Submariner")
    """
    print(f"\n🔍 Searching for: {watch_model}")
    print("⏳ This may take a moment...\n")
    
    # Create the agent
    agent = create_watch_agent()
    
    # Create a simple prompt with instructions
    prompt = f"""
You are a helpful watch price tracking assistant.

The user wants to know about: {watch_model}

Please provide helpful information about this watch model, including:
- What it typically costs
- Where it can be found
- Any important details about this model

Be friendly and clear in your response.
"""
    
    # Call the agent (using the () syntax like in the example)
    response = agent(prompt)
    
    return response

# Test function
if __name__ == "__main__":
    # Simple test
    print("✅ Agent file created successfully!")
    print("Testing basic functionality...\n")
    
    result = track_watch("Rolex Submariner")
    print("\n📊 Result:")
    print(result)