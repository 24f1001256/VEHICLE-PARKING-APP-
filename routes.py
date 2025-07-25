from functools import wraps
from flask import Flask,render_template,request,redirect,url_for,flash, session
from models import db,Users,ParkingLot,ParkingSpot,Reservation

from app import app

def auth_required(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'user_id' not in session:
            flash("Please login to continue.")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return inner

@app.route('/')
@auth_required
def index():
    return render_template('index.html', user=Users.query.get(session['user_id']))

@app.route('/profile')
@auth_required
def profile():
    return render_template('profile.html', user=Users.query.get(session['user_id']))

@app.route('/profile', methods=["POST"])
def profile_post():
    user=Users.query.get(session['user_id'])
    name = request.form.get('name')
    user_id = request.form.get('user_id')
    email_id = request.form.get('email_id')
    phone = request.form.get('phone')
    cpassword = request.form.get('cpassword')
    password = request.form.get('password')
    if user_id=='' or password=='' or cpassword=='':
        flash("Username or password cannot be empty.")
        return redirect(url_for('profile'))
    if not user.check_password(cpassword):
        flash("incorrect password.")
        return redirect(url_for('profile'))
    
    user.user_id=user_id
    user.name=name
    user.email_id=email_id
    user.phone=phone
    user.password=password
    db.session.commit()
    flash("Profile updated successfully!")
    return redirect(url_for('profile'))
    
    if Users.query.filter_by(user_id=user_id).first() and user_id!=user.user_id:
        flash("Oh No! User ID already exists. Try a different ID.")
        return redirect(url_for('register'))

@app.route('/login')    #never put auth_required in login or in register because we want the person to visit the site and login as he is not registered or logged in yet
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    
    if password=='' or user_id=='' :
        flash("User ID or Password cannot be empty.")
        return redirect(url_for("login"))
    user = Users.query.filter_by(user_id=user_id).first()
    if not user:
        flash('User does not exist.')
        return redirect(url_for('register'))
    if not user.check_password(password):
        flash('Incorrect password.')
        return redirect(url_for('login'))

    session['user_id'] = user.user_id
    #login_sucessful
    return redirect(url_for('index'))    

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    name = request.form.get('name')
    user_id = request.form.get('user_id')
    email_id = request.form.get('email_id')
    phone = request.form.get('phone')
    password = request.form.get('password')

    if password=='' or user_id=='' :
        flash("User ID or Password cannot be empty.")
        return redirect(url_for('register'))
    if name=='' or phone=='' :
        flash("Name or Phone number cannot be empty.")
        return redirect(url_for('register'))
    if Users.query.filter_by(user_id=user_id).first():
        flash("Oh No! User ID already exists. Try a different ID.")
        return redirect(url_for('register'))
    user=Users(user_id=user_id, name=name, email_id=email_id, phone=phone)
    user.password = request.form.get("password")
    db.session.add(user)
    db.session.commit()
    flash("User successfully registered!")
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)