#use W3school, stackoverflow, progamiz for checking syntax and overview

#Topic:Distributed employee management system
#2 view:manager and employee
#manager have all access that add,delete,view and update the employee details also they will create the schedule according to employee availability
#employee will add,delete,update and view the employee detail and they can give the availability and view the schedule

#this is main file
#main.py

from manager import vmc, add_employee
from employee import employee_menu, update_employee, delete_employee, view_employee
from schedule import emp_schedule_menu, Manager_schedule_menu
from Attendance import attendance_menu
from Attendance import tips_distribution

#manager menu
def manager_interface():
    while True:
        print("\nManager Interface:")
        print("\n---------------------------------")
        print("1. Display employees")
        print("2. Add new employee")
        print("3. Update employee details")
        print("4. Delete an employee")
        print("5. Employee Scheduling")
        print("6. Exit")

        ch = input("Enter your choice: ")

        if ch == '1':
            view_employee() #display all employee details
        elif ch == '2':
            add_employee() #add employee
        elif ch == '3':
            emp_id = int(input("Enter Employee ID to update: "))
            update_employee(emp_id, manager_mode=True) #update employee details
        elif ch == '4':
            emp_id = int(input("Enter Employee ID to delete: "))
            delete_employee(emp_id) #delete employee details
        elif ch == '5':
            Manager_schedule_menu() #scheduling
        elif ch == '6':
            break
        else:
            print("Invalid ch. Please try again.")

#employee menu
def employee_interface():
    while True:
        print("\nEmployee Menu:")
        print("\n---------------------------------")
        print("1. Employee Profile")
        print("2. Shift Scheduling")
        print("3. Attendance")
        print("4. Tips Distribution")
        print("5. Exit")

        ch = input("Enter your choice: ")

        if ch == '1':
            employee_menu() #employee profile
        elif ch == '2':
            emp_schedule_menu() #shift scheduling
        elif ch == '3':
            attendance_menu() #attendance
        elif ch == '4':
            tips_distribution() #tip distribution
        elif ch == '5':
            break
        else:
            print("Invalid ch! Try again.")

def main():
    while True:
        print("Welcome to the Employee Management System.")

        print("1. Manager")
        print("2. Employee")
        print("3. Exit")

        ch = input("Choose your role: ")

        if ch == '1':
            username = input("\nEnter your username: ")
            password = input("Enter your password: ")

            if vmc(username, password):
                print("Manager Login Successful.")
                manager_interface()
            else:
                print("Invalid Manager Credentials. Access Denied.")

        elif ch == '2':
            employee_interface()

        elif ch == '3':
            print("Thank you for using the Employee Management System!")
            break  # Exit the program

        else:
            print("Invalid ch. Please select from the provided options.")
            input("Press Enter to continue...")  # Pause for the user to read the message

if __name__ == "__main__":
    main()
