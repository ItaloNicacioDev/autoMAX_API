# ver 0.0.5 - BETA
# bibliotecas
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Chave secreta para sessões e flash messages

# Configurações do banco de dados
DB_CONFIG = {
    'host': 'localhost',
    'database': 'your_database_name',
    'user': 'your_username',
    'password': 'your_password'
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
            return redirect(url_for('employees'))  # Redireciona para a página de funcionários
        else:
            return render_template('login.html', error_message='Usuário ou senha inválidos.')
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/employees')
def employees():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('employees.html')

@app.route('/get_employees')
def get_employees():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM employees')
        employees = cursor.fetchall()
        return jsonify(employees)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/add_employee', methods=['POST'])
def add_employee():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    name = request.form.get('name')
    position = request.form.get('position')
    salary = request.form.get('salary')

    if not name or not position or not salary:
        return jsonify({"error": "All fields are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO employees (name, position, salary) VALUES (%s, %s, %s)',
                       (name, position, salary))
        conn.commit()
        return jsonify({"message": "Employee added successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/delete_employee/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM employees WHERE id = %s', (employee_id,))
        conn.commit()
        return jsonify({"message": "Employee deleted successfully"}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
