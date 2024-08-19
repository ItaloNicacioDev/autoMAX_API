#ver. BETA 0.0.4



#bibliotecas
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    # Simulate adding the user (implement your logic here)
    return jsonify({"message": "User registered successfully"}), 201

if __name__ == '__main__':
    app.run()
