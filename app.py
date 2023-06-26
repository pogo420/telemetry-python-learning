from random import randint
from flask import Flask
from opentelemetry import trace, metrics

# generating the tracer
tracer = trace.get_tracer("diceroller.tracer")

# generating the meters
meter = metrics.get_meter("diceroller.meter")

# creating counter
roll_counter = meter.create_counter("roll_counter", description="number of rolls")

# Application object
app = Flask(__name__)


def do_roll() -> int:
    with tracer.start_as_current_span("do_roll") as roll_span:
        res = randint(1,6)
        roll_span.set_attribute("roll.value", res)
        roll_counter.add(1, {"roll.value": res})
        return res


@app.route("/rolldice")
def roll_dice() -> str:
    return str(do_roll())

