# bibliotecas
from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql  # Usar PyMySQL para conectar ao MySQL/MariaDB
from werkzeug.security import check_password_hash
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configuração da chave secreta
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'ItaloNicacioDEV')  # Use uma variável de ambiente para a chave secreta

# Configurações do banco de dados
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'database': os.environ.get('DB_NAME', 'automax'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
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
        print(f"Error connecting to database: {e}")
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
            flash('Erro ao conectar ao banco de dados.', 'error')
            return redirect(url_for('index'))

        cursor = conn.cursor(pymysql.cursors.DictCursor)  # Usar DictCursor para dicionários
        cursor.execute('SELECT * FROM empresasuser WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            print(f"User ID set in session: {session['user_id']}")  # Depuração
            return redirect(url_for('employees'))
        else:
            flash('Usuário ou senha inválidos.', 'error')
            return redirect(url_for('index'))
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        flash('Erro ao processar sua solicitação.', 'error')
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
        print("Não é possível iniciar a sessão, tente novamente!")  # Depuração
        return redirect(url_for('index'))
    return render_template('employees.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
