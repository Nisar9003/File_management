# File and User Management Flask Application

This is a Flask-based web application for user authentication and file management. Users can register, log in, log out, manage their profile, and perform file operations (upload, list, download, delete) with profile picture updates (PNG/JPEG/JPG, max 2MB, with cropping). The application uses Flask-Login for session management, blueprints for modular code, and optionally Flask-SQLAlchemy for persistent user storage with SQLite.

## Features
- **User Management**:
  - Register new users with a username, password, and optional email.
  - Log in and log out with session management.
  - View, update, and delete user accounts.
- **File Management**:
  - Upload files to a user-specific directory (`uploads/<user_id>`).
  - List, download, and delete files.
  - Update profile picture (PNG/JPEG/JPG, max 2MB) with client-side cropping using Cropper.js.
- **Security**:
  - Secure password hashing (using Werkzeug).
  - Login required for file operations and user management.
  - Randomly generated `SECRET_KEY` for sessions.
- **Frontend**:
  - Tailwind CSS for styling.
  - Client-side JavaScript for user and file operations.

## Prerequisites
- Python 3.8 or higher
- Virtualenv (recommended for isolated environments)
- A web browser for accessing the application

## Setup Instructions

1. **Clone or Set Up the Project**:
   - Ensure the project files are in `C:\Users\Mg\OneDrive\Desktop\file_manage\`.
   - The project structure should be:
     ```
     file_manage/
     ├── app.py
     ├── blueprint/
     │   ├── __init__.py
     │   ├── user_management.py
     │   ├── file_management.py
     ├── static/
     │   ├── login.html
     │   ├── file_management.html
     ├── uploads/
     ├── README.md
     ├── requirements.txt
     ```

2. **Create a Virtual Environment**:
   - Navigate to the project directory:
     ```bash
     cd C:\Users\Mg\OneDrive\Desktop\file_manage
     ```
   - Create and activate a virtual environment:
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```

3. **Install Dependencies**:
   - Install required packages:
     ```bash
     pip install -r requirements.txt
     ```
   - The `requirements.txt` should include:
     ```
     flask==3.0.3
     flask-login==0.6.3
     werkzeug==3.0.4
     flask-sqlalchemy==3.1.1  # If using SQLAlchemy
     ```

4. **Set Up the Uploads Folder**:
   - Ensure the `uploads/` folder is writable:
     ```bash
     icacls uploads /grant Everyone:F
     ```
   - The application creates user-specific subfolders (`uploads/<user_id>`) automatically.

5. **Set Up the Database (Optional)**:
   - If using SQLAlchemy for user management, the SQLite database (`database.db`) is created automatically in the project root when running `app.py`.
   - No manual database setup is required.

6. **Add a Favicon (Optional)**:
   - Place a `favicon.ico` file (16x16 or 32x32) in `static/` to avoid 404 errors.
   - Alternatively, ignore favicon errors (they are harmless).

7. **Run the Application**:
   - Start the Flask development server:
     ```bash
     python app.py
     ```
   - The app will run on `http://127.0.0.1:5000`.

## Usage
1. **Access the Application**:
   - Open `http://127.0.0.1:5000` in your browser.
   - You’ll be redirected to `/users/login` if not logged in.

2. **Register a User**:
   - On the login page (`/users/login`), click “Create one”.
   - Enter a username, password, and optional email.
   - After successful registration, log in with the credentials.

3. **Log In**:
   - Enter your username and password at `/users/login`.
   - On success, you’ll be redirected to `/files/` (file management page).

4. **File Management**:
   - At `/files/`:
     - **Upload Files**: Select and upload files to `uploads/<user_id>`.
     - **List Files**: View all uploaded files (excludes profile pictures).
     - **Download Files**: Download any listed file.
     - **Delete Files**: Remove files from your directory.
     - **Update Profile Picture**: Upload a PNG/JPEG/JPG file (max 2MB), crop it using Cropper.js, and save as `profile.<ext>`.

5. **Log Out**:
   - Click “Logout” on the file management page to return to `/users/login`.

## Routes
- **Main Routes**:
  - `GET /`: Redirects to `/users/login`.
  - `GET /favicon.ico`: Serves the favicon.
- **User Management Routes** (via `user_management` blueprint, prefixed with `/users`):
  - `GET/POST /users/login`: Show login page or handle login.
  - `POST /users/create_user`: Create a new user.
  - `GET /users/logout`: Log out the current user.
  - `GET /users/get_user/<user_id>`: Get user details (requires login).
  - `PUT /users/update_user/<user_id>`: Update user details (requires login).
  - `DELETE /users/delete_user/<user_id>`: Delete a user (requires login).
- **File Management Routes** (via `file_management` blueprint, prefixed with `/files`):
  - `GET /files/`: Show file management page.
  - `POST /files/upload_file`: Upload a file.
  - `GET /files/list_files`: List user’s files.
  - `DELETE /files/delete_file/<filename>`: Delete a file.
  - `GET /files/download_file/<filename>`: Download a file.
  - `POST /files/update_profile_pic`: Update profile picture.
  - `GET /files/get_profile_pic`: Retrieve profile picture.

## Dependencies
See `requirements.txt` for the full list:
- Flask: Web framework
- Flask-Login: Session management
- Werkzeug: Password hashing utilities
- Flask-SQLAlchemy: ORM for SQLite (optional, if using database)

## Notes
- **Security**:
  - The `SECRET_KEY` in `app.py` is randomly generated (`os.urandom(24).hex()`).
  - Replace with a fixed, secure key for production consistency.
  - Consider adding CSRF protection (e.g., Flask-WTF) for POST routes.
- **Production**:
  - The Flask development server is not suitable for production. Use Gunicorn:
    ```bash
    pip install gunicorn
    gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
    ```
  - Use HTTPS in production.
- **Database**:
  - The provided `user_management.py` may use an in-memory `users` dictionary. To use SQLite (as in your previous user management code), update `user_management.py` with Flask-SQLAlchemy:
    ```python
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String, unique=True, nullable=False)
        password_hash = db.Column(db.String, nullable=False)
        email = db.Column(db.String)
        is_active = db.Column(db.Boolean, default=True)
        def get_id(self):
            return str(self.id)
        def is_authenticated(self):
            return True
        def is_active(self):
            return self.is_active
        def is_anonymous(self):
            return False
    ```
  - Initialize the database in `app.py`:
    ```python
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    db.init_app(app)
    with app.app_context():
        db.create_all()
    ```
- **Frontend**:
  - `login.html` and `file_management.html` use Tailwind CSS and Cropper.js (via CDN).
  - Ensure internet access for CDN resources or host them locally.

## Troubleshooting
- **404 for `/files/`**:
  - Verify `blueprint/file_management.py` and `static/file_management.html` exist and match the provided code.
  - Check `app.py` registers the `file_management` blueprint.
- **404 for `/static/favicon.ico`**:
  - Place `favicon.ico` in `static/`.
- **Login Failures (401)**:
  - Ensure correct username/password.
  - If using SQLAlchemy, verify users exist in `database.db`.
- **File Upload Issues**:
  - Ensure `uploads/` is writable:
    ```bash
    icacls uploads /grant Everyone:F
    ```
- **ModuleNotFoundError**:
  - Confirm `blueprint/__init__.py` exists.
  - Run `python -c "from blueprint import user_management, file_management"` to test.

For further assistance, check the Flask documentation or provide error logs.