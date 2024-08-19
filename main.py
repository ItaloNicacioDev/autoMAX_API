#ver 0.0.5 - BETA
#bibliotecas
from flask import Flask, request, jsonify

app = Flask(__name__)

# Simula um banco de dados em memória
users_db = []

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

if __name__ == '__main__':
    app.run(debug=True)
