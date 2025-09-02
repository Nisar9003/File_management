import mimetypes
import json
import os
from flask import Blueprint, request, jsonify, send_from_directory, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from docx import Document

file_bp = Blueprint('file_management', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_PROFILE_SIZE = 2 * 1024 * 1024  # 2MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_text_file(filepath):
    mime, _ = mimetypes.guess_type(filepath)
    ext = os.path.splitext(filepath)[1].lower()
    return mime and (mime.startswith('text') or mime == 'application/json') or ext == '.docx'

@file_bp.route('/upload_file', methods=['POST'])
@login_required
def upload_file():
    user_id = current_user.id
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = secure_filename(file.filename)
        user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
        os.makedirs(user_folder, exist_ok=True)
        file.save(os.path.join(user_folder, filename))
        return 'File uploaded', 200

@file_bp.route('/list_files', methods=['GET'])
@login_required
def list_files():
    user_id = current_user.id
    user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
    if not os.path.exists(user_folder):
        return jsonify([])
    files = [f for f in os.listdir(user_folder) if not f.startswith('profile.')]
    return jsonify(files)

@file_bp.route('/delete_file/<filename>', methods=['DELETE'])
@login_required
def delete_file(filename):
    user_id = current_user.id
    user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
    file_path = os.path.join(user_folder, secure_filename(filename))
    if os.path.exists(file_path):
        os.remove(file_path)
        return 'File deleted', 200
    else:
        return 'File not found', 404

@file_bp.route('/download_file/<filename>', methods=['GET'])
@login_required
def download_file(filename):
    user_id = current_user.id
    user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
    try:
        return send_from_directory(user_folder, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@file_bp.route('/update_profile_pic', methods=['POST'])
@login_required
def update_profile_pic():
    user_id = current_user.id
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if not allowed_file(file.filename):
        return 'Invalid file type', 400
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_PROFILE_SIZE:
        return 'File too large', 400
    filename = secure_filename(file.filename)
    user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    for ext in ALLOWED_EXTENSIONS:
        old_path = os.path.join(user_folder, f'profile.{ext}')
        if os.path.exists(old_path):
            os.remove(old_path)
    ext = filename.rsplit('.', 1)[1].lower()
    file.save(os.path.join(user_folder, f'profile.{ext}'))
    return 'Profile pic updated', 200

@file_bp.route('/get_profile_pic')
@login_required
def get_profile_pic():
    user_id = current_user.id
    user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
    for ext in ALLOWED_EXTENSIONS:
        path = os.path.join(user_folder, f'profile.{ext}')
        if os.path.exists(path):
            return send_from_directory(user_folder, f'profile.{ext}')
    return '', 204

@file_bp.route('/get_file_content/<filename>', methods=['GET'])
@login_required
def get_file_content(filename):
    user_id = current_user.id
    user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
    file_path = os.path.join(user_folder, secure_filename(filename))
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    ext = os.path.splitext(file_path)[1].lower()
    if is_text_file(file_path):
        if ext == '.docx':
            try:
                doc = Document(file_path)
                content = '\n'.join([p.text for p in doc.paragraphs])
            except Exception as e:
                return jsonify({'is_text': False, 'content': f'Error reading docx: {str(e)}'})
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        return jsonify({'is_text': True, 'content': content})
    else:
        return jsonify({'is_text': False, 'content': 'Cannot display non-text file.'})

@file_bp.route('/get_file_content_any/<filename>', methods=['GET'])
@login_required
def get_file_content_any(filename):
    # Only allow files in the project root for safety
    project_root = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.abspath(os.path.join(project_root, '..', filename))
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.txt', '.csv', '.json']:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'is_text': True, 'content': content})
    else:
        return jsonify({'is_text': False, 'content': 'Cannot display non-text file.'})

@file_bp.route('/save_file_content_any/<filename>', methods=['POST'])
@login_required
def save_file_content_any(filename):
    project_root = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.abspath(os.path.join(project_root, '..', filename))
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ['.txt', '.csv', '.json']:
        return jsonify({'error': 'Cannot edit non-text file'}), 400
    data = request.get_json()
    content = data.get('content', '')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return jsonify({'success': True})

@file_bp.route('/')
@login_required
def show_file_management():
    return current_app.send_static_file('file_management.html')