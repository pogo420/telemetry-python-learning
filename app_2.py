from random import randint
from flask import Flask
from time import sleep

from requests import get

from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Boiler plate code for enabling jaeger, below
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "dummy_compute"})
    )
)
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)
# Boiler plate code for enabling jaeger, above

# generating the tracer
tracer = trace.get_tracer("dummy_compute.tracer")


# Application object
app = Flask(__name__)


def dummy() -> float:
    with tracer.start_as_current_span("dummy") as roll_span:
        random_compute = randint(1, 10)/1000
        sleep(random_compute)
        roll_span.set_attribute("computeTime.value", random_compute)
        return random_compute


@app.route("/doCompute")
def do_compute() -> str:
    return str(dummy())
