import pyodbc

server = 'localhost'
database = 'my_database'
username = 'sa'
password = 'Database!2021'

sql_script = """

USE my_database
GO

CREATE TABLE parking_stations_T1 (
    id INT PRIMARY KEY,
    latitude FLOAT,
    longitude FLOAT,
    max_capacity INT
);
GO

CREATE TABLE parking_stations_T2 (
    id INT PRIMARY KEY,
    latitude FLOAT,
    longitude FLOAT,
    max_capacity INT
);
GO

CREATE TABLE car_types_T1 (
    id INT PRIMARY KEY,
    model VARCHAR(30),
    manufacturer VARCHAR(30),
    production_year INT,
    price_per_minute FLOAT
);
GO

CREATE TABLE car_types_T2 (
    id INT PRIMARY KEY,
    model VARCHAR(30),
    manufacturer VARCHAR(30),
    production_year INT,
    price_per_minute FLOAT
);
GO

CREATE TABLE users_T1 (
    id INT PRIMARY KEY,
    email VARCHAR(50),
    first_name VARCHAR(30),
    last_name VARCHAR(30)
);
GO

CREATE TABLE users_T2 (
    id INT PRIMARY KEY,
    email VARCHAR(50),
    first_name VARCHAR(30),
    last_name VARCHAR(30)
);
GO



CREATE TABLE cars_T1 (
    plate_number VARCHAR(10) PRIMARY KEY,
    station_id INT NULL,
    FOREIGN KEY (station_id) REFERENCES parking_stations_T1(id),
    car_type_id INT
);
GO

CREATE TABLE cars_T2 (
    plate_number VARCHAR(10) PRIMARY KEY,
    station_id INT NULL,
    FOREIGN KEY (station_id) REFERENCES parking_stations_T2(id),
    car_type_id INT
);
GO



CREATE TABLE rents_T1 (
    id INT PRIMARY KEY,
    renter INT,
    FOREIGN KEY (renter) REFERENCES users_T1(id),
    start_station_id INT,
    FOREIGN KEY (start_station_id) REFERENCES parking_stations_T1(id),
    start_date DATETIME,
    end_station_id INT NULL,
    FOREIGN KEY (end_station_id) REFERENCES parking_stations_T1(id),
    end_date DATETIME NULL,
    car_plate_number VARCHAR(10),
    FOREIGN KEY (car_plate_number) REFERENCES cars_T1(plate_number)
);
GO

CREATE TABLE rents_T2 (
    id INT PRIMARY KEY,
    renter INT,
    FOREIGN KEY (renter) REFERENCES users_T2(id),
    start_station_id INT,
    FOREIGN KEY (start_station_id) REFERENCES parking_stations_T2(id),
    start_date DATETIME,
    end_station_id INT NULL,
    FOREIGN KEY (end_station_id) REFERENCES parking_stations_T2(id),
    end_date DATETIME NULL,
    car_plate_number VARCHAR(10),
    FOREIGN KEY (car_plate_number) REFERENCES cars_T2(plate_number)
);
GO


CREATE TABLE invoices_T1 (
    number INT PRIMARY KEY,
    rent_id INT UNIQUE,
    FOREIGN KEY (rent_id) REFERENCES rents_T1(id),
    date DATE,
    currency VARCHAR(3),
    total_price FLOAT,
    description VARCHAR(100)
);
GO

CREATE TABLE invoices_T2 (
    number INT PRIMARY KEY,
    rent_id INT UNIQUE,
    FOREIGN KEY (rent_id) REFERENCES rents_T2(id),
    date DATE,
    currency VARCHAR(3),
    total_price FLOAT,
    description VARCHAR(100)
);
GO

"""

conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')
cursor = conn.cursor()

# Execute the SQL commands
for command in sql_script.split("GO"):
    command = command.strip()  # Remove leading and trailing whitespace
    if command:  # Only execute non-empty commands
        cursor.execute(command)

# Commit the changes
conn.commit()

# Clean up
cursor.close()
conn.close()