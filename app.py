from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash

app = Flask(__name__)


# Função para verificar as credenciais
def check_credentials(username, password):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='automax',
            user='root',
            password='@Eufr4sio123'
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM empresasUser WHERE username = %s', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            return user
    except Error as e:
        print(f"Erro: {e}")

    return None


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = check_credentials(username, password)

    if user:
        return "Login bem-sucedido!"  # Aqui você pode redirecionar para outra página ou exibir uma mensagem de sucesso
    else:
        return render_template('login.html', error_message='Usuário ou senha inválidos.')


if __name__ == '__main__':
    app.run(debug=True)
