import binary
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error as MySQLError
import psycopg2
from psycopg2 import OperationalError as PostgresError
from werkzeug.security import check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'supersecretkey')

# Configurações do banco de dados
DB_CONFIG_MYSQL = {
    'host': 'localhost',
    'port': 3306,
    'database': 'automax',
    'user': 'root',
    'password': os.environ.get('DB_PASSWORD', '@Eufr4sio123')
}

DB_CONFIG_POSTGRES = {
    'host': 'localhost',
    'port': 5432,
    'database': 'automax',
    'user': 'postgres',
    'password': os.environ.get('DB_PASSWORD', '@Eufr4sio123')
}


def get_db_connection():
    """ Cria e retorna uma nova conexão com o banco de dados, tentando MySQL e PostgreSQL. """
    connection = None
    try:
        # Tentar conectar ao MySQL
        connection = mysql.connector.connect(
            host=DB_CONFIG_MYSQL['host'],
            port=DB_CONFIG_MYSQL['port'],
            database=DB_CONFIG_MYSQL['database'],
            user=DB_CONFIG_MYSQL['user'],
            password=DB_CONFIG_MYSQL['password']
        )
        print("Conectado ao MySQL com sucesso!")
    except MySQLError as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        try:
            # Se a conexão MySQL falhar, tentar conectar ao PostgreSQL
            connection = psycopg2.connect(
                host=DB_CONFIG_POSTGRES['host'],
                port=DB_CONFIG_POSTGRES['port'],
                dbname=DB_CONFIG_POSTGRES['database'],
                user=DB_CONFIG_POSTGRES['user'],
                password=DB_CONFIG_POSTGRES['password']
            )
            print("Conectado ao PostgreSQL com sucesso!")
        except PostgresError as e:
            print(f"Erro ao conectar ao PostgreSQL: {e}")
            return None
    return connection


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            flash('Erro ao conectar ao banco de dados.', 'error')
            return redirect(url_for('index'))

        if conn.__class__.__name__ == 'MySQLConnection':
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM empresasUser WHERE username = %s', (username,))
        elif conn.__class__.__name__ == 'connection':
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
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


@app.route('/employees')  # página de cadastro de funcionário
def employees():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('employees.html')


@app.route('/')  # página inicial
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
