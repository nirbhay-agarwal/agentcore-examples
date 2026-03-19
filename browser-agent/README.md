# 🌐 AgentCore Browser Agent

An AI-powered browser agent that can browse any website with real-time live view,
full observability, and session recordings.

---

## Features

- 🤖 **AI Browser Agent** - Give it instructions in plain English
- 🖥️ **Live Browser View** - Watch the agent browse in real time via AWS DCV
- 📊 **Full Observability** - All traces visible in CloudWatch GenAI dashboard
- 📹 **Session Recordings** - Every session recorded and saved to S3
- ✏️ **Editable Instructions** - Generic agent that works for any website

---

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

---

## Prerequisites

Complete [SETUP.md](../SETUP.md) first, then continue here.

---

## Step 1: Create Your Browser Tool

1. Go to **AWS Console → Bedrock AgentCore → Built-in Tools**
2. Click the **"Browser Tools"** tab
3. Click **"Create browser tool"**
4. Fill in:
   - **Name:** `your-name-browser`
   - **Network:** Public
   - **Recording:** Enable ✅
   - **S3 Bucket:** Create new or use existing
5. Click **Create**
6. Copy the **ARN:**

```
arn:aws:bedrock-agentcore:us-east-1:YOUR_ACCOUNT:browser-custom/your-browser-id
```

---

## Step 2: Create CloudWatch Log Group

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
cd browser-agent

pip install -r requirements.txt

playwright install chromium
```

---

## Step 4: Download DCV SDK

> Required for live browser view

```bash
cd browser-agent

curl -O https://d1uj6qtbmh3dt5.cloudfront.net/webclientsdk/nice-dcv-web-client-sdk-1.9.100-952.zip
unzip nice-dcv-web-client-sdk-1.9.100-952.zip
mv nice-dcv-web-client-sdk dcv-sdk
rm nice-dcv-web-client-sdk-1.9.100-952.zip
```

**Verify:**

```bash
ls dcv-sdk/dcvjs-umd/
# Should show: dcv  dcv.js  EULA.txt ...
```

---

## Step 5: Configure .env

Create a `.env` file inside the `browser-agent/` folder:

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
AWS_DEFAULT_REGION=us-east-1

# Your browser tool ARN (from Step 1)
BROWSER_TOOL_ARN=arn:aws:bedrock-agentcore:us-east-1:YOUR_ACCOUNT:browser-custom/your-browser-id

# Observability (use your log group name from Step 2)
OTEL_PYTHON_DISTRO=aws_distro
OTEL_PYTHON_CONFIGURATOR=aws_configurator
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_TRACES_EXPORTER=otlp
OTEL_PROPAGATORS=xray,tracecontext,baggage
OTEL_EXPORTER_OTLP_LOGS_HEADERS=x-aws-log-group=/agentcore/your-name-agent,x-aws-log-stream=default,x-aws-metric-namespace=bedrock-agentcore
OTEL_RESOURCE_ATTRIBUTES=service.name=your-name-agent
AGENT_OBSERVABILITY_ENABLED=true
```

> ⚠️ Replace all `your-*` values with your actual values.

---

## Step 6: Run the App

You need **two Terminal windows open at the same time.**

**Terminal 1 — Web server:**

```bash
cd browser-agent
python -m http.server 8080
```

**Terminal 2 — Streamlit app:**

```bash
cd browser-agent
source ../venv/bin/activate
streamlit run streamlit_app.py
```

Open http://localhost:8501 in your browser.

---

## Usage

1. Type your instructions in the text box
2. Click **🚀 Run Agent**
3. Watch the live browser view as the agent works
4. See results below when complete

---

## Example Instructions

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

**Track product availability:**
```
Go to https://www.bestbuy.com and search for "PlayStation 5".
Tell me if it is in stock and the current price.
```

---

## View Observability

After running the agent:

### CloudWatch Logs
1. **AWS Console → CloudWatch → Log Groups**
2. Click `/agentcore/your-name-agent`
3. Click the `default` stream

### GenAI Observability Dashboard
1. **AWS Console → CloudWatch → GenAI Observability**
2. Find your `your-name-agent` service
3. View traces, token usage, and latency

### Session Recordings
1. **AWS Console → S3 → your bucket**
2. Look for the `browser-recordings/` folder

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Live view not showing | Make sure Terminal 1 is running `python -m http.server 8080` |
| AWS credentials error | Check your `.env` file has correct keys |
| Browser not loading | Run `playwright install chromium` |
| No traces in GenAI Observability | Check Transaction Search is enabled in CloudWatch Settings |
| 403 error in logs | Check IAM permissions in `SETUP.md` |
| Agent gets stuck | Press `Ctrl+C` and try again — sessions auto-terminate |

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
       ├──→ CloudWatch Logs
       ├──→ CloudWatch GenAI Observability
       ├──→ S3 Session Recordings
       └──→ Streamlit UI (results)
```

---

## Built With

- [AWS Bedrock AgentCore](https://aws.amazon.com/bedrock/)
- [Strands Agents](https://strandsagents.com)
- [Streamlit](https://streamlit.io)
- [Amazon DCV](https://aws.amazon.com/dcv/)
- [OpenTelemetry](https://opentelemetry.io)