import sqlite3
import datetime

START_DATE = datetime.date(2023, 11, 26)

def get_one_rep_max(exercise_name):
    conn = sqlite3.connect("exercise_database.db")
    cursor = conn.cursor()

    query = "SELECT one_rep_max FROM exercises WHERE name = ?"
    cursor.execute(query, (exercise_name,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        print(f"No one rep max found for {exercise_name}")
        return None
    
def calculate_weights(one_rep_max, percentages):
    return [round((one_rep_max * (p / 100)) / 2.5) * 2.5 for p in percentages]

def get_training_day(check_date):
    delta = check_date - START_DATE
    return delta.days % 16

def is_gym_day(check_date):
    training_day = get_training_day(check_date)
    return training_day in range(0, 4) or training_day in range(8, 12)

def next_gym_day():
    today = datetime.date.today()
    one_day = datetime.timedelta(days=1)
    next_day = today + one_day

    while not is_gym_day(next_day):
        next_day += one_day

    return next_day

def get_training_week(start_date):
    today = datetime.date.today()
    days_since_start = (today - start_date).days

    if days_since_start < 0:
        return None

    cycle_day = days_since_start % 32

    if (0 <= cycle_day <= 3):
        return 4
    elif (10 <= cycle_day <= 13):
        return 1
    elif (17 <= cycle_day <= 20):
        return 2
    elif (26 <= cycle_day <= 29):
        return 3
    else:
        return None
    
def is_new_cycle(start_date):
    today = datetime.date.today()
    days_since_start = (today - start_date).days

    if days_since_start < 0:
        return None

    cycle_day = days_since_start % 16

    return 0 <= cycle_day <= 3

def increment_exercise_count(exercise_name):
    conn = sqlite3.connect("exercise_database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM exercises WHERE name = ?", (exercise_name,))
    result = cursor.fetchone()
    if result:
        exercise_id = result[0]

        cursor.execute("""
            INSERT INTO exercise_counts (exercise_id, count)
            VALUES (?, 1)
            ON CONFLICT(exercise_id) DO UPDATE SET count = count + 1
            """, (exercise_id,))
        conn.commit()
    else:
        print("Exercise not found")

    conn.close()

def fetch_exercise_count(exercise_name):
    conn = sqlite3.connect("exercise_database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM exercises WHERE name = ?", (exercise_name,))
    result = cursor.fetchone()

    if result:
        exercise_id = result[0]

        cursor.execute("SELECT count FROM exercise_counts WHERE exercise_id = ?", (exercise_id,))
        count_result = cursor.fetchone()

        conn.close()

        return count_result[0] if count_result else 0
    else:
        print("Exercise not found")
        conn.close()
        return 0

def clear_exercise_count(exercise_name):
    conn = sqlite3.connect("exercise_database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM exercises WHERE name = ?", (exercise_name,))
    result = cursor.fetchone()

    if result:
        exercise_id = result[0]

        cursor.execute("""
            INSERT INTO exercise_counts (exercise_id, count)
            VALUES (?, 0)
            ON CONFLICT(exercise_id) DO UPDATE SET count = 0
            """, (exercise_id,))
        conn.commit()
    else:
        print("Exercise not found")

    conn.close()

def add_weight(exercise_name):
    count = fetch_exercise_count(exercise_name)

    if exercise_name == 'face pull':
        return count >= 8

    return count >= 4

def add_to_bar(weight, exercise_name):
        conn = sqlite3.connect("exercise_database.db")
        cursor = conn.cursor()

        cursor.execute("""
                UPDATE exercises 
                SET one_rep_max = one_rep_max + ? 
                WHERE exercise_type = ?
                """, weight, exercise_name)
        
        conn.commit()
        conn.close()

def progressive_overload():
    if is_new_cycle(START_DATE):
        conn = sqlite3.connect("exercise_database.db")
        cursor = conn.cursor()

        query = "SELECT name FROM exercises"
        cursor.execute(query)

        exercises = []

        for row in cursor.fetchall():
            exercises.append(row[0])

        conn.close()
      
        for exercise in exercises:
            if add_weight(exercise) == True:
                add_to_bar(5, exercise)

def display_training_schedule(training_day):
    current_week = get_training_week(START_DATE)
    if current_week is None:
        return "<p>Training schedule has not started yet.</p>"

    html_output = f"<p>Current Training Week: {current_week}</p>"

    exercises_schedule = {
        0: [
            "overhead press",
            "chest press",
            "pull up",
            "face pull",
            "tricep extension",
            "bicep curl",
        ],
        1: [
            "deadlift",
            "hack squat",
            "ab crunch",
            "standing calf raise"
        ],
        2: [
            "bench press",
            "shoulder press",
            "row",
            "face pull",
            "tricep pushdown",
            "hammer curl",
        ],
        3: [
            "squat",
            "rdl",
            "hanging leg raise",
            "seated calf raise"
        ],
    }

    exercises_for_today = exercises_schedule.get(training_day)
    if not exercises_for_today:
        return "<p>No exercises scheduled for today.</p>"
    weeks = [
        ([3, 3, 3], [5, 5, 5], [65, 75, 85]),  # Week 1: 3 sets of 5 reps
        ([3, 3, 3], [3, 3, 3], [70, 80, 90]),  # Week 2: 3 sets of 3 reps
        ([1, 1, 1], [5, 3, 1], [75, 85, 95]),  # Week 3: 5/3/1 reps
        ([3, 3, 3], [5, 5, 5], [40, 50, 60]),  # Week 4: Deload
    ]

    html_output += "<ul>"

    for idx, exercise in enumerate(exercises_for_today):
        if idx == 0:
            # First exercise uses the 5/3/1 formula
            one_rep_max = get_one_rep_max(exercise)
            if one_rep_max is not None:
                html_output += f"<li>{exercise.title()}:</li>"
                sets, reps, percentages = weeks[current_week - 1]
                weights = calculate_weights(one_rep_max, percentages)
                for set_num, weight in enumerate(weights):
                    html_output += f"<li>Set {set_num + 1}: {reps[set_num]} reps at {weight} kg</li>"
        elif idx == 1:
            # Second exercise is 5 sets of 10 reps at 50% 1RM
            one_rep_max = get_one_rep_max(exercise)
            if one_rep_max is not None:
                weight = round((one_rep_max * 0.50) / 2.5) * 2.5
                html_output += (
                    f"<li>{exercise.title()}: 5 sets of 10 reps at {weight} kg</li>"
                )

        else:
            # Remaining exercises with their own weight variables
            one_rep_max = get_one_rep_max(exercise)
            if one_rep_max is not None:
                weight = round((one_rep_max * 0.50) / 2.5) * 2.5
                if exercise in ("pull up", "ab crunch", "row"):
                    html_output += f"<li>{exercise.title()}: 5 sets of 10 reps at {weight} kg</li>"
                else:
                    html_output += f"<li>{exercise.title()}: 3 sets of 10 reps at {weight} kg</li>"

                html_output += f"<button id='btn_{exercise}' onclick='incrementCounter(\"{exercise}\")'>Hit Target for {exercise.title()}</button>"
            else:
                html_output += (
                    f"<li>Skipping {exercise} as weight data is not available.</li>"
                )

    html_output += "</ul>"
    return html_output

        

def main():
    print('placeholder')


if __name__ == "__main__":
    main()