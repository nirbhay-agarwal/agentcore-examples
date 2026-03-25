# SETUP.md

```markdown
# Complete Setup Guide
## AWS Bedrock AgentCore Examples - Mac OS

---

## Part 1: Install Required Software

### 1.1 Install Python
1. Go to **https://www.python.org/downloads**
2. Click **"Download Python 3.12"**
3. Open downloaded file and follow installer

Verify installation:
```bash
python3 --version
# Should show: Python 3.12.x
```

### 1.2 Install Git
```bash
xcode-select --install
```
Click **Install** when prompted.

### 1.3 Install an IDE
- **Cursor:** https://cursor.sh ← Recommended
- **VS Code:** https://code.visualstudio.com

---

## Part 2: AWS Setup

### 2.1 Create IAM Role for Browser Tool

The browser tool needs an IAM role to access AWS services.

1. Go to **AWS Console → IAM → Roles**
2. Click **"Create role"**
3. Search and attach these managed policies:
   - ✅ AmazonBedrockFullAccess
   - ✅ CloudWatchFullAccess
   - ✅ AWSXRayFullAccess
   - ✅ AmazonS3FullAccess
   - ✅ AWSXRayDaemonWriteAccess
   - ✅ BedrockAgentCoreFullAccess
4. Click **Next**
5. **Role name:** `agentcore-browser-role`
6. Click **Create role**
7. Click on the role you just created
8. Copy the **Role ARN** - looks like:
```
arn:aws:iam::YOUR_ACCOUNT:role/agentcore-browser-role
```

### 2.2 Create IAM User

1. Go to **AWS Console → IAM → Users**
2. Click **"Create user"**
3. **Username:** `agentcore-user`
4. Click **Next**
5. Select **"Attach policies directly"**
6. Search and attach these managed policies:
   - ✅ AmazonBedrockFullAccess
   - ✅ CloudWatchFullAccess
   - ✅ AWSXRayFullAccess
   - ✅ AmazonS3FullAccess
   - ✅ AWSXRayDaemonWriteAccess
   - ✅ BedrockAgentCoreFullAccess
7. Click **Next → Create user**


### 2.3 Create Access Keys

1. Click on your user
2. Click **"Security credentials"** tab
3. Scroll to **"Access keys"**
4. Click **"Create access key"**
5. Select **"Local code"**
6. Click **Next → Create access key"**
7. ⚠️ **Copy both keys NOW - you won't see them again!**
   - `Access key ID` → your `AWS_ACCESS_KEY_ID`
   - `Secret access key` → your `AWS_SECRET_ACCESS_KEY`
8. Click **Done**


### 2.4 Enable CloudWatch Transaction Search

1. Go to **AWS Console → CloudWatch → Settings**
2. Find **"Transaction Search"**
3. Click **Edit**
4. Enable **"Ingest spans as structured logs in OpenTelemetry format"**
5. Click **Save**

---

## Part 3: Get the Code

```bash
git clone https://github.com/nirbhay-agarwal/agentcore-examples.git
cd agentcore-examples
```

---

## Part 4: Python Environment

```bash
# Make sure you are in the root folder
cd agentcore-examples

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) in your terminal prompt ✅
```

---

Now follow the setup instructions inside each example folder.
```

---

# browser-agent/README.md

```markdown
# 🌐 AgentCore Browser Agent

An AI-powered browser agent that can browse any website with real-time live view,
full observability, and session recordings.

## Features

- 🤖 **AI Browser Agent** - Give it instructions in plain English
- 🖥️ **Live Browser View** - Watch the agent browse in real time via AWS DCV
- 📊 **Full Observability** - All traces visible in CloudWatch GenAI dashboard
- 📹 **Session Recordings** - Every session recorded and saved to S3
- ✏️ **Editable Instructions** - Generic agent that works for any website

## How it Works

```
User Instructions
      ↓
Strands Agent (Claude Sonnet)
      ↓
AgentCore Browser Tool ←→ Live View (AWS DCV) → Your Browser
      ↓
CloudWatch Traces + S3 Recordings
```

## Prerequisites

Complete [SETUP.md](../SETUP.md) first, then continue below.

---

## Step 1: Create Your Browser Tool

1. Go to **AWS Console → Bedrock AgentCore → Built-in Tools**
2. Click **"Browser Tools"** tab
3. Click **"Create browser tool"**
4. Fill in:
   - **Name:** `your-name-browser`
   - **Network:** Public
   - **Execution Role:** Select `agentcore-browser-role` (created in SETUP.md Part 2.1)
5. Enable **Recording:**
   - Toggle Recording **ON**
   - Select or create an **S3 bucket** for recordings
6. Enable **Logging:**
   - Toggle Logging **ON**
   - Log group will be auto-created:
     `/aws/vendedlogs/bedrock-agentcore/browser-custom/USAGE_LOGS/your-browser-id`
7. Enable **Tracing:**
   - Toggle Tracing **ON**
8. Click **Create**
9. Copy the **ARN:**
```
arn:aws:bedrock-agentcore:us-east-1:YOUR_ACCOUNT:browser-custom/your-browser-id
```

---

## Step 2: Create CloudWatch Log Group for Agent

This log group is for the **agent traces** (separate from browser tool logs).

1. Go to **AWS Console → CloudWatch → Log Groups**
2. Click **"Create log group"**
3. **Name:** `/agentcore/your-name-agent`
4. Click **Create**
5. Click on your log group → **"Create log stream"**
6. **Name:** `default`
7. Click **Create**

---

## Step 3: Install Dependencies

```bash
# Make sure you are in the browser-agent folder
cd agentcore-examples/browser-agent

# Make sure venv is activated (you should see (venv) in terminal)
source ../venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install browser automation
playwright install chromium
```

---

## Step 4: Download DCV SDK
*(Required for live browser view)*

```bash
# Make sure you are in the browser-agent folder
cd agentcore-examples/browser-agent

curl -O https://d1uj6qtbmh3dt5.cloudfront.net/webclientsdk/nice-dcv-web-client-sdk-1.9.100-952.zip
unzip nice-dcv-web-client-sdk-1.9.100-952.zip
mv nice-dcv-web-client-sdk dcv-sdk
rm nice-dcv-web-client-sdk-1.9.100-952.zip
```

Verify:
```bash
ls dcv-sdk/dcvjs-umd/
# Should show: dcv  dcv.js  EULA.txt ...
```

---

## Step 5: Configure .env

```bash
# Make sure you are in the browser-agent folder
cd agentcore-examples/browser-agent
```

Create a `.env` file inside the `browser-agent/` folder:

```bash
# AWS Credentials (from SETUP.md Part 2.4)
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
AWS_DEFAULT_REGION=us-east-1

# Your browser tool ARN (from Step 1 above)
BROWSER_TOOL_ARN=arn:aws:bedrock-agentcore:us-east-1:YOUR_ACCOUNT:browser-custom/your-browser-id

# Observability - use YOUR log group name (from Step 2 above)
OTEL_PYTHON_DISTRO=aws_distro
OTEL_PYTHON_CONFIGURATOR=aws_configurator
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_TRACES_EXPORTER=otlp
OTEL_PROPAGATORS=xray,tracecontext,baggage
OTEL_EXPORTER_OTLP_LOGS_HEADERS=x-aws-log-group=/agentcore/your-name-agent,x-aws-log-stream=default,x-aws-metric-namespace=bedrock-agentcore
OTEL_RESOURCE_ATTRIBUTES=service.name=your-name-agent
AGENT_OBSERVABILITY_ENABLED=true
```

⚠️ **Replace all `your-*` values with your actual values.**

Verify your `.env` is loading correctly:
```bash
# Make sure you are in the browser-agent folder
cd agentcore-examples/browser-agent

python -c "
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path('.') / '.env')
print('BROWSER_TOOL_ARN:', os.getenv('BROWSER_TOOL_ARN'))
print('AWS_REGION:', os.getenv('AWS_REGION'))
print('OTEL_RESOURCE_ATTRIBUTES:', os.getenv('OTEL_RESOURCE_ATTRIBUTES'))
"
# All values should be printed correctly
```

---

## Step 6: Run the App

You need **two Terminal windows** open at the same time.

**Terminal 1 - Web server for live browser view:**
```bash
cd agentcore-examples/browser-agent
python -m http.server 8080
```
Leave this running ✅

**Terminal 2 - Streamlit app:**
```bash
cd agentcore-examples/browser-agent
source ../venv/bin/activate
streamlit run streamlit_app.py
```

Open **http://localhost:8501** in your browser.

---

## Usage

1. Type your instructions in the text box
2. Click **🚀 Run Agent**
3. Watch the **live browser view** as the agent works
4. See results below when complete

### Example Instructions

**Search for watch prices:**
```
Go to https://www.ebay.com and search for "Rolex Submariner 126610LN".
Find the first 3 listings and tell me the prices and conditions.
```

**Research a product:**
```
Go to https://www.amazon.com and search for "Sony WH-1000XM5 headphones".
Find the current price, rating and top 3 customer reviews.
```

**Track stock availability:**
```
Go to https://www.bestbuy.com and search for "PlayStation 5".
Tell me if it is in stock and the current price.
```

---

## View Observability

After running the agent:

### Agent Traces
1. **AWS Console → CloudWatch → Log Groups**
2. Click `/agentcore/your-name-agent`
3. Click `default` stream

### GenAI Observability Dashboard
1. **AWS Console → CloudWatch → GenAI Observability**
2. Find `your-name-agent` service
3. View traces, token usage, latency

### Browser Tool Logs
1. **AWS Console → CloudWatch → Log Groups**
2. Find `/aws/vendedlogs/bedrock-agentcore/browser-custom/USAGE_LOGS/your-browser-id`

### Session Recordings
1. **AWS Console → S3 → your bucket**
2. Look for `browser-recordings/` folder

---

## Stop the App

**Terminal 2:** Press `Ctrl+C`

**Terminal 1:** Press `Ctrl+C`

**Deactivate virtual environment:**
```bash
deactivate
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `BROWSER_TOOL_ARN not found` | Check `.env` is inside `browser-agent/` folder |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Live view not showing | Make sure Terminal 1 is running `python -m http.server 8080` |
| AWS credentials error | Verify `.env` values using the verification command in Step 5 |
| Browser not loading | Run `playwright install chromium` |
| No traces in GenAI Observability | Check Transaction Search is enabled in CloudWatch Settings |
| Agent gets stuck | Press `Ctrl+C` and try again |
| `source: no such file or directory: venv/bin/activate` | Use `source ../venv/bin/activate` (note the `../`) |

---

## Architecture

```
┌─────────────────────────────────────────┐
│           Streamlit UI (Port 8501)       │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │ Instructions│  │  Live View       │  │
│  │   Text Box  │  │  (DCV iframe)    │  │
│  └─────────────┘  └──────────────────┘  │
│  ┌─────────────────────────────────────┐ │
│  │         Activity Logs               │ │
│  └─────────────────────────────────────┘ │
└──────────────────┬──────────────────────┘
                   │ subprocess
                   ↓
┌─────────────────────────────────────────┐
│     run_agent.py (with OTEL)            │
│                                         │
│  Strands Agent → AgentCore Browser      │
│                       ↓                 │
│              AWS DCV Live View          │
└──────┬──────────────────────────────────┘
       │
       ├──→ CloudWatch Agent Logs
       ├──→ CloudWatch Browser Tool Logs
       ├──→ CloudWatch GenAI Observability
       └──→ S3 Session Recordings
```

## Built With
- [AWS Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)
- [Strands Agents](https://strandsagents.com)
- [Streamlit](https://streamlit.io)
- [Amazon DCV](https://aws.amazon.com/hpc/dcv/)
- [OpenTelemetry](https://opentelemetry.io)
```