#employee.py
# used database for store and load the data
# for reference: https://docs.python.org/3/library/sqlite3.html
import re
from database import execute_query
from datetime import datetime,date


class Employee:
    def __init__(self, eid, fname, lname, pos, email, address, phone, date_joined=None, salary='0.00'):
        if not self.validate_email(email):
            raise ValueError("Invalid email format.")
        self.eid = eid
        self.fname = fname
        self.lname = lname
        self.pos = pos
        self.email = email
        self.address = address
        self.phone = phone
        self._date_joined = date.today() if date_joined is None else date_joined # by default value is current date
        self.salary = round(float(salary), 2)  # This ensures the salary is a float rounded to 2 decimal places

    def __repr__(self):
        return f"\nEmployee Id: {self.eid}\nFull name: {self.fname} {self.lname}\nPosition: {self.pos}\nE-mail: {self.email}\nAddress: {self.address}\nPhone: {self.phone}\nDate of joined: {self._date_joined}\nSalary: {self.salary}"

    def get_full_name(self):
        return f"{self.fname} {self.lname}" #get the full name of employee

    @staticmethod
    def validate_email(email):
        email_regex = r"[^@]+@[^@]+\.[^@]+"
        return re.match(email_regex, email) # check the email format

    @staticmethod
    def validate_postal_code(pos_code):
        return pos_code.isalnum()

    @property
    def date_joined(self):
        return self._date_joined

    @date_joined.setter
    def date_joined(self, value):
        if value is None:
            self._date_joined = date.today() # if no value , value is today date
        elif value > date.today(): # check that date is not a future date
            raise ValueError("Date of joining cannot be in the future.")
        else:
            self._date_joined = value

    @staticmethod
    def validate_salary(salary):
        salary_regex = r"^\d+\.\d{2}$"
        return re.match(salary_regex, str(salary))

    def to_dict(self):
        return {
            "eid": self.eid,
            "fname": self.fname,
            "lname": self.lname,
            "pos": self.pos,
            "email": self.email,
            "address": self.address,
            "phone": self.phone,
            "date_joined": self._date_joined,
            "salary": "{:.2f}".format(float(self.salary))
        }

    @classmethod
    def from_dict(cls, data):
        e = cls(data["eid"], data["fname"], data["lname"], data["pos"], data["email"],
                data["address"], data["phone"], data["salary"])

        # Assign date_joined directly from the dictionary
        e._date_joined = data["date_joined"]

        return e

# load the data from database
def load_employees_from_database():
    query = "SELECT * FROM employees"
    data = execute_query(query, fetchall=True)
    emp = []

    for e in data:
        # Convert the salary to float if it's stored as a string
        e = list(e)
        e[-1] = float(e[-1])
        e[-2] = datetime.strptime(e[-2], '%Y-%m-%d').date() if e[-2] else None # for reference: https://www.programiz.com/python-programming/datetime/strptime

        emp.append(Employee(*e))

    return emp

# save the data into the database
def save_employees_to_database(employees):
    # Check if the employees table exists
    t = "SELECT name FROM sqlite_master WHERE type='table' AND name='employees'"
    te = execute_query(t, fetchone=True)

    if not te:
        # If the table doesn't exist, create it
        execute_query("""
            CREATE TABLE employees (
                eid INTEGER PRIMARY KEY,
                fname TEXT,
                lname TEXT,
                pos TEXT,
                email TEXT,
                address TEXT,
                phone TEXT,
                date_joined DATE,
                salary REAL
            )
        """)

    for emp in employees:
        query = "SELECT * FROM employees WHERE eid = ?"
        existing_employee = execute_query(query, (employee.eid,), fetchone=True)

        if existing_employee:
            # If the employee exists, perform an update
            uq = """
                UPDATE employees
                SET fname=?, lname=?, pos=?, email=?, address=?, phone=?, date_joined=?, salary=?
                WHERE eid=?
            """
            execute_query(uq, (emp.fname, emp.lname, emp.pos, emp.email,
                                         emp.address, emp.phone, emp.date_joined, emp.salary,
                                         emp.eid))

        # for reference: https://www.tutorialspoint.com/sqlite/sqlite_insert_query.htm
        else:
            # If the employee doesn't exist, perform an insert
            iq = """
                INSERT INTO employees (eid, fname, lname, pos, email, address, phone, date_joined, salary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            execute_query(iq, (emp.eid, emp.fname, emp.lname, emp.pos, emp.email,
                                         emp.address, emp.phone, emp.date_joined, emp.salary))

employees = []

#get the details from user
def get_employee_details_from_user(manager_mode=False):
    try:
        eid = int(input("Enter employee ID: "))
        # If the entered ID already exists, notify the user and return
        if any(emp.eid == eid for emp in employees):
            print(f"An employee with ID {eid} already exists!")
            return None
        fname = input("Enter first name: ")
        lname = input("Enter last name: ")
        pos = input("Enter position: ")
        email = input("Enter email: ")
        address = input("Enter full address: ")
        phone = input("Enter phone number: ")
        if manager_mode:  # if it is manager mode, the manager can enter the salary and date of joined
            new_value = input("Enter new salary: ")
            try:
                salary = float("{:.2f}".format(float(new_value)))
            except ValueError:
                print("Invalid salary format. Please enter a positive number with two decimal places.")
                return None
            doj_input = input("Enter date of joining (YYYY-MM-DD): ")
            try:
                doj = date.fromisoformat(doj_input)
            except ValueError:
                print("By default stores TODAY's date.")
                doj = None
        else:
            salary = 0.00  # Default salary for the employee is 0
            doj = None  # Default date of joining for employees is None

        emp = Employee(eid, fname, lname, pos, email, address, phone, date_joined=doj, salary=salary)
        return emp
    except ValueError as e:
        print(f"Error: {e}")
        return None


#add the employee
def create_employee():
    global employee
    emp = get_employee_details_from_user() # get the details from the user
    if emp:
        employees.append(employee)
        print(f"Employee {employee.get_full_name()} added successfully!")
    save_employees_to_database(employees) #save the data into database

def read_employee(eid):
    global employees
    employees = load_employees_from_database()  # Load employees data from the database
    for emp in employees:
        if emp.eid == eid:
            return emp
    return None

#view the details of employee
def view_employee():
    global employees
    employees = load_employees_from_database()  # Load employees directly from the database
    print("1. View by ID")
    print("2. View all")
    choice = input("Choose an option: ")
    if choice == '1':
        eid = int(input("Enter Employee ID: "))
        emp = read_employee(eid) #display the particular employee detail
        if emp:
            print(emp)
        else:
            print(f"Employee with ID {eid} not found!")
    elif choice == '2':
        for emp in employees:
            print(emp) #display all employees details

#update the employee details
def update_employee(eid, manager_mode=False):
    employees = load_employees_from_database()  # Load fresh data
    emp = read_employee(eid)
    if not emp:
        print(f"Employee with ID {eid} not found!")
        return

    print(f"Updating details for {emp.get_full_name()}.")
    fields = ['1. First Name', '2. Last Name', '3. Position', '4. Email', '5. Address', '6. Phone']

    # Extend the fields list when manager_mode is True
    if manager_mode:
        fields.extend(['7. Salary', '8. Date of Joining'])

    for field in fields:
        print(field)

    ch = input("Enter your choice: ")

    if ch == '1':
        nv = input("Enter new first name: ")
        emp.fname = nv
    elif ch == '2':
        nv = input("Enter new last name: ")
        emp.lname = nv
    elif ch == '3':
        nv = input("Enter new position: ")
        emp.pos = nv
    elif ch == '4':
        nv = input("Enter new email: ")
        emp.email = nv
    elif ch == '5':
        nv = input("Enter new full address: ")
        emp.address = nv
    elif ch == '6':
        nv = input("Enter new phone: ")
        emp.phone = nv
    elif ch == '7' and manager_mode:
        nv = input("Enter new salary: ")
        try:
            emp.salary = round(float(nv), 2)
        except ValueError:
            print("Invalid salary format. Please enter a positive number with two decimal places.")
            return
    elif ch == '8' and manager_mode:
        nv = input("Enter new date of joining (format: YYYY-MM-DD): ")
        try:
            emp.date_joined = date.fromisoformat(nv)
        except ValueError:
            print("Invalid date format. No changes made.")
            return
    else:
        print("Invalid choice! No changes made.")
        return

    # Update the list of employees with the modified employee
    ue = [e if e.eid != eid else emp for e in employees]

    # Save the updated list to the database
    save_employees_to_database(ue)
    print(f"Updated details for {emp.get_full_name()}.")

# delete the employee details
def delete_employee(eid):
    global employees
    # Load fresh data
    employees = load_employees_from_database()

    # Check if the employee with the given ID exists
    ed = next((e for e in employees if e.eid == eid), None)

    if not ed:
        print(f"Employee with ID {eid} not found!")
        return

    # Update the list by excluding the employee to delete
    emp = [e for e in employees if e.eid != eid]

    # Save the updated list to the database
    save_employees_to_database(emp)

    # Execute delete query to remove the employee from the database
    dq = "DELETE FROM employees WHERE eid = ?"
    execute_query(dq, (eid,), commit=True)

    print(f"Employee with ID {eid} deleted!")

#employee menu
def employee_menu():
    global employees
    employees = load_employees_from_database()
    while True:
        print("\nEmployee Management System:")
        print("1. View Employee")
        print("2. Update Employee")
        print("3. Delete Employee")
        print("4. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            view_employee() #display the employee detail
        elif choice == '2':
            try:
                emp_id = int(input("Enter Employee ID to update: "))
                update_employee(emp_id) #update the employee detail
            except ValueError:
                print("Please enter a valid integer for Employee ID.")
        elif choice == '3':
            try:
                emp_id = int(input("Enter Employee ID to delete: "))
                delete_employee(emp_id) #delete the employee detail
            except ValueError:
                print("Please enter a valid integer for Employee ID.")
        elif choice == '4':
            break
        else:
            print("Invalid choice! Try again.")

