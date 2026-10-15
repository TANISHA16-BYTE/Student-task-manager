
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = "tasks.db"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_db():
    connection = get_db()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0
        )
    """)
    connection.commit()
    connection.close()


@app.route("/")
def home():
    current_filter = request.args.get("filter", "all")

    connection = get_db()

    total = connection.execute(
        "SELECT COUNT(*) FROM tasks"
    ).fetchone()[0]

    completed = connection.execute(
        "SELECT COUNT(*) FROM tasks WHERE completed = 1"
    ).fetchone()[0]

    pending = total - completed

    if current_filter == "pending":
        tasks = connection.execute(
            "SELECT * FROM tasks WHERE completed = 0 ORDER BY id DESC"
        ).fetchall()
    elif current_filter == "completed":
        tasks = connection.execute(
            "SELECT * FROM tasks WHERE completed = 1 ORDER BY id DESC"
        ).fetchall()
    else:
        current_filter = "all"
        tasks = connection.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()

    connection.close()

    return render_template(
        "index.html",
        tasks=tasks,
        total=total,
        pending=pending,
        completed=completed,
        current_filter=current_filter
    )


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()

    if title:
        connection = get_db()
        connection.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (title,)
        )
        connection.commit()
        connection.close()

    return redirect(url_for("home"))


@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    connection = get_db()

    connection.execute(
        """UPDATE tasks
           SET completed = CASE
               WHEN completed = 0 THEN 1
               ELSE 0
           END
           WHERE id = ?""",
        (task_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("home"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    connection = get_db()

    connection.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("home"))


if __name__ == "__main__":
    initialize_db()
    app.run(debug=True)
