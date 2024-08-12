import jwt
from flask import Flask, request, make_response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


app.config['SECRET'] = 'dumba'

users_db = {}


@app.route('/register', methods=['POST'])
def register():

    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username or passord not provided'}), 400

    if username in users_db:
        return jsonify({'error': 'User already exists'})

    hashed_pass = generate_password_hash(password)
    users_db[username] = hashed_pass

    return jsonify({'message': 'User created'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    print(request.headers)

    return 'great work'



@app.route('/home')
def home():
    content = {'please move along': 'Nothing to see here!'}
    return content


if __name__ == '__main__':
    app.run(port=3000, debug=False)
