import sqlite3
import datetime
from flask import Flask, render_template, request, jsonify

from helpers import *

START_DATE = datetime.date(2023, 11, 26)


app = Flask(__name__)


@app.route("/")
def index():
    progressive_overload()
    today = datetime.date.today()
    current_week = get_training_week(START_DATE) 

    if is_gym_day(today):
        schedule = display_training_schedule(
            get_training_day(today)
        )
        message = "Today is a gym day!"
    else:
        next_day = next_gym_day()
        message = f"Rest day. Next gym day is on {next_day.strftime('%A, %B %d, %Y')}."
        schedule = None

    return render_template("index.html", message=message, schedule=schedule)

@app.route("/increment_counter", methods=["POST"])
def increment_counter():
    data = request.json
    exercise_name = data.get("exercise")

    increment_exercise_count(exercise_name)

    return jsonify({"message": "Counter incremented for " + exercise_name})

if __name__ == "__main__":
    app.run(debug=True)