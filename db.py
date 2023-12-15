import sqlite3

def update_one_rep_max():
    # New one-rep max values for specific exercises
    one_rep_max_values = {
        'pull up': 0,
        'row': 70
    }

    # Connect to the SQLite database
    conn = sqlite3.connect('exercise_database.db')
    cursor = conn.cursor()

    # Update one-rep max values
    for exercise, max_value in one_rep_max_values.items():
        cursor.execute('''
            UPDATE exercises
            SET one_rep_max = ?
            WHERE name = ?
        ''', (max_value, exercise))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("One-rep max values updated successfully.")

if __name__ == "__main__":
    update_one_rep_max()
