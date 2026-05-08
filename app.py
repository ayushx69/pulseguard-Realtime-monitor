from flask import Flask, render_template, request, redirect, jsonify, session
import sqlite3
import requests
import time
import os
import socket
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

app.secret_key = os.getenv("APP_SECRET_KEY", "pulseguard_secret_key_123")

DB_NAME = "monitors.db"

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "1234")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS monitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            url TEXT,
            status TEXT DEFAULT 'Unknown',
            response_time REAL DEFAULT 0,
            last_checked TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monitor_id INTEGER,
            status TEXT,
            response_time REAL,
            checked_at TEXT
        )
    """)

    try:
        c.execute("ALTER TABLE monitors ADD COLUMN monitor_type TEXT DEFAULT 'HTTP'")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


def is_logged_in():
    return session.get("logged_in") is True


def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram alert skipped: token/chat_id missing")
        return

    try:
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }

        response = requests.post(telegram_url, data=payload, timeout=10)

        if response.status_code == 200:
            print("Telegram alert sent successfully")
        else:
            print("Telegram alert failed:", response.text)

    except Exception as e:
        print("Telegram alert error:", e)


def check_http(url):
    retries = 2  # retry 2 times

    for attempt in range(retries):
        try:
            start = time.time()

            r = requests.get(
                url,
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )

            response_time = round((time.time() - start) * 1000, 2)

            # 500 se neeche sabko UP maan lo (403, 404 bhi)
            if r.status_code < 500:
                return "UP", response_time

        except Exception as e:
            print(f"HTTP attempt {attempt+1} failed:", e)

    return "DOWN", 0  

def check_ping(ip):
    try:
        start = time.time()

        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        response_time = round((time.time() - start) * 1000, 2)

        if result.returncode == 0:
            return "UP", response_time

        return "DOWN", 0

    except Exception as e:
        print("PING check error:", e)
        return "DOWN", 0


def check_tcp(target):
    try:
        if ":" not in target:
            return "DOWN", 0

        host, port = target.rsplit(":", 1)
        port = int(port)

        start = time.time()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)

        result = sock.connect_ex((host, port))
        sock.close()

        response_time = round((time.time() - start) * 1000, 2)

        if result == 0:
            return "UP", response_time

        return "DOWN", 0

    except Exception as e:
        print("TCP check error:", e)
        return "DOWN", 0


def check_target(monitor_type, target):
    monitor_type = monitor_type.upper().strip()

    if monitor_type == "HTTP":
        return check_http(target)

    if monitor_type == "PING":
        return check_ping(target)

    if monitor_type == "TCP":
        return check_tcp(target)

    return "DOWN", 0


def check_sites():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT id, name, url, status, monitor_type FROM monitors")
    sites = c.fetchall()

    for site_id, name, url, old_status, monitor_type in sites:
        new_status, response_time = check_target(monitor_type, url)

        c.execute("""
            UPDATE monitors
            SET status=?, response_time=?, last_checked=datetime('now')
            WHERE id=?
        """, (new_status, response_time, site_id))

        c.execute("""
            INSERT INTO history (monitor_id, status, response_time, checked_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (site_id, new_status, response_time))

        if old_status != "Unknown" and old_status != new_status:
            if new_status == "DOWN":
                message = f"""
🚨 <b>DOWN Alert</b>

<b>Service:</b> {name}
<b>Type:</b> {monitor_type}
<b>Target:</b> {url}
<b>Status:</b> DOWN
"""
                send_telegram_alert(message)

            elif new_status == "UP":
                message = f"""
✅ <b>Recovered</b>

<b>Service:</b> {name}
<b>Type:</b> {monitor_type}
<b>Target:</b> {url}
<b>Status:</b> UP
<b>Response Time:</b> {response_time} ms
"""
                send_telegram_alert(message)

    conn.commit()
    conn.close()


@app.route("/login", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect("/")

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/")
def index():
    if not is_logged_in():
        return redirect("/login")

    return render_template("index.html")


@app.route("/status")
def status_page():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        SELECT name, url, status, response_time, last_checked, monitor_type
        FROM monitors
        ORDER BY id DESC
    """)

    monitors = c.fetchall()
    conn.close()

    all_up = len(monitors) > 0 and all(m[2] == "UP" for m in monitors)

    return render_template("status.html", monitors=monitors, all_up=all_up)


@app.route("/api/monitors")
def api_monitors():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        SELECT id, name, url, status, response_time, last_checked, monitor_type
        FROM monitors
        ORDER BY id DESC
    """)

    rows = c.fetchall()
    monitors = []

    for row in rows:
        monitor_id = row[0]

        c.execute("""
            SELECT status
            FROM history
            WHERE monitor_id=?
            ORDER BY id DESC
            LIMIT 20
        """, (monitor_id,))

        history_rows = c.fetchall()
        total_checks = len(history_rows)
        up_checks = sum(1 for h in history_rows if h[0] == "UP")

        uptime = round((up_checks / total_checks) * 100, 1) if total_checks > 0 else 0

        monitors.append({
            "id": row[0],
            "name": row[1],
            "url": row[2],
            "status": row[3],
            "response_time": row[4],
            "last_checked": row[5],
            "monitor_type": row[6],
            "uptime": uptime
        })

    conn.close()

    total = len(monitors)
    up = len([m for m in monitors if m["status"] == "UP"])
    down = len([m for m in monitors if m["status"] == "DOWN"])
    unknown = len([m for m in monitors if m["status"] == "Unknown"])

    return jsonify({
        "monitors": monitors,
        "stats": {
            "total": total,
            "up": up,
            "down": down,
            "unknown": unknown
        }
    })


@app.route("/add", methods=["POST"])
def add():
    if not is_logged_in():
        return redirect("/login")

    name = request.form.get("name", "").strip()
    url = request.form.get("url", "").strip()
    monitor_type = request.form.get("monitor_type", "HTTP").strip().upper()

    if not name or not url:
        return redirect("/")

    if monitor_type not in ["HTTP", "PING", "TCP"]:
        monitor_type = "HTTP"

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        INSERT INTO monitors (name, url, monitor_type)
        VALUES (?, ?, ?)
    """, (name, url, monitor_type))

    conn.commit()
    conn.close()

    check_sites()
    return redirect("/")


@app.route("/delete/<int:id>")
def delete(id):
    if not is_logged_in():
        return redirect("/login")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("DELETE FROM monitors WHERE id=?", (id,))
    c.execute("DELETE FROM history WHERE monitor_id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/history/<int:id>")
def history(id):
    if not is_logged_in():
        return redirect("/login")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT name, url FROM monitors WHERE id=?", (id,))
    monitor = c.fetchone()

    if monitor is None:
        conn.close()
        return redirect("/")

    c.execute("""
        SELECT status, response_time, checked_at
        FROM history
        WHERE monitor_id=?
        ORDER BY id ASC
        LIMIT 30
    """, (id,))

    logs = c.fetchall()
    conn.close()

    return render_template("history.html", monitor=monitor, logs=logs)


@app.route("/test-alert")
def test_alert():
    if not is_logged_in():
        return redirect("/login")

    send_telegram_alert("✅ <b>PulseGuard Test Alert</b>\n\nTelegram alert system is working.")
    return "Test alert sent. Check Telegram."


if __name__ == "__main__":
    init_db()

    scheduler = BackgroundScheduler()
    scheduler.add_job(check_sites, "interval", seconds=60)
    scheduler.start()

    app.run(host="0.0.0.0", port=5000, debug=False)
