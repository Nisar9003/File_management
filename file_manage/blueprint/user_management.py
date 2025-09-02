from flask import Blueprint, request, jsonify, redirect, url_for, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

user_bp = Blueprint('user_management', __name__)

# In-memory user storage for demonstration; replace with your database
users = {}
next_user_id = 1

class User:
    def __init__(self, id, username, password_hash, email=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.is_active = True
        self.is_authenticated = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.id)

@user_bp.route('/create_user', methods=['POST'])
def create_user():
    global next_user_id
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return 'Invalid data', 400
    username = data['username']
    password = data['password']
    if any(u.username == username for u in users.values()):
        return 'Username exists', 400
    user = User(next_user_id, username, generate_password_hash(password), data.get('email'))
    users[next_user_id] = user
    next_user_id += 1
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email}), 201

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return 'Invalid data', 400
    username = data['username']
    password = data['password']
    user = next((u for u in users.values() if u.username == username), None)
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'message': 'Login successful', 'user_id': user.id}), 200
    return 'Invalid credentials', 401

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user_management.show_login'))

@user_bp.route('/get_user/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    if current_user.id != user_id:
        return 'Unauthorized', 403
    user = users.get(user_id)
    if user:
        return jsonify({'id': user.id, 'username': user.username, 'email': user.email})
    return 'User not found', 404

@user_bp.route('/update_user/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    if current_user.id != user_id:
        return 'Unauthorized', 403
    user = users.get(user_id)
    if not user:
        return 'User not found', 404
    data = request.json
    if data:
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.password_hash = generate_password_hash(data['password'])
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email})

@user_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if current_user.id != user_id:
        return 'Unauthorized', 403
    if user_id in users:
        del users[user_id]
        return 'User deleted', 200
    return 'User not found', 404

@user_bp.route('/login', methods=['GET'])
def show_login():
    return send_from_directory('static', 'login.html')