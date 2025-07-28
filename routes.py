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

def admin_required(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'user_id' not in session:
            flash('Please login to continue')
            return redirect(url_for('index'))
        user=Users.query.get(session['user_id'])
        if not user.is_admin:
            flash('You are not authorised to view this page')
            return redirect('index.html')
        return func(*args,**kwargs)
    return inner

@app.route('/')
@auth_required
def index():
    user=Users.query.get(session['user_id'])
    if user.is_admin:
        return redirect(url_for('admin'))
    else:
        return render_template('index.html', user=user)

@app.route('/admin')
@admin_required
def admin():
    user=Users.query.get(session['user_id'])
    if not user.is_admin:
        flash("You're not authorised to view this page")
        return redirect(url_for('index'))
    parking_lot = ParkingLot.query.all()
    return render_template('admin.html', user=user,parking_lot=parking_lot)

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

@app.route('/booking')
@auth_required
def booking():
    return render_template('layout.html')

@app.route('/summary')
@auth_required
def summary():
    return render_template('layout.html')

@app.route('/aboutus')
def aboutus():
    return "IITM BS DEGREE MAD-1 PROJECT FOR DEVELOPING A WEB APPLICATION FOR FOUR-WHEELER VEHICLE PARKING USING HTML5, JINJA2, BOOTSTRAP, SQLITE3 AND PYTHON"

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/admin/add')
@admin_required
def add_lot():
    user=Users.query.get(session['user_id'])
    if not user.is_admin:
        flash("You're not authorised to view this page")
        return redirect(url_for('index'))
    return render_template('lot/add_lot.html', user=user)

@app.route('/admin/add', methods=['POST'])
@admin_required
def add_lot_post():
    lot_id=request.form.get('lot_id')
    lot_name=request.form.get('lot_name')
    location=request.form.get('location')
    capacity=request.form.get('capacity')
    if lot_id=='' or lot_name=='' or location=='' or capacity=='':
        flash('The values cannot be empty')
        return redirect(url_for('add_lot'))
    existing_lot = ParkingLot.query.get(lot_id)
    if existing_lot:
        flash('Lot ID already exists. Please choose a different one.')
        return redirect(url_for('add_lot'))
    lot=ParkingLot(lot_id=lot_id,lot_name=lot_name,location=location,capacity=capacity)
    db.session.add(lot)
    db.session.commit()
    flash('Lot added successfully')
    return redirect(url_for('admin'))
    for i in range(1, int(capacity) + 1):
        spot = ParkingSpot(
            lot_id=lot_id,
            spot_number=i,
            status='available'  # Or use whatever default you have
        )
    db.session.add(spot)
    db.session.commit()
    flash('Lot and parking spots added successfully.')
    return redirect(url_for('admin'))
        
@app.route('/admin/<string:lot_id>/delete')
@admin_required
def delete_lot(lot_id):
    user=Users.query.get(session['user_id'])
    lot = ParkingLot.query.get(lot_id)
    if not user.is_admin:
        flash("You're not authorised to view this page")
        return redirect(url_for('index'))
    return render_template('lot/delete_lot.html',user=user,lot=lot)
        

@app.route('/admin/<string:lot_id>/edit')
@admin_required
def edit_lot(lot_id):
    user=Users.query.get(session['user_id'])
    if not user.is_admin:
        flash("You're not authorised to view this page")
        return redirect(url_for('index'))
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        flash("Parking Lot not found.")
        return redirect(url_for('admin'))
    return render_template('lot/edit_lot.html', user=user,lot=lot)

@app.route('/admin/<string:lot_id>/edit', methods=['POST'])
@admin_required
def edit_lot_post(lot_id):
    user = Users.query.get(session['user_id'])
    if not user.is_admin:
        flash("You're not authorised to perform this action.")
        return redirect(url_for('index'))

    lot = ParkingLot.query.get(lot_id)
    if not lot:
        flash("Parking lot not found.")
        return redirect(url_for('admin'))

    new_name = request.form.get('lot_name')
    new_location = request.form.get('location')
    new_capacity = int(request.form.get('capacity'))

    if new_capacity < lot.capacity:
        # Check if any spots beyond new capacity are occupied
        extra_spots = ParkingSpot.query.filter(
            ParkingSpot.lot_id == lot_id,
            ParkingSpot.spot_number > new_capacity,
            ParkingSpot.availability == False  # or whatever your model uses
        ).all()
        if extra_spots:
            flash("Cannot reduce capacity. Some spots beyond this limit are occupied.")
            return redirect(url_for('edit_lot', lot_id=lot_id))
        
        # Optionally delete free extra spots
        ParkingSpot.query.filter(
            ParkingSpot.lot_id == lot_id,
            ParkingSpot.spot_number > new_capacity
        ).delete()

    elif new_capacity > lot.capacity:
        for i in range(lot.capacity + 1, new_capacity + 1):
            new_spot = ParkingSpot(lot_id=lot_id, spot_number=i, availability=True)
            db.session.add(new_spot)

    # Update lot details
    lot.lot_name = new_name
    lot.location = new_location
    lot.capacity = new_capacity
    db.session.commit()
    flash("Parking lot updated successfully.")
    return redirect(url_for('admin'))

@app.route('/admin/<string:lot_id>/show')
@admin_required
def show_lot(lot_id):
    user = Users.query.get(session['user_id'])
    lot=ParkingLot.query.get(lot_id)
    return render_template('lot/show_lot.html',user=user,lot=lot)

@app.route('/admin/<string:lot_id>/delete', methods=['POST'])
@admin_required
def delete_lot_post(lot_id):
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        flash("Lot does not exist", "danger")
        return redirect(url_for('admin'))
    occupied_spots = ParkingSpot.query.filter_by(lot_id=lot_id, availability=False).count()
    if occupied_spots > 0:
        flash("Cannot delete lot: Some parking spots are occupied.", "danger")
        return redirect(url_for('admin'))

@app.route('/users')
@admin_required
def view_users():
    users=Users.query.filter_by(is_admin=False).all()
    return render_template('view_users.html',users=users)