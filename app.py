from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


# -----------------------------
# Database Connection Function
# -----------------------------
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row   # Access columns by name
    return conn


# -----------------------------
# Initialize Database
# -----------------------------
def init_db():
    conn = get_db_connection()
    conn.execute("DROP TABLE IF EXISTS notes")   # Force reset
    conn.execute("""
        CREATE TABLE notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT (datetime('now','localtime'))
        )
    """)
    conn.commit()
    conn.close()


# -----------------------------
# Routes
# -----------------------------

# Home Page
@app.route("/")
def home():
    return render_template("home.html")


# Add Note
@app.route("/add", methods=["GET", "POST"])
def add_note():
    if request.method == "POST":
        content = request.form["note"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO notes (content) VALUES (?)",
            (content,)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("view_notes"))

    return render_template("add_note.html")


# View Notes
@app.route("/notes")
def view_notes():
    conn = get_db_connection()
    notes = conn.execute(
        "SELECT * FROM notes ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    return render_template("notes.html", notes=notes)


# Delete Note
@app.route("/delete/<int:id>")
def delete_note(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM notes WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("view_notes"))


# Edit Note
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_note(id):
    conn = get_db_connection()
    note = conn.execute(
        "SELECT * FROM notes WHERE id = ?",
        (id,)
    ).fetchone()

    if request.method == "POST":
        updated_content = request.form["note"]

        conn.execute(
            "UPDATE notes SET content = ? WHERE id = ?",
            (updated_content, id)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("view_notes"))

    conn.close()
    return render_template("edit_note.html", note=note)


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)