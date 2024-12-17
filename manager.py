# manager.py
from employee import get_employee_details_from_user
from database import execute_query, vmc, smc

# Check the username and password
def vms(username, password):
    if vmc(username, password):
        return True
    else:
        sc = input("Invalid Manager Credentials. Would you like to set up manager credentials? (yes/no): ").lower()
        if sc == 'yes':
            nu = input("Enter a new username: ")
            np = input("Enter a new password: ")
            if smc(nu, np):
                print("Manager credentials set up successfully! Access granted.")
                return True
            else:
                print("Failed to set up manager credentials.")
        else:
            print("Access Denied.")
        return False

# Add an employee by the manager
def add_employee():
    global emp
    emp = get_employee_details_from_user(manager_mode=True)  # get the details from the user
    if emp:
        query = "INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        execute_query(query, (emp.eid, emp.fname, emp.lname, emp.pos, emp.email, emp.address, emp.phone, str(emp._date_joined), emp.salary))

        print("Employee added successfully!")

