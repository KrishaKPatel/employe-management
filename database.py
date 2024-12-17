# database.py
import sqlite3

DATABASE_FILE = "employees.db"

def create_tables():
    # make the connection with database file
    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()

        # Create employees table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                eid INTEGER PRIMARY KEY,
                fname TEXT,
                lname TEXT,
                pos TEXT,
                email TEXT,
                address TEXT,
                phone TEXT,
                date_joined DATE DEFAULT CURRENT_DATE,
                salary REAL
            )
        """)

        # Create managers table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS managers (
                username TEXT PRIMARY KEY,
                password TEXT
            )
        """)

def execute_query(query, values=None, fetchone=False, fetchall=False, commit=True):
    # make the connection with database file
    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()

        # Create tables if they don't exist
        create_tables()

        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)

        if fetchone:
            return cursor.fetchone()
        elif fetchall:
            return cursor.fetchall()
        elif commit:
            connection.commit()

# check the username and password , if it exists then give access
# otherwise ask for setting up username and password then after give the access
def vmc(username, password):
    query = "SELECT * FROM managers WHERE username = ? AND password = ?" # get the data from managers table
    data = execute_query(query, (username, password), fetchone=True)

    if data:
        return True
    else:
        print("Invalid Manager Credentials. Access Denied.")
        setup_choice = input("Would you like to set up manager username and password? (yes/no): ").lower()
        if setup_choice == 'yes':
            smc(username, password)
            return True  # Return True if setup is successful
        else:
            return False  # Return False if the user chooses not to set up credentials


def smc(username, password):
    query = "INSERT INTO managers (username, password) VALUES (?, ?)" # insert the data into managers table
    execute_query(query, (username, password), commit=True)

    print("\nManager username and password set up successfully!")
