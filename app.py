import datetime
from flask import Flask, render_template, request, jsonify

from helpers import *

START_DATE = datetime.date(2023, 11, 26)


app = Flask(__name__)


@app.route("/")
def index():
    progressive_overload()
    today = datetime.date.today()

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

@app.route('/update_count', methods=['POST'])
def update_count():
    data = request.json
    exercise_name = data['exercise_name']
    action = data['action']

    increment = 0
    if action == "Hit":
        increment = 1
    elif action == "Smash":
        increment = 4 if exercise_name != 'face pull' else 8

    if increment > 0:
        increment_exercise_count(exercise_name, increment)

    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)