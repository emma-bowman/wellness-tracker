from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from datetime import datetime
import psycopg2
import uuid
import os

app = Flask(__name__)
app.secret_key = "gratitude-app"


def get_db():
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
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
    user_id = session.get("user_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM entries WHERE date = %s AND user_id = %s", (today, user_id))
    entry = cursor.fetchone()
    cursor.close()
    conn.close()
    if entry is None:
        return False, None
    return True, entry[1]


@app.route("/")
def index():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())

    user_id = session.get("user_id")
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
    return render_template("index.html", entries=entries, already_entered=already_entered, name=name)


@app.route("/add", methods=["POST"])
def add_entry():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())

    user_id = session.get("user_id")

    name = request.form.get("name", "").strip()[:50]
    if not name:
        return redirect(url_for("index"))

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
        session["name"] = name
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
def delete_entry(entry_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entries WHERE id = %s", (entry_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("index"))


@app.route("/api/entries")
def api_entries():
    user_id = session.get("user_id")
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