import logging


from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
from werkzeug.security import check_password_hash
import os
from dotenv import load_dotenv

import socket

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configuração da chave secreta
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'ItaloNicacioDEV')  # Use uma variável de ambiente para a chave secreta

# Configuração do logging
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurações do banco de dados
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'POSTGRES_PRISMA_URL="postgres://default:a1D6IXQoWiPT@ep-young-mud-a46g29gr-pooler.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require&pgbouncer=true&connect_timeout=15'),
}

def get_db_connection():
    """ Cria e retorna uma nova conexão com o banco de dados. """
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        return connection
    except pymysql.MySQLError as e:
        logging.error(f"Error connecting to database: {e}")
        return None

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            flash('Erro ao conectar ao banco de dados. Por favor, tente novamente mais tarde.', 'error')
            return redirect(url_for('index'))

        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM empresasuser WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('employees'))
        else:
            flash('Usuário ou senha inválidos.', 'error')
            return redirect(url_for('index'))
    except pymysql.MySQLError as e:
        logging.error(f"Database error: {e}")
        flash('Erro ao processar sua solicitação. Por favor, tente novamente mais tarde.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        logging.error(f"Error: {e}")
        flash('Erro ao processar sua solicitação. Por favor, tente novamente mais tarde.', 'error')
        return redirect(url_for('index'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/employees')
def employees():
    if 'user_id' not in session:
        flash('Você deve estar logado para acessar esta página.', 'warning')
        return redirect(url_for('index'))
    return render_template('employees.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
