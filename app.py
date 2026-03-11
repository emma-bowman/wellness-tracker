from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))
app.permanent_session_lifetime = timedelta(days=365)


def get_db():
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            pin TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            grateful_1 TEXT NOT NULL,
            grateful_2 TEXT NOT NULL,
            grateful_3 TEXT NOT NULL,
            prayer_1 TEXT NOT NULL,
            prayer_2 TEXT NOT NULL,
            prayer_3 TEXT NOT NULL,
            score INTEGER NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

init_db()


def entry_exists_today():
    today = datetime.now().strftime("%d %b %Y")
    user_id = int(session.get("user_id"))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM entries WHERE date = %s AND user_id = %s", (today, user_id))
    entry = cursor.fetchone()
    cursor.close()
    conn.close()
    if entry is None:
        return False, None
    return True, entry[1]


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if "user_id" not in session:
                return redirect(url_for("login"))
            int(session.get("user_id"))
        except (ValueError, TypeError):
            session.clear()
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        pin = request.form.get("pin", "").strip()
        action = request.form.get("action")

        if action == "register":
            if len(pin) != 4 or not pin.isdigit():
                error = "PIN must be exactly 4 digits."
            else:
                conn = get_db()
                cursor = conn.cursor()
                try:
                    hashed_pin = generate_password_hash(pin)
                    cursor.execute(
                        "INSERT INTO users (username, pin) VALUES (%s, %s) RETURNING id",
                        (username, hashed_pin)
                    )
                    user_id = cursor.fetchone()[0]
                    conn.commit()
                    session.permanent = True
                    session["user_id"] = user_id
                    session["username"] = username
                    return redirect(url_for("index"))
                except psycopg2.errors.UniqueViolation:
                    conn.rollback()
                    error = "That username is already taken."
                finally:
                    cursor.close()
                    conn.close()

        elif action == "login":
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, pin FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            if user and check_password_hash(user[1], pin):
                session.permanent = True
                session["user_id"] = user[0]
                session["username"] = username
                return redirect(url_for("index"))
            else:
                error = "Invalid username or PIN."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    user_id = int(session.get("user_id"))
    username = session.get("username")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entries WHERE user_id = %s ORDER BY id DESC", (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    entries = []
    for row in rows:
        entries.append({
            "id": row[0],
            "user_id": row[1],
            "name": row[2],
            "date": row[3],
            "grateful": [row[4], row[5], row[6]],
            "prayers": [row[7], row[8], row[9]],
            "score": row[10]
        })

    already_entered, name = entry_exists_today()
    has_name = len(entries) > 0

    return render_template(
        "index.html",
        entries=entries,
        already_entered=already_entered,
        name=name,
        username=username,
        has_name=has_name
    )


@app.route("/add", methods=["POST"])
@login_required
def add_entry():
    user_id = int(session.get("user_id"))
    username = session.get("username")

    name = request.form.get("name", "").strip()[:50]
    if not name:
        name = username

    grateful = [
        request.form.get("grateful_1", "").strip()[:150],
        request.form.get("grateful_2", "").strip()[:150],
        request.form.get("grateful_3", "").strip()[:150],
    ]

    prayers = [
        request.form.get("prayer_1", "").strip()[:150],
        request.form.get("prayer_2", "").strip()[:150],
        request.form.get("prayer_3", "").strip()[:150],
    ]

    try:
        score = int(request.form.get("score", 5))
        score = max(0, min(10, score))
    except ValueError:
        score = 5

    if all(grateful) and all(prayers):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO entries 
            (user_id, name, date, grateful_1, grateful_2, grateful_3, prayer_1, prayer_2, prayer_3, score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, name, datetime.now().strftime("%d %b %Y"),
              grateful[0], grateful[1], grateful[2],
              prayers[0], prayers[1], prayers[2],
              score))
        conn.commit()
        cursor.close()
        conn.close()

    return redirect(url_for("index"))

@app.route("/delete/<int:entry_id>", methods=["POST"])
@login_required
def delete_entry(entry_id):
    user_id = int(session.get("user_id"))
    conn = get_db()
    cursor = conn.cursor()
    # Only delete if the entry belongs to the logged-in user
    cursor.execute("DELETE FROM entries WHERE id = %s AND user_id = %s", (entry_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("index"))


@app.route("/backdate", methods=["GET", "POST"])
@login_required
def backdate():
    user_id = int(session.get("user_id"))
    username = session.get("username")
    error = None
    success = None

    if request.method == "POST":
        date_str = request.form.get("date", "").strip()
        name = request.form.get("name", "").strip()[:50] or username

        grateful = [
            request.form.get("grateful_1", "").strip()[:150],
            request.form.get("grateful_2", "").strip()[:150],
            request.form.get("grateful_3", "").strip()[:150],
        ]
        prayers = [
            request.form.get("prayer_1", "").strip()[:150],
            request.form.get("prayer_2", "").strip()[:150],
            request.form.get("prayer_3", "").strip()[:150],
        ]

        try:
            score = int(request.form.get("score", 5))
            score = max(0, min(10, score))
        except ValueError:
            score = 5

        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
            if parsed_date.date() >= datetime.now().date():
                error = "Please choose a date in the past."
            elif not all(grateful) or not all(prayers):
                error = "Please fill in all fields."
            else:
                formatted_date = parsed_date.strftime("%d %b %Y")
                conn = get_db()
                cursor = conn.cursor()
                # Check if entry already exists for that date
                cursor.execute(
                    "SELECT id FROM entries WHERE date = %s AND user_id = %s",
                    (formatted_date, user_id)
                )
                existing = cursor.fetchone()
                if existing:
                    error = f"You already have an entry for {formatted_date}."
                    cursor.close()
                    conn.close()
                else:
                    cursor.execute("""
                        INSERT INTO entries
                        (user_id, name, date, grateful_1, grateful_2, grateful_3, prayer_1, prayer_2, prayer_3, score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (user_id, name, formatted_date,
                          grateful[0], grateful[1], grateful[2],
                          prayers[0], prayers[1], prayers[2],
                          score))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    success = f"Entry added for {formatted_date}."
        except ValueError:
            error = "Invalid date format."

    return render_template("backdate.html", error=error, success=success, username=username)


@app.route("/api/entries")
@login_required
def api_entries():
    user_id = int(session.get("user_id"))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entries WHERE user_id = %s ORDER BY id ASC", (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    entries = []
    for row in rows:
        entries.append({
            "id": row[0],
            "user_id": row[1],
            "name": row[2],
            "date": row[3],
            "grateful": [row[4], row[5], row[6]],
            "prayers": [row[7], row[8], row[9]],
            "score": row[10]
        })

    return jsonify(entries)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
