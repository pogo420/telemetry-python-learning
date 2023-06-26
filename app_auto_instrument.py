from random import randint
from flask import Flask

app = Flask(__name__)


def do_roll() -> int:
    return randint(1,6)


@app.route("/rolldice")
def roll_dice() -> str:
    return str(do_roll())

