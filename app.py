from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import date

app = Flask(__name__)

# ------------------- Database Init -------------------
def init_db():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            coins INTEGER DEFAULT 0,
            energy INTEGER DEFAULT 10,
            max_energy INTEGER DEFAULT 10,
            last_bonus DATE,
            referral_code TEXT,
            referred_by TEXT,
            tap_power INTEGER DEFAULT 1
        )
    ''')
    # Tasks table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            task_name TEXT,
            completed INTEGER DEFAULT 0
        )
    ''')
    # Default user
    c.execute("INSERT OR IGNORE INTO users (id, referral_code) VALUES (1, 'REF-EASY001')")
    tasks = ["youtube_subscribe", "join_group_1", "join_group_2"]
    for t in tasks:
        c.execute("INSERT OR IGNORE INTO tasks (id, task_name) VALUES (?,?)", (tasks.index(t)+1, t))
    conn.commit()
    conn.close()

init_db()

# ------------------- Helper Functions -------------------
def get_user():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT coins, energy, max_energy, tap_power FROM users WHERE id=1")
    user = c.fetchone()
    conn.close()
    return user

def refill_energy():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT energy, max_energy FROM users WHERE id=1")
    energy, max_energy = c.fetchone()
    if energy < max_energy:
        energy += 1
        c.execute("UPDATE users SET energy=? WHERE id=1", (energy,))
        conn.commit()
    conn.close()

# ------------------- Routes -------------------
@app.route('/')
def home():
    refill_energy()
    return render_template('index.html')

@app.route('/api/user')
def user():
    refill_energy()
    coins, energy, max_energy, tap_power = get_user()
    # Get task status
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT task_name, completed FROM tasks")
    tasks = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    return jsonify({"coins": coins, "energy": energy, "max_energy": max_energy, "tap_power": tap_power, "tasks": tasks})

@app.route('/api/tap', methods=['POST'])
def tap():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT coins, energy, tap_power FROM users WHERE id=1")
    coins, energy, tap_power = c.fetchone()
    if energy > 0:
        coins += tap_power
        energy -= 1
        c.execute("UPDATE users SET coins=?, energy=? WHERE id=1", (coins, energy))
        conn.commit()
    conn.close()
    return jsonify({"coins": coins, "energy": energy})

@app.route('/api/daily_bonus', methods=['POST'])
def daily_bonus():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    today = date.today()
    c.execute("SELECT last_bonus FROM users WHERE id=1")
    last_bonus = c.fetchone()[0]
    if str(last_bonus) != str(today):
        c.execute("UPDATE users SET coins = coins + 50, last_bonus=? WHERE id=1", (today,))
        conn.commit()
        message = "🎁 EasySwap Daily Bonus Claimed!"
    else:
        message = "Already claimed today"
    conn.close()
    return jsonify({"message": message})

@app.route('/api/referral', methods=['POST'])
def referral():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    data = request.json
    referred_by = data.get("referred_by")
    c.execute("UPDATE users SET referred_by=? WHERE id=1", (referred_by,))
    c.execute("UPDATE users SET coins = coins + 20 WHERE referral_code=?", (referred_by,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Referral applied: +20 coins from {referred_by}"})

@app.route('/api/upgrade', methods=['POST'])
def upgrade():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    data = request.json
    upgrade_type = data.get("type")
    if upgrade_type == "tap_power":
        c.execute("UPDATE users SET tap_power = tap_power + 1, coins = coins - 50 WHERE id=1")
    elif upgrade_type == "max_energy":
        c.execute("UPDATE users SET max_energy = max_energy + 5, coins = coins - 50 WHERE id=1")
    conn.commit()
    conn.close()
    return jsonify({"message": f"{upgrade_type} upgraded!"})

@app.route('/api/task_complete', methods=['POST'])
def task_complete():
    data = request.json
    task_name = data.get("task")
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("UPDATE tasks SET completed=1 WHERE task_name=?", (task_name,))
    # Reward coins
    c.execute("UPDATE users SET coins = coins + 20 WHERE id=1")
    conn.commit()
    conn.close()
    return jsonify({"message": f"{task_name} completed! +20 coins"})

if __name__ == '__main__':
    app.run(debug=True)
