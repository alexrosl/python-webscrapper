from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

from src.db.db_utils import DbUtil, User

auth = Blueprint('auth', __name__)


@auth.route("/login")
def login():
    return render_template('login.html')


@auth.route("/login", methods=['POST'])
def login_post():
    login_name = request.form.get('login')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    db_util = DbUtil()
    user = db_util.read(User).filter(User.login == login_name).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return redirect(url_for('main.index'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


def generate_password(password):
    generate_password_hash(password, method='sha256')

