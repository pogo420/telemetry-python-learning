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
        resource=Resource.create({SERVICE_NAME: "dice_roller"})
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
tracer = trace.get_tracer("diceroller.tracer")

# generating the meters
meter = metrics.get_meter("diceroller.meter")

# creating counter
roll_counter = meter.create_counter("roll_counter", description="number of rolls")

# Application object
app = Flask(__name__)


def do_roll() -> int:
    with tracer.start_as_current_span("do_compute") as compute_span:
        response = get("http://localhost:8080/doCompute")
        compute_span.set_attribute("compute.duration", response.text)

    with tracer.start_as_current_span("do_sleep") as sleep_span:
        dur = randint(1,10)/1000
        sleep(dur)
        compute_span.set_attribute("sleep.duration", dur)

    with tracer.start_as_current_span("do_roll") as roll_span:
        res = randint(1, 6)
        roll_span.set_attribute("roll.value", res)
        roll_counter.add(1, {"roll.value": res})
        return res


@app.route("/rolldice")
def roll_dice() -> str:
    return str(do_roll())

