import os
import sqlite3
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "wpp-lab16-crud-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "records.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                course TEXT NOT NULL,
                grade TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


# READ: View all records + handle CREATE via POST
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        course = request.form.get("course", "").strip()
        grade = request.form.get("grade", "").strip().upper()

        if not student_name or not course or not grade:
            flash("Please fill in student name, course, and grade.", "error")
            return redirect(url_for("index"))

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        try:
            with get_db_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO students (student_name, course, grade, updated_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (student_name, course, grade, timestamp),
                )
                conn.commit()
            flash(f"Added record for {student_name}.", "success")
        except sqlite3.Error as exc:
            flash(f"Database error: {exc}", "error")

        return redirect(url_for("index"))

    with get_db_connection() as conn:
        records = conn.execute(
            "SELECT id, student_name, course, grade, updated_at FROM students ORDER BY id DESC"
        ).fetchall()

    return render_template("index.html", records=records)


# UPDATE: Display edit form & save changes
@app.route("/edit/<int:record_id>", methods=["GET", "POST"])
def edit_record(record_id):
    with get_db_connection() as conn:
        record = conn.execute(
            "SELECT id, student_name, course, grade, updated_at FROM students WHERE id = ?",
            (record_id,),
        ).fetchone()

        if not record:
            flash("Record not found.", "error")
            return redirect(url_for("index"))

        if request.method == "POST":
            student_name = request.form.get("student_name", "").strip()
            course = request.form.get("course", "").strip()
            grade = request.form.get("grade", "").strip().upper()

            if not student_name or not course or not grade:
                flash("All fields are required when updating a record.", "error")
                return render_template("edit.html", record=record)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            conn.execute(
                """
                UPDATE students
                SET student_name = ?, course = ?, grade = ?, updated_at = ?
                WHERE id = ?
                """,
                (student_name, course, grade, timestamp, record_id),
            )
            conn.commit()
            flash(f"Updated record for {student_name}.", "success")
            return redirect(url_for("index"))

    return render_template("edit.html", record=record)


# DELETE: Remove a record by ID
@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("DELETE FROM students WHERE id = ?", (record_id,))
            conn.commit()

        if cursor.rowcount > 0:
            flash("Record deleted successfully.", "success")
        else:
            flash("Record was already removed.", "error")
    except sqlite3.Error as exc:
        flash(f"Error deleting record: {exc}", "error")

    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)