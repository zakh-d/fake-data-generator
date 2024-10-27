import pyodbc
import os

# Ustawienia połączenia
server = 'localhost'
database = 'my_database'
username = 'sa'
password = 'Database!2021'

# Ścieżki do plików CSV i odpowiadające im tabele w bazie danych
csv_files = {
    'car_types_T1': '/home/car_types_T1.csv',
    'car_types_T2': '/home/car_types_T2.csv',
    'cars_T1': '/home/cars_T1.csv',
    'cars_T2': '/home/cars_T2.csv',
    'parking_stations_T1': '/home/parking_station_T1.csv',
    'parking_stations_T2': '/home/parking_station_T2.csv',
    'users_T1': '/home/users_T1.csv',
    'users_T2': '/home/users_T2.csv',
    'invoices_T1': '/home/invoice_T1.csv',
    'invoices_T2': '/home/invoice_T2.csv',
    'rents_T1': '/home/rents_T1.csv',
    'rents_T2': '/home/rents_T2.csv',
}

# Tworzenie połączenia
conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')
cursor = conn.cursor()

# Funkcja do wykonania BULK INSERT
def bulk_insert(table_name, csv_path):
    try:
        bulk_insert_sql = f"""
        BULK INSERT {table_name}
        FROM '{csv_path}'
        WITH (
            FIELDTERMINATOR = ',',  
            ROWTERMINATOR = '\\n',  
            FIRSTROW = 2            
        );
        """
        cursor.execute(bulk_insert_sql)
        print(f"Dane załadowane pomyślnie do tabeli {table_name}.")
    except Exception as e:
        print(f"Wystąpił błąd podczas ładowania danych do tabeli {table_name}: {e}")

# Wykonaj BULK INSERT dla każdej tabeli
for table_name, csv_path in csv_files.items():
    bulk_insert(table_name, csv_path)

# Zatwierdź zmiany i zamknij połączenie
conn.commit()
cursor.close()
conn.close()
