from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, ForeignKey
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
db=SQLAlchemy(app)

class Users(db.Model):
     __tablename__ = 'users'
     user_id = db.Column(db.String(32),primary_key=True)
     name = db.Column(db.String(32), nullable=False)
     _password_hash = db.Column('password', db.String(128), nullable=False)
     email_id = db.Column(db.String(64),nullable=True)
     phone = db.Column(db.BigInteger, nullable=False)
     is_admin = db.Column(db.Boolean, nullable=False, default = False)
     user_created = db.Column(db.DateTime,default=datetime.utcnow)
     last_logged_in = db.Column(db.DateTime)

     @property
     def password(self):
          raise AttributeError('password is write-only')
     
     @password.setter
     def password(self,plain_password):
          self._password_hash  = generate_password_hash(plain_password)

     def check_password(self,plain_password):
          return check_password_hash(self._password_hash, plain_password)

class ParkingLot (db.Model): 
     __tablename__ = 'parking_lot' 
     lot_id = db.Column(db.String(250),primary_key=True)
     lot_name = db.Column(db.String(250), nullable=False)     
     location = db.Column(db.String(250), nullable=False)
     capacity = db.Column(db.Integer, nullable=False)

class ParkingSpot (db.Model):  
     __tablename__ = 'parking_spot' 
     spot_id = db.Column(db.Integer, nullable=False,primary_key=True,autoincrement=True)     
     lot_id = db.Column(db.String(250), ForeignKey('parking_lot.lot_id'),nullable=False)
     spot_number = db.Column(db.Integer, nullable=False)
     availability = db.Column(db.Boolean, nullable=False)
     vehicle_number = db.Column(db.String(64), ForeignKey('reservation.vehicle_number'), nullable=False)

class Reservation(db.Model):  
     __tablename__ = 'reservation' 
     reservation_id = db.Column(db.Integer,primary_key=True)
     spot_id = db.Column(db.Integer,ForeignKey('parking_spot.spot_id'), nullable=False )
     user_id = db.Column(db.String(32),ForeignKey('users.user_id'), nullable=True) #foreign key?
     parking_in_time = db.Column(db.DateTime, nullable=False)
     parking_out_time = db.Column(db.DateTime, nullable=False)
     vehicle_number = db.Column(db.String(64), nullable=False)

with app.app_context():
     db.create_all()
     #Create Admin if admin doesnot exist
     admin = Users.query.filter_by(is_admin=True).first()
     if not admin:
          admin = Users(user_id='admin', password='admin', name='Admin', phone=0000000000, email_id="admin@gmail.com", is_admin=True)
          db.session.add(admin)
          db.session.commit()

