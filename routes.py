from functools import wraps
from flask import Flask,render_template,request,redirect,url_for,flash, session
from models import db,Users,ParkingLot,ParkingSpot,Reservation
from datetime import datetime
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

@app.context_processor
def inject_user():
    if 'user_id' in session:
        user = Users.query.filter_by(user_id=session['user_id']).first()
        return dict(user=user)
    return dict(user=None)

@app.route('/')
@auth_required
def home():
    user=Users.query.get(session['user_id'])
    return render_template('home.html',user=user)

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
    return redirect(url_for('home'))    

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
        if user_id=="admin":
            flash("Admin can't register, Admin can login with predefined credentials.")
            return redirect(url_for('login'))
        flash("Oh No! User ID already exists. Try a different ID.")
        return redirect(url_for('register'))
    user=Users(user_id=user_id, name=name, email_id=email_id, phone=phone)
    user.password = request.form.get("password")
    db.session.add(user)
    db.session.commit()
    flash("User successfully registered!")
    return redirect(url_for('login'))

@app.route('/summary')
@auth_required
def summary():
    user = Users.query.get(session['user_id'])

    if user.is_admin:
        lots = ParkingLot.query.all()
        lot_names = []
        total_spots = []
        booked_spots = []

        for lot in lots:
            lot_names.append(lot.lot_name)
            total = lot.capacity
            booked = ParkingSpot.query.filter_by(lot_id=lot.lot_id, availability=False).count()
            total_spots.append(total)
            booked_spots.append(booked)

        return render_template(
            'summary_admin.html',
            lot_names=lot_names,
            total_spots=total_spots,
            booked_spots=booked_spots
        )

    # 👇 User summary logic (must come after admin return)
    # Get all lots the user has booked spots in, and how many per lot
    result = (
        db.session.query(ParkingLot.lot_name, db.func.count(Reservation.reservation_id))
        .join(ParkingSpot, ParkingSpot.lot_id == ParkingLot.lot_id)
        .join(Reservation, Reservation.spot_id == ParkingSpot.spot_id)
        .filter(Reservation.user_id == user.user_id)
        .group_by(ParkingLot.lot_name)
        .all()
    )

    lot_names = [r[0] for r in result]
    bookings_per_lot = [r[1] for r in result]

    return render_template(
        'summary_user.html',
        lot_names=lot_names,
        bookings_per_lot=bookings_per_lot
    )
        
@app.route('/aboutus')
def aboutus():
    return render_template('about_us.html')

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
    lot_id = request.form.get('lot_id')
    lot_name = request.form.get('lot_name')
    location = request.form.get('location')
    capacity = int(request.form.get('capacity'))
    price = float(request.form.get('per_hour_cost'))

    if not all([lot_id, lot_name, location, capacity, price]):
        flash('The values cannot be empty')
        return redirect(url_for('add_lot'))

    if ParkingLot.query.get(lot_id):
        flash('Lot ID already exists. Please choose a different one.')
        return redirect(url_for('add_lot'))

    lot = ParkingLot(
        lot_id=lot_id,
        lot_name=lot_name,
        location=location,
        capacity=capacity,
        per_hour_cost=price
    )
    db.session.add(lot)
    db.session.commit()

    for i in range(1, capacity + 1):
        spot = ParkingSpot(
            spot_id = int(lot_id+str(i)),
            lot_id = lot_id,
            spot_number = i,
            availability = True
        )
        print('creating')
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

        extra_spots = ParkingSpot.query.filter(
            ParkingSpot.lot_id == lot_id,
            ParkingSpot.spot_number > new_capacity,
            ParkingSpot.availability == False  
        ).all()
        if extra_spots:
            flash("Cannot reduce capacity. Some spots beyond this limit are occupied.")
            return redirect(url_for('edit_lot', lot_id=lot_id))

        ParkingSpot.query.filter(
            ParkingSpot.lot_id == lot_id,
            ParkingSpot.spot_number > new_capacity
        ).delete()

    elif new_capacity > lot.capacity:
        for i in range(lot.capacity + 1, new_capacity + 1):
            new_spot = ParkingSpot(lot_id=lot_id, spot_number=i, availability=True)
            db.session.add(new_spot)

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

    db.session.delete(lot)
    db.session.commit()
    flash("Parking lot deleted successfully.", "success")
    return redirect(url_for('admin'))

@app.route('/admin/users')
@admin_required
def view_users():
    users=Users.query.filter_by(is_admin=False).all()
    return render_template('view_users.html',users=users)

@app.route('/dashboard')
@auth_required
def index():
    user = Users.query.get(session['user_id'])

    if user.is_admin:
        return redirect(url_for('admin'))

    parameter = request.args.get('parameter')
    query = request.args.get('query')
    lots = ParkingLot.query.all()

    lot_data = []
    for lot in lots:
        available = ParkingSpot.query.filter_by(lot_id=lot.lot_id, availability=True).count()
        lot_data.append({
            'lot': lot,
            'available_spots': available
        })

    if parameter and query:
        if parameter == 'lot_name':
            filtered_lots = ParkingLot.query.filter(ParkingLot.lot_name.ilike('%' + query + '%')).all()
        elif parameter == 'lot_id':
            filtered_lots = ParkingLot.query.filter(ParkingLot.lot_id.ilike('%' + query + '%')).all()
        elif parameter == 'location':
            filtered_lots = ParkingLot.query.filter(ParkingLot.location.ilike('%' + query + '%')).all()
        else:
            filtered_lots = lots
    else:
        filtered_lots = lots

    filtered_lot_data = []
    for item in lot_data:
        if item['lot'] in filtered_lots:
            filtered_lot_data.append(item)

    return render_template('index.html', user=user, lot_data=filtered_lot_data)

@app.route("/reserve", methods=["POST"])
@auth_required
def reserve():
    lot_id = request.form['lot_id']
    in_time_dt = datetime.strptime(request.form['in_time'], "%Y-%m-%dT%H:%M")
    out_time_dt = datetime.strptime(request.form['out_time'], "%Y-%m-%dT%H:%M")

    if out_time_dt <= in_time_dt:
        flash("Out-time must be after In-time.")
        return redirect(url_for('reserve'))
        lot = ParkingLot.query.get_or_404(lot_id)

    lot = ParkingLot.query.get_or_404(lot_id)

    # Get vehicle number
    vehicle_number = request.form['vehicle_number']

    # Find an available spot in the selected lot
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, availability=True).first()
    if not spot:
        flash("No available spots in this lot.", "warning")
        return redirect(url_for('book_spot', lot_id=lot_id))

    # Calculate price
    duration_hours = (out_time_dt - in_time_dt).total_seconds() / 3600
    price = round(duration_hours * lot.per_hour_cost, 2)

    # Mark spot unavailable
    spot.availability = False

    # Create and save reservation
    reservation = Reservation(
        spot_id=spot.spot_id,
        user_id=session['user_id'],
        parking_in_time=in_time_dt,
        parking_out_time=out_time_dt,
        vehicle_number=vehicle_number
    )

    db.session.add(reservation)
    db.session.commit()

    flash(f"Booked Spot {spot.spot_number} in Lot '{lot.lot_name}'. Estimated cost: ₹{price}", "success")
    return redirect(url_for('your_booking'))
    
@app.route('/yourbooking')
@auth_required
def your_booking():
    bookings = Reservation.query.filter_by(user_id=session['user_id']).all()
    return render_template('your_booking.html', bookings=bookings)

@app.route('/booking/<string:lot_id>')
@auth_required
def book_spot(lot_id):
    lot = ParkingLot.query.get(lot_id)
    available_spots = ParkingSpot.query.filter_by(lot_id=lot_id, availability=True).count()
    return render_template('book_spot.html', lot=lot, available_spots=available_spots)

@app.route('/release/<int:reservation_id>', methods=['POST'])
@auth_required
def release_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    # Ensure the booking belongs to the logged-in user
    if reservation.user_id != session['user_id']:
        flash("Not authorized to release this booking.", "danger")
        return redirect(url_for('your_booking'))

    # Free up the parking spot
    spot = ParkingSpot.query.get(reservation.spot_id)
    if spot:
        spot.availability = True

    # Delete or mark reservation as ended
    db.session.delete(reservation)
    db.session.commit()

    flash("Booking released and spot is now available.", "success")
    return redirect(url_for('your_booking'))
