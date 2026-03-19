# test_observability.py
import streamlit as st
import subprocess
import os
import sys
import time
import boto3
from dotenv import load_dotenv

load_dotenv()

st.title("🔍 Observability Test")

otel_path = "/Users/agarnirb/Developer/watch_watcher/venv/bin/opentelemetry-instrument"
python_path = "/Users/agarnirb/Developer/watch_watcher/venv/bin/python3"

env = os.environ.copy()

# AWS credentials
env['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
env['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
env['AWS_REGION'] = os.getenv('AWS_REGION', 'us-east-1')
env['AWS_DEFAULT_REGION'] = os.getenv('AWS_REGION', 'us-east-1')

# OTEL vars - keep it simple, same as terminal
env['OTEL_PYTHON_DISTRO'] = 'aws_distro'
env['OTEL_PYTHON_CONFIGURATOR'] = 'aws_configurator'
env['OTEL_EXPORTER_OTLP_PROTOCOL'] = 'http/protobuf'
env['OTEL_TRACES_EXPORTER'] = 'otlp'
env['OTEL_PROPAGATORS'] = 'xray,tracecontext,baggage'  # Add X-Ray propagator
env['OTEL_EXPORTER_OTLP_LOGS_HEADERS'] = 'x-aws-log-group=/agentcore/watch-tracker,x-aws-log-stream=default,x-aws-metric-namespace=bedrock-agentcore'
env['OTEL_RESOURCE_ATTRIBUTES'] = 'service.name=watch-tracker-agent'
env['AGENT_OBSERVABILITY_ENABLED'] = 'true'

# Remove these - let AWS distro handle it
# env['OTEL_EXPORTER_OTLP_TRACES_ENDPOINT'] = ...
# env['OTEL_PROPAGATORS'] = ...

if st.button("Test Agent"):
    
    st.write("**Env vars being passed:**")
    otel_vars = {k: v for k, v in env.items() if 'OTEL' in k or 'AGENT_OBS' in k}
    for k, v in otel_vars.items():
        st.code(f"{k}={v}")
    
    test_session_id = "test-session-001"  # Fixed so we can track it
    st.write(f"**Session ID:** `{test_session_id}`")

    
    with st.spinner("Running agent..."):
        result = subprocess.run(
            [otel_path, python_path, '-c', f'''
from strands import Agent
from opentelemetry import baggage, context

session_id = "{test_session_id}"
print(f"Using session ID: {{session_id}}", flush=True)

ctx = baggage.set_baggage("session.id", session_id)
token = context.attach(ctx)

agent = Agent(
    model="global.anthropic.claude-sonnet-4-6",
    trace_attributes={{
        "session.id": session_id,
        "tags": ["browser", "watch-tracker"]
    }}
)

response = agent("Say hello in one word")
print(f"Response: {{response}}", flush=True)

context.detach(token)
'''],
            capture_output=True,
            text=True,
            env=env
        )
    
    st.write("**Output:**", result.stdout)
    st.write("**Stderr:**", result.stderr[-500:] if result.stderr else "None")
    st.write("**Return code:**", result.returncode)