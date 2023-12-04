from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)

# Configuration
DATABASE = 'students.db'

# Connect to the database
def get_db():
    # Check if a database connection exists in the global context, if not, create a new connection
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Close the database connection at the end of the request
@app.teardown_appcontext
def close_connection(exception):
    # Close the database connection if it exists at the end of the request
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize the database
def init_db():
    # Create the students table in the database if it does not already exist
    with app.app_context():
        db = get_db()
        with db:
            db.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, id_number TEXT, gender TEXT, courses TEXT)")

# Route for displaying the form
@app.route('/')
def index():
    # Retrieve the list of students from the database and render the index.html template with the student data
    students = get_students()
    return render_template('index.html', students=students)

# Route for handling form submission
@app.route('/submit', methods=['POST'])
def submit():
    # Extract form data and insert it into the students table in the database
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    id_number = request.form['id_number']
    gender = request.form['gender']
    courses = ', '.join(request.form.getlist('courses'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO students (first_name, last_name, id_number, gender, courses) VALUES (?, ?, ?, ?, ?)",
                   (first_name, last_name, id_number, gender, courses))
    db.commit()
    return redirect(url_for('index'))

# Route for deleting a student
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    # Delete a student from the database based on the provided student ID
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (id,))
    db.commit()
    return redirect(url_for('index'))

def get_students():
    # Retrieve the list of students from the database
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    return students

if __name__ == '__main__':
    # Initialize the database and start the Flask application in debug mode
    init_db()
    app.run(debug=True)
