from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chave-secreta'
DB = 'database.db'

# --- Inicializa o banco se não existir ---
def init_db():
    if not os.path.exists(DB):
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    coins INTEGER DEFAULT 100
                )
            ''')
            c.execute('''
                CREATE TABLE videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    user_id INTEGER,
                    watched_by TEXT DEFAULT ''
                )
            ''')
            conn.commit()

init_db()

# --- Rota: Login ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE username=? AND password=?', (user, pw))
            data = c.fetchone()
            if data:
                session['user_id'] = data[0]
                session['username'] = data[1]
                session['coins'] = data[3]
                if user == "Danilo" and pw == "12022005":
                    return redirect('/admin')
                return redirect('/dashboard')
            flash('Usuário ou senha inválidos.')
    return render_template('login.html')

# --- Rota: Cadastro ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        try:
            with sqlite3.connect(DB) as conn:
                c = conn.cursor()
                c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (user, pw))
                conn.commit()
                print(f"[ALERTA] Novo cadastro: {user}")
                return redirect('/')
        except sqlite3.IntegrityError:
            flash('Nome de usuário já existe.')
    return render_template('register.html')

# --- Rota: Dashboard do usuário ---
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('dashboard.html', username=session['username'], coins=session['coins'])

# --- Rota: Painel do Administrador ---
@app.route('/admin')
def admin():
    if session.get('username') != 'Danilo':
        return redirect('/')
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM users')
        users = c.fetchall()
        c.execute('SELECT * FROM videos')
        videos = c.fetchall()
    return render_template('admin.html', users=users, videos=videos)

# --- Logout ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
