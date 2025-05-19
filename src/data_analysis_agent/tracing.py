from helper import get_phoenix_endpoint
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor

PROJECT_NAME = "Data Analysis Agent"

# Set up OpenTelemetry tracing
tracer_provider = register(
    project_name=PROJECT_NAME,
    endpoint=get_phoenix_endpoint())

OpenAIInstrumentor().instrument(tracer_provider = tracer_provider)
tracer = tracer_provider.get_tracer(__name__)