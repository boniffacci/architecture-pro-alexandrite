from flask import Flask
import requests
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

app = Flask(__name__)

# Настройка OpenTelemetry
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "service-a"}))
)
tracer_provider = trace.get_tracer_provider()
jaeger_exporter = OTLPSpanExporter(endpoint="http://simplest-collector:4318/v1/traces")

tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route("/")
def call_service_b():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("call-service-b"):
        r = requests.get("http://service-b:8080/")
        return f"Response from B: {r.text}\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
