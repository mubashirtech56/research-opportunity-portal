import os
from datetime import datetime
from flask import Flask, jsonify, request
import mysql.connector
from werkzeug.exceptions import HTTPException

app = Flask(__name__, static_folder="static", static_url_path="")

FIELDS = ["title", "description", "research_area", "faculty_name",
          "department", "required_skills", "positions", "deadline", "status"]


def get_db():
    # Credentials come from environment variables (never hard-code passwords)
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "research_portal"),
    )


def clean(row):
    row["deadline"] = row["deadline"].isoformat()
    return row


def validate(data, partial=False):
    """Return an error message, or None if the data is valid."""
    for f in FIELDS:
        if f in data:
            if data[f] is None or str(data[f]).strip() == "":
                return f"'{f}' cannot be empty"
        elif not partial and f != "status":
            return f"'{f}' is required"
    if "positions" in data:
        try:
            if int(data["positions"]) < 1:
                return "'positions' must be at least 1"
        except (ValueError, TypeError):
            return "'positions' must be a number"
    if "deadline" in data:
        try:
            datetime.strptime(str(data["deadline"]), "%Y-%m-%d")
        except ValueError:
            return "'deadline' must be in YYYY-MM-DD format"
    if "status" in data and data["status"] not in ("Open", "Closed"):
        return "'status' must be 'Open' or 'Closed'"
    return None


@app.route("/")
def home():
    return app.send_static_file("index.html")


# 1. CREATE
@app.route("/api/opportunities", methods=["POST"])
def create():
    data = request.get_json(silent=True) or {}
    error = validate(data)
    if error:
        return jsonify(error=error), 400
    data.setdefault("status", "Open")
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(
        f"INSERT INTO opportunities ({', '.join(FIELDS)}) VALUES ({', '.join(['%s'] * len(FIELDS))})",
        [data[f] for f in FIELDS])
    db.commit()
    new_id = cur.lastrowid
    cur.execute("SELECT * FROM opportunities WHERE id=%s", (new_id,))
    row = clean(cur.fetchone())
    db.close()
    return jsonify(row), 201


# 2. READ ALL
@app.route("/api/opportunities", methods=["GET"])
def get_all():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM opportunities ORDER BY id")
    rows = [clean(r) for r in cur.fetchall()]
    db.close()
    return jsonify(rows), 200


# 3. READ ONE
@app.route("/api/opportunities/<int:id>", methods=["GET"])
def get_one(id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM opportunities WHERE id=%s", (id,))
    row = cur.fetchone()
    db.close()
    if not row:
        return jsonify(error="Opportunity not found"), 404
    return jsonify(clean(row)), 200


# 4. UPDATE (also used to change status Open -> Closed)
@app.route("/api/opportunities/<int:id>", methods=["PUT"])
def update(id):
    data = request.get_json(silent=True) or {}
    data = {k: v for k, v in data.items() if k in FIELDS}
    if not data:
        return jsonify(error="No valid fields provided"), 400
    error = validate(data, partial=True)
    if error:
        return jsonify(error=error), 400
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id FROM opportunities WHERE id=%s", (id,))
    if not cur.fetchone():
        db.close()
        return jsonify(error="Opportunity not found"), 404
    sets = ", ".join(f"{k}=%s" for k in data)
    cur.execute(f"UPDATE opportunities SET {sets} WHERE id=%s", list(data.values()) + [id])
    db.commit()
    cur.execute("SELECT * FROM opportunities WHERE id=%s", (id,))
    row = clean(cur.fetchone())
    db.close()
    return jsonify(row), 200


# 5. DELETE
@app.route("/api/opportunities/<int:id>", methods=["DELETE"])
def delete(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM opportunities WHERE id=%s", (id,))
    db.commit()
    deleted = cur.rowcount
    db.close()
    if not deleted:
        return jsonify(error="Opportunity not found"), 404
    return jsonify(message="Opportunity deleted"), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Route not found"), 404


@app.errorhandler(Exception)
def server_error(e):
    if isinstance(e, HTTPException):
        return jsonify(error=e.description), e.code
    app.logger.exception(e)
    return jsonify(error="Internal server error"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
