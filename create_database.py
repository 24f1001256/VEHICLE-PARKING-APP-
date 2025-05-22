import sqlite3
conn = sqlite3.connect("vehicle_parking_app.db")
cur=conn.cursor()
cur.execute("PRAGMA foreign_keys = ON;")
cur.execute('''
	CREATE TABLE IF NOT EXISTS users(
	user_id TEXT PRIMARY KEY,
	name TEXT,
	email_id TEXT,
	phone TEXT,
	role TEXT,
	user_created DATETIME,
	last_logged_in DATETIME
);
''')
cur.execute('''
    CREATE TABLE IF NOT EXISTS parking_lot(
    lot_id TEXT PRIMARY KEY,
    lot_name TEXT,
    location TEXT,
    capacity INTEGER
);
''')
cur.execute('''
    CREATE TABLE IF NOT EXISTS parking_spot(
    spot_id TEXT PRIMARY KEY,
    lot_id TEXT,
    spot_number INTEGER,
    availability BOOLEAN,
    FOREIGN KEY(lot_id) REFERENCES parking_lot(lot_id)                                      
);
''')
cur.execute('''
    CREATE TABLE IF NOT EXISTS reservation(
    reservation_id TEXT PRIMARY KEY,
    user_id TEXT,
    spot_id TEXT,
    parking_in_time DATETIME,
    parking_out_time DATETIME,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(spot_id) REFERENCES parking_spot(spot_id)           
);
''')
cur.execute('''
    INSERT OR IGNORE INTO users (user_id, name, email_id, phone, role, user_created, last_logged_in)
    VALUES('admin1','Admin User','admin@gmail.com', '1234567890','admin', DATETIME('now'), DATETIME('now')
);
''')
conn.commit()
conn.close()
