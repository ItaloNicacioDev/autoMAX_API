# bibliotecas
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'supersecretkey')  # Use uma variável de ambiente para a chave secreta

# Configurações do banco de dados
DB_CONFIG = {
    'host': 'localhost',        # Alterado para 'localhost'
    'port': '3307',             # Porta padrão do MySQL
    'database': 'automax',
    'user': 'root',
    'password': os.environ.get('DB_PASSWORD', '@Eufr4sio123')  # Use uma variável de ambiente para a senha
}

def get_db_connection():
    """ Cria e retorna uma nova conexão com o banco de dados. """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    cursor = None
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            flash('Erro ao conectar ao banco de dados.', 'error')
            return redirect(url_for('index'))

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
        flash('Erro ao processar sua solicitação.', 'error')
        return redirect(url_for('index'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/employees')
def employees():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('employees.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
