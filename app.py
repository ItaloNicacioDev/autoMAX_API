# ver 0.0.37 - BETA
# bibliotecas
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Chave secreta para sessões e flash messages

# Configurações do banco de dados
DB_CONFIG = {
    'host': 'localhost',
    'database': 'automax',
    'user': 'root',
    'password': '@Eufr4sio123'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM empresasUser WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('employees'))
        else:
            flash('Usuário ou senha inválidos.', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        print(f"Error: {e}")
        flash('Erro ao conectar ao banco de dados.', 'error')
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

@app.route('/employees')
def employees():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('employees.html')

@app.route('/')
def index():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)