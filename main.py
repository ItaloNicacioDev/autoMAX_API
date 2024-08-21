#ver 0.0.40 - BETA
#bibliotecas
from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash
#----------------------------------------------------------------------------------------------
app = Flask(__name__)

# Configurações do banco de dados
DB_CONFIG = {
    'host': 'localhost',
    'database': 'automax',
    'user': 'root',
    'password': '@Eufr4sio123'
}
#processo de conexão
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

#-----------------------------------------------------------------------------------------------------------
#conexão com o processo flask
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    # Verifica se o usuário já existe
    for user in users_db:
        if user['email'] == email:
            return jsonify({"error": "User already exists"}), 400

    # Adiciona o usuário ao banco de dados simulado
    users_db.append({
        "username": username,
        "email": email,
        "password": password
    })

    return jsonify({"message": "User registered successfully"}), 201


@app.route('/')
def index():
    return render_template('index.html')

#faz  a ligação de login no mysql
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

#se usuario existe ele vai para a pag de cadastro se não volta para a pagina de login
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
