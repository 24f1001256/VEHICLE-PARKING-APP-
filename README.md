# VEHICLE-PARKING-APP-
MAD-1 PROJECT MAY 2025
# 🚗 Vehicle Parking App - MAD-I Project

A full-stack web application built as part of the **Modern Application Development - I (MAD-1)** course, May 2025. This app allows users to reserve parking spots in various lots, while providing administrators with full control over parking management, user tracking, and analytics.

---

## 📚 Project Description

The Vehicle Parking App is a multi-user system for managing 4-wheeler parking lots. The application supports:

- **Admin Role**: Lot creation, management of spots, viewing user data, and summary analytics.
- **User Role**: Registration, login, automatic parking spot reservation, history tracking, and payment summary.

This application is developed using **Flask, SQLite, Jinja2, HTML, Bootstrap**, and **Chart.js**.

---

## 🔧 Tech Stack

| Layer         | Technology Used        |
|--------------|------------------------|
| Backend       | Python + Flask         |
| Frontend      | HTML, CSS, Bootstrap   |
| Templating    | Jinja2                 |
| Database      | SQLite (programmatically created) |
| Charts        | Chart.js               |
| Authentication| Flask + Role-based logic |

---

## 🧑‍💻 Roles

- **Admin (Predefined)**: No registration; full access to system.
- **User**: Registers and reserves parking spaces automatically.

---

## 🧱 Database Models

- **User**: ID, full name, email, password
- **Admin**: Predefined in database creation
- **ParkingLot**: ID, name, location, price, pin, capacity, etc.
- **ParkingSpot**: ID, status (Available/Occupied), linked to lot
- **Reservation**: ID, user ID, spot ID, timestamps, cost

All models are created via SQLAlchemy and initialized using a Python script. No manual DB creation.

---

## ✅ Core Features

### 🔐 Authentication
- User registration and login
- Admin login (predefined credentials)
- Role-based dashboards

### 🛠️ Admin Dashboard
- Create/edit/delete parking lots (delete only if all spots are free)
- Auto-create spots based on capacity
- View all parking spots and user details
- Summary chart (available vs occupied spots)

### 🚙 User Dashboard
- View all parking lots
- Reserve first available spot
- Occupy and release spot (records timestamps)
- Parking history with durations and cost
- Chart visualization of history

---

## 🌟 Enhancements

- ✅ Search for spots/users in admin dashboard
- ✅ Chart.js integration for analytics
- ✅ Frontend + backend validation
- ✅ Responsive UI with Bootstrap
- ✅ Flask-Login integration for route protection
- (Optional) JSON APIs using Flask-Restful or Flask route controllers

---

## 🛠️ Installation & Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/<your-username>/vehicle-parking-app.git
   cd vehicle-parking-app
2. **Set up Virtual Environment**
  python -m venv venv
  source venv/bin/activate  # or venv\Scripts\activate on Windows
3. **Install Dependencies**
   pip install -r requirements.txt
4. **Run Initial Setup (Create DB)**
   python setup.py  # Initializes DB and predefined admin
5. **Start the Application**
   flask run

