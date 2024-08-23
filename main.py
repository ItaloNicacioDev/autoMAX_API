from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user, login_required
from werkzeug.security import check_password_hash
import os
import pymysql

# Configuração para usar pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Eufr4sio123@localhost/automax'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'supersecretkey')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'


class User(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    permissions = db.Column(db.String(255), default='', nullable=False)
    accessible_pages = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

    @staticmethod
    def is_valid_username(username):
        return username.isalnum() or '_' in username or '.' in username

    @staticmethod
    def is_valid_email(email):
        import re
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def has_permission(self, permission):
        if not self.permissions:
            return False
        permissions = self.permissions.split(',')
        return permission in permissions

    def is_superadmin(self):
        return self.role == 'superadmin'

    def can_access_page(self, page):
        accessible_pages = self.accessible_pages.split(',') if self.accessible_pages else []
        return page in accessible_pages


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('employees'))
        else:
            flash('Usuário ou senha inválidos.', 'error')
            return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/employees')
@login_required
def employees():
    return render_template('employees.html')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
