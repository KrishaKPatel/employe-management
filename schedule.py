import sqlite3
from datetime import datetime
from prettytable import PrettyTable

EMPLOYEE_DB_FILE = "employees.db"
AVAILABILITY_DB_FILE = "availability.db"
SCHEDULE_DB_FILE = "schedule.db"

#create the table
def create_availability_table():
    with sqlite3.connect(AVAILABILITY_DB_FILE) as connection:
        cursor = connection.cursor()
        # create availability table if it doesn't exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS availability (
                date TEXT,
                eid INTEGER,
                morning_availability TEXT,
                evening_availability TEXT,
                PRIMARY KEY (date, eid),
                FOREIGN KEY (eid) REFERENCES employees(eid)
            )
        """)
        connection.commit()

# create the table
def create_schedule_table():
    try:
        with sqlite3.connect(SCHEDULE_DB_FILE) as connection:
            cursor = connection.cursor()
            # create schedule table if it doesn't exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schedule (
                    date TEXT NOT NULL,
                    eid INTEGER NOT NULL,
                    morning_start TEXT,
                    morning_end TEXT,
                    evening_start TEXT,
                    evening_end TEXT,
                    PRIMARY KEY (date, eid),
                    FOREIGN KEY (eid) REFERENCES employees(eid)
                )
            ''')
            connection.commit()
    except sqlite3.Error as e:
        print("Error creating schedule table:", e)

#check that employee is present or not
def employee_exists_in_db(eid):
    with sqlite3.connect(EMPLOYEE_DB_FILE) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM employees WHERE eid = ?", (eid,))
        return cursor.fetchone() is not None

#check the date is future date or not
def is_future_date(date_str):
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date > datetime.today()
    except ValueError:
        return False

#check that time is valid or not
def is_valid_time(ts, st):
    try:
        if ts.lower() == 'none':
            return 'none'

        if ':' not in ts:
            hour = int(ts)
            if st == "evening" and 0 <= hour <= 8:
                ts = f"{hour + 12:02d}:00"
            else:
                ts = f"{hour:02d}:00"
        else:
            hour, minute = map(int, ts.split(':'))
            if st == 'morning' and 5 <= hour <= 12:
                ts = f"{hour:02d}:{minute:02d}"
            elif st == 'evening' and 12 <= hour <= 24:
                ts = f"{hour:02d}:{minute:02d}"
            else:
                return None

        return ts
    except ValueError:
        return None

def set_employee_availability():
    date = input("Enter date (YYYY-MM-DD): ")
    if not is_future_date(date):
        print("Please enter a future date.")
        return

    while True:
        eid = input("Enter Employee ID: ")
        if employee_exists_in_db(eid):
            break
        else:
            print("Invalid Employee ID. Please enter a valid Employee ID.")

    with sqlite3.connect(AVAILABILITY_DB_FILE) as connection:
        cursor = connection.cursor()

        create_availability_table()

        cursor.execute("SELECT * FROM availability WHERE date = ? AND eid = ?", (date, eid))
        ea = cursor.fetchone()

        if ea:
            mea = ea[2] is not None and ea[2] != ''
            eea = ea[3] is not None and ea[3] != ''

            if mea or eea:
                ca = input(
                    f"You've already set your availability for Employee ID {eid} on this date. Do you want to change it? (yes/no): ").lower()
                if ca != 'yes':
                    return

        ava = input("Are you available? (yes/no): ").lower()
        if ava == 'yes':
            while True:
                shift = input(f"For Employee ID {eid}, are you available for 'morning', 'evening', or 'both'? ")
                if shift in ['morning', 'evening', 'both']:
                    break
                print("Invalid choice. Please select 'morning', 'evening', or 'both'.")

            cursor.execute(
                "INSERT OR REPLACE INTO availability (date, eid, morning_availability, evening_availability) VALUES (?, ?, ?, ?)",
                (date, eid, shift if shift in ['morning', 'both'] else '',
                 shift if shift in ['evening', 'both'] else ''))
def manager_set_schedule():
    create_schedule_table()  # Ensure the schedule table exists
    date = input("Enter the date for which you're setting the schedule (YYYY-MM-DD): ")

    while True:
        eid = input("Enter Employee ID: ")
        if employee_exists_in_db(eid):
            break
        else:
            print("Invalid Employee ID. Please enter a valid Employee ID.")

    # Check the availability database for existing data
    with sqlite3.connect(AVAILABILITY_DB_FILE) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM availability WHERE date = ? AND eid = ?", (date, eid))
        existing_availability = cursor.fetchone()

    if not existing_availability:
        print(f"No availability has been set for Employee ID {eid} on this date. Please set availability first.")
        return

    mae = existing_availability[2] != ""
    eae = existing_availability[3] != ""

    available_shifts = set()
    if mae:
        available_shifts.add('morning')
    if eae:
        available_shifts.add('evening')

    print(f"Debug: Available shifts: {available_shifts}")

    if not available_shifts:
        print(f"No shifts available for Employee ID {eid} on this date.")
        return

    for shift_type in available_shifts:
        sti = input(f"Set start time for Employee ID {eid} in {shift_type} (HH:MM or 'none'): ")
        if sti.lower() == 'none':
            continue

        fst = is_valid_time(sti, shift_type)
        if not fst:
            print(f"Invalid {shift_type} start time. Please try again.")
            continue

        eti = input(f"Set end time for Employee ID {eid} in {shift_type} (HH:MM): ")
        fet = is_valid_time(eti, shift_type)
        if not fet:
            print(f"Invalid {shift_type} end time. Please try again.")
            continue

        # Update the schedule
        with sqlite3.connect(SCHEDULE_DB_FILE) as schedule_connection:
            schedule_cursor = schedule_connection.cursor()
            schedule_cursor.execute(
                "INSERT OR REPLACE INTO schedule (date, eid, morning_start, morning_end, evening_start, evening_end) VALUES (?, ?, ?, ?, ?, ?)",
                (date, eid, fst if shift_type == 'morning' else '',
                 fet if shift_type == 'morning' else '',
                 fst if shift_type == 'evening' else '',
                 fet if shift_type == 'evening' else '')
            )

    print("Schedule updated successfully.")

def get_employee_shift_hour(date, eid, hour, availability_data, schedule_data):
    ma = (
        availability_data[2] if isinstance(availability_data[2], str) else {}
    )
    ea = (
        availability_data[3] if availability_data[3] and isinstance(availability_data[3], str) else {}
    )
    ms = (
        dict(item.split(':') for item in schedule_data[1].split(',')) if isinstance(schedule_data[1], str) else {}
    )
    es = (
        dict(item.split(':') for item in schedule_data[2].split(',')) if schedule_data[2] and isinstance(schedule_data[2], str) else {}
    )

    def is_hour_in_range(start, end):
        return start <= hour < end

    def check_availability(availability_dict):
        if eid in availability_dict:
            start_hour, _ = map(int, availability_dict[eid]['start'].split(":"))
            end_hour, _ = map(int, availability_dict[eid]['end'].split(":"))
            return is_hour_in_range(start_hour, end_hour)
        return False

    def check_schedule(schedule_dict):
        if eid in schedule_dict:
            start_hour, _ = map(int, schedule_dict[eid]['start'].split(":"))
            end_hour, _ = map(int, schedule_dict[eid]['end'].split(":"))
            return is_hour_in_range(start_hour, end_hour)
        return False

    if check_availability(ma) or check_schedule(ms):
        return "✓"

    if check_availability(ea) or check_schedule(es):
        return "✓"

    return ""

def format_time(time_str):
    if time_str.lower() == 'none':
        return 'none'

    hour, minute = map(int, time_str.split(':'))
    return f"{hour:02d}:{minute:02d}"

# Add this function to your existing code
def view_schedule_for_date():
    date = input("Enter date (YYYY-MM-DD): ")

    # Fetching schedule data
    with sqlite3.connect(SCHEDULE_DB_FILE) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT eid FROM schedule WHERE date = ?", (date,))
        eid = [row[0] for row in cursor.fetchall()]

    if eid:
        # Fetching employee names for the specified employee IDs
        with sqlite3.connect(EMPLOYEE_DB_FILE) as connection:
            employee_cursor = connection.cursor()
            employee_cursor.execute("SELECT eid, fname FROM employees WHERE eid IN ({})".format(','.join('?' for _ in eid)), tuple(eid))
            employee_data = dict(employee_cursor.fetchall())

        # Fetching schedule data again for the specified date
        with sqlite3.connect(SCHEDULE_DB_FILE) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM schedule WHERE date = ?", (date,))
            schedule_data = cursor.fetchall()

        # Create a dictionary to store the schedule for each employee
        employee_schedule = {eid: [""] * 24 for eid in employee_data}

        for entry in schedule_data:
            eid, morning_start, morning_end, evening_start, evening_end = entry[1:]
            for hour in range(24):
                if (
                    (morning_start and morning_end and int(morning_start[:2]) <= hour < int(morning_end[:2])) or
                    (evening_start and evening_end and int(evening_start[:2]) <= hour < int(evening_end[:2]))
                ):
                    employee_schedule[eid][hour] = "✓"

        # Create a PrettyTable
        table = PrettyTable()
        table.field_names = ["Hour", *employee_data.values()]

        for hour in range(24):
            row_data = [f"{hour:02d}-{(hour + 1):02d}"]
            for eid, schedule in employee_schedule.items():
                row_data.append(schedule[hour])
            table.add_row(row_data)

        # Print the table
        print(table)
    else:
        print(f"No schedule data available for the specified date: {date}")


def emp_schedule_menu():
    while True:
        print("\nSchedule Menu:")
        print("1. Set Employee Availability")
        print("2. View Schedule for Date")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            set_employee_availability()
        elif choice == '2':
            view_schedule_for_date()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Try again.")

def Manager_schedule_menu():
    while True:
        print("\nSchedule Menu:")
        print("1. Set Employee Availability")
        print("2. Manager Set Employee Schedule")
        print("3. View Schedule for Date")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            set_employee_availability()
        elif choice == '2':
            manager_set_schedule()
        elif choice == '3':
            view_schedule_for_date()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Try again.")
