Browser agent setup instructions

AgentCore Browser Agent - Mac OS


Part 1: Install Required Software

1.1 Install VS Code or Cursor

* Cursor: https://cursor.sh
* VS Code: https://code.visualstudio.com

1.2 Install Python

1. Go to https://www.python.org/downloads
2. Click "Download Python 3.12"
3. Open downloaded file and follow installer
4. ✅ Verify: Open Terminal and run:


python3 --version
# Should show: Python 3.12.x

1.3 Install Git


xcode-select --install


Part 2: AWS Setup

1. Part 2.1: Create IAM User with Required Permissions


Step 1: Go to IAM Console

1. Go to AWS Console → IAM
2. Click "Users" in left menu
3. Click "Create user"


Step 2: Create User

1. Username: agentcore-browser-user (or your name)
2. Click Next
3. Select "Attach policies directly"
4. Search and attach these managed policies:
    1. ✅ AmazonBedrockFullAccess
    2. ✅ CloudWatchFullAccess
    3. ✅ AWSXRayFullAccess
    4. AmazonS3FullAccess
    5. AWSXRayDaemonWriteAccess
    6. BedrockAgentCoreFullAccess
5. Click Next → Create user


Part 3: Get the Code

Run each command one by one in terminal

Open Terminal:


# Clone the repo
git clone https://github.com/nirbhay-agarwal/watch-watcher.git
cd watch-watcher


Part 4: Set Up Python Environment



# Create virtual environment
python3 -m venv venv
# Activate it
source venv/bin/activate
# You should see (venv) in terminal ✅

# Install all dependencies
pip install -r requirements.txt
# Install browser automation
playwright install chromium


Part 5: Download DCV SDK

(Required for live browser view)



curl -O https://d1uj6qtbmh3dt5.cloudfront.net/webclientsdk/nice-dcv-web-client-sdk-1.9.100-952.zipunzip nice-dcv-web-client-sdk-1.9.100-952.zipmv nice-dcv-web-client-sdk dcv-sdkrm nice-dcv-web-client-sdk-1.9.100-952.zip

Verify:



ls dcv-sdk/dcvjs-umd/# Should show: dcv  dcv.js  EULA.txt ...


Part 6: Configure Your Settings

Open the project in your IDE and create a .env file:


# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
AWS_DEFAULT_REGION=us-east-1
# Your custom browser tool ARN (from Part 2.2)
BROWSER_TOOL_ARN=arn:aws:bedrock-agentcore:us-east-1:
YOUR_ACCOUNT:browser-custom/your-browser-id
# Observability - use YOUR log group name (from Part 2.3)
OTEL_PYTHON_DISTRO=aws_distro
OTEL_PYTHON_CONFIGURATOR=aws_configurator
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_TRACES_EXPORTER=otlp
OTEL_PROPAGATORS=xray,tracecontext,baggage
OTEL_EXPORTER_OTLP_LOGS_HEADERS=x-aws-log-group=/agentcore/your-name-agent,x-aws-log-stream=default,x-aws-metric-namespace=bedrock-agentcore
OTEL_RESOURCE_ATTRIBUTES=service.name=your-name-agent
AGENT_OBSERVABILITY_ENABLED=true

⚠️ Replace these with your actual values:

* your_access_key_here → your AWS key
* your_secret_key_here → your AWS secret
* BROWSER_TOOL_ARN → your browser ARN from Part 2.2
* /agentcore/your-name-agent → your log group from Part 2.3
* your-name-agent → same name as your log group


Part 7: Run the App

You need two Terminal windows open at the same time.

Terminal 1 - Web server for live browser view:


cd watch-watcherpython -m http.server 8080

Leave this running ✅

Terminal 2 - Streamlit app:


cd watch-watchersource venv/bin/activatestreamlit run streamlit_app.py


Part 8: Use the App

1. Open browser → http://localhost:8501
2. Write your instructions in the text box
3. Click 🚀 Run Agent
4. Watch the live browser view in real time!
5. See results below when done

Example instructions:

Go to https://www.ebay.com and search for 
"Rolex Submariner 126610LN". 
Find the first 3 listings and tell me 
the prices and conditions.


Part 9: View Observability

After running the agent:

1. CloudWatch Logs:

    * AWS Console → CloudWatch → Log Groups
    * Click /agentcore/your-name-agent
    * Click default stream

1. GenAI Observability Dashboard:

    * AWS Console → CloudWatch → GenAI Observability
    * Find your-name-agent service
    * View traces, token usage, latency

1. Browser Session Recordings:

    * AWS Console → S3 → your-bucket
    * Look for browser-recordings/ folder


Troubleshooting



PROBLEM	SOLUTION
python3: command not found	Reinstall Python, check "Add to PATH"
(venv) not showing	Run source venv/bin/activate again
Live view not showing	Make sure Terminal 1 is running
AWS credentials error	Check .env file values
Browser not loading	Run playwright install chromium
No traces in GenAI Observability	Check Transaction Search is enabled (Part 2.4)
403 error in logs	Check IAM permissions (Part 2.5)
App won't open	Make sure both terminals are running


Need Help?

Contact Nirbhay Agarwal on Slack 🙂

You're all set! 🚀
