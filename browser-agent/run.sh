#!/bin/bash

# Export all OTEL env vars
export OTEL_PYTHON_DISTRO=aws_distro
export OTEL_PYTHON_CONFIGURATOR=aws_configurator
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_TRACES_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_LOGS_HEADERS="x-aws-log-group=/agentcore/watch-tracker,x-aws-log-stream=watch-tracker-agent,x-aws-metric-namespace=bedrock-agentcore"
export OTEL_RESOURCE_ATTRIBUTES="service.name=watch-tracker-agent"
export AGENT_OBSERVABILITY_ENABLED=true

# Export AWS vars
export AWS_ACCESS_KEY_ID=$(grep AWS_ACCESS_KEY_ID .env | cut -d '=' -f2)
export AWS_SECRET_ACCESS_KEY=$(grep AWS_SECRET_ACCESS_KEY .env | cut -d '=' -f2)
export AWS_REGION=$(grep AWS_REGION .env | cut -d '=' -f2)
export BROWSER_TOOL_ARN=$(grep BROWSER_TOOL_ARN .env | cut -d '=' -f2)

# Run with instrumentation
opentelemetry-instrument streamlit run streamlit_app.py