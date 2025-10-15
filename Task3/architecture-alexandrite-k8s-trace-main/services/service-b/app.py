from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__)

trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "service-b"}))
)
tracer_provider = trace.get_tracer_provider()
jaeger_exporter = OTLPSpanExporter(endpoint="http://simplest-collector:4318/v1/traces")

tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
FlaskInstrumentor().instrument_app(app)

@app.route("/")
def hello():
    with trace.get_tracer(__name__).start_as_current_span("process-request"):
        return "Hello from service B!\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
