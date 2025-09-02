import os
from flask import Flask, redirect, url_for, send_from_directory
from flask_login import LoginManager
from blueprint.user_management import user_bp, User, users
from blueprint.file_management import file_bp

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = os.urandom(24).hex()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_management.show_login'

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(file_bp, url_prefix='/files')

@app.route('/')
def index():
    return redirect(url_for('user_management.show_login'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)