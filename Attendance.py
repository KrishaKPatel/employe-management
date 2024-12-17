import sqlite3
from datetime import datetime, timedelta
from database import create_tables as create_employees_tables  # Import the create_tables function for employees

DATABASE_FILE = "attendance.db"
EMPLOYEES_DATABASE_FILE = "employees.db"

def create_tables():
    # make the connection with database file
    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()

        # Create attendance table if it doesn't exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                eid INTEGER,
                action TEXT,
                timestamp DATETIME,
                FOREIGN KEY (eid) REFERENCES employees(eid)
            )
        """)

# get the data from employees table
def get_employees():
    with sqlite3.connect(EMPLOYEES_DATABASE_FILE) as connection:
        cursor = connection.cursor()

        # Create tables if they don't exist in employees database
        create_employees_tables()

        # Fetch all employees
        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()

    return [{'eid': emp[0], 'fname': emp[1], 'lname': emp[2]} for emp in employees]
def log_attendance(employee, action):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()

        # Create tables if it doesn't exist
        create_tables()

        # Insert attendance record
        cursor.execute("INSERT INTO attendance (eid, action, timestamp) VALUES (?, ?, ?)",
                       (employee['eid'], action, timestamp))

    return True

#calculating the hours by weekly and day
def calculate_hours(employee, mode='recent'):
    eid = str(employee['eid'])

    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()

        # Create tables if it doesn't exist
        create_tables()

        # fetch the data from the attendance table
        cursor.execute("SELECT action, timestamp FROM attendance WHERE eid = ? ORDER BY timestamp", (eid,))
        logs = cursor.fetchall()

    if mode == 'recent':
        if len(logs) < 2:
            return 0
        punch_ins = [log[1] for log in logs if log[0] == 'Punch-In']
        punch_outs = [log[1] for log in logs if log[0] == 'Punch-Out']

        ts = 0
        for pot in punch_outs:
            cpi = min((pit for pit in punch_ins if pit < pot),
                                   key=lambda x: abs(datetime.strptime(x, '%Y-%m-%d %H:%M:%S') - datetime.strptime(pot, '%Y-%m-%d %H:%M:%S')))
            ts += (datetime.strptime(pot, '%Y-%m-%d %H:%M:%S') - datetime.strptime(cpi, '%Y-%m-%d %H:%M:%S')).total_seconds()

        return ts / 3600

    elif mode == 'weekly':
        ts = 0
        pis = None
        today = datetime.today()
        ls = today - timedelta(days=(today.weekday() + 1) % 7)
        for log in logs:
            action, timestamp = log
            if action == "Punch-In":
                punch_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                if ls <= punch_time <= today:
                    print(f"Punch-In: {punch_time}")
                    pis = punch_time
            elif action == "Punch-Out" and pis:
                pot = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                if ls <= pot <= today:
                    print(f"Punch-Out: {pot}")
                    ts += (pot - pis).total_seconds()
                    pis = None

        return ts / 3600

def ewd(sh, sm, eh, em):

    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()

        # Check if the attendance table exists
        cursor.execute("PRAGMA table_info(attendance)")
        if not cursor.fetchall():
            # If the attendance table does not exist, return an empty list
            return []

        wei = set()  # Using a set to store unique employee IDs

        td = datetime.today().date()
        sdt = datetime(td.year, td.month, td.day, sh, sm)
        edt = datetime(td.year, td.month, td.day, eh, em)

        # Fetch attendance data for today's date and the given time range
        cursor.execute("""
            SELECT DISTINCT eid, timestamp
            FROM attendance
            WHERE timestamp BETWEEN ? AND ?
        """, (sdt.strftime('%Y-%m-%d %H:%M:%S'), edt.strftime('%Y-%m-%d %H:%M:%S')))
        rows = cursor.fetchall()

        for row in rows:
            eid, timestamp = row
            wei.add(eid)

        return list(wei)

#attendance menu
def attendance_menu():
    # Check if the attendance table exists
    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()
        cursor.execute("PRAGMA table_info(attendance)")
        table_info = cursor.fetchall()

        if not table_info:
            # If the attendance table does not exist, create it
            create_tables()

    employees = get_employees()

    if not employees:
        print("No employee data found. Please go back to the main menu.")
        return

    print("Select your name:")
    for idx, employee in enumerate(employees, 1):
        print(f"{idx}. {employee['fname']} {employee['lname']}")

    ch = int(input("Enter your choice: "))
    if 1 <= ch <= len(employees):
        se = employees[ch - 1]
        print(f"Hello, {se['fname']} {se['lname']}.")
        print("1. Punch-In\n2. Punch-Out\n3. Total Hours\n4. Total Weekly Hours")
        ac = int(input("Enter your choice: "))
        if ac == 1:
            if log_attendance(se, "Punch-In"):
                print("Punched In!")
        elif ac == 2:
            if log_attendance(se, "Punch-Out"):
                print("Punched Out!")
        elif ac == 3:
            hours = calculate_hours(se, 'recent')
            print(f"You've worked for {hours:.2f} recent hours.")
        elif ac == 4:
            hours = calculate_hours(se, 'weekly')
            print(f"You've worked for {hours:.2f} weekly hours.")
        else:
            print("Invalid choice!")
    else:
        print("Invalid choice!")

def tips_distribution():
    # Option for distributing tips
    ch = ['yes', 'no']
    print("Do you want to distribute tips? (yes/no)")
    for i, ch in enumerate(ch, start=1):
        print(f"{i}. {ch}")
    try:
        dis = int(input()) - 1
        dc = ch[dis].lower()
    except (ValueError, IndexError):
        dc = None  # Invalid choice

    if dc == 'yes':
        tr = input("Enter the time range (e.g., 8 or 20-20:30) to check how many employees are working: ")
        if '-' in tr:
            sts, ets = tr.split('-')
            # Check if minutes are included in the start_time_str
            if ':' in sts:
                sh, sm = map(int, sts.split(':'))
            else:
                sh, sm= int(sts), 0
            # Check if minutes are included in the end_time_str
            if ':' in ets:
                eh, em = map(int, ets.split(':'))
            else:
                eh, em = int(ets), 0
        else:
            sh, sm, eh, em = int(tr), 0, int(tr), 0

        # Fetch working employee IDs for the specified time range
        weid = ewd(sh, sm, eh, em)

        if not weid:
            print(f"No employees are working between hours {sh:02d}:{sm:02d}-{eh:02d}:{em:02d}.")
        else:
            print(f"{len(weid)} employees are working between hours {sh:02d}:{sm:02d}-{eh:02d}:{em:02d}.")

            # Establish connections to both databases
            with sqlite3.connect(DATABASE_FILE) as attendance_connection:
                with sqlite3.connect(EMPLOYEES_DATABASE_FILE) as employees_connection:
                    # Create cursors for both connections
                    ec = employees_connection.cursor()

                    # Retrieve employee names using the fetched employee IDs
                    emp = []
                    for eid in weid:
                        ec.execute("SELECT fname FROM employees WHERE eid = ?", (eid,))
                        result = ec.fetchone()
                        if result:
                            ec.append(result[0])

                    if not ec:
                        print("No employee names found.")
                    else:
                        print("Employees who worked during this time range:")
                        for emp in emp:
                            print(f"- {emp}")

                    tips = float(input("Enter the total tips for that time range: "))

                    if tips <= 0:
                        print("Invalid total tips value. Exiting tips distribution.")
                        return

                    tpe = tips / len(weid)
                    print(f"Each employee gets {tpe:.2f} from the tips.")
    elif dc == 'no':
        print("Okay, have a nice day!")
    else:
        print("Invalid choice!")


