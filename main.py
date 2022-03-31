try:
    from mysql.connector import connect, errors
    from setup import setup
except ModuleNotFoundError:
    print("Dependency not found. Please run 'pip install -r requirements.txt' to install all dependencies.")
    quit()

import os
from typing import List, Tuple, Dict, Any, Optional
from random import randint, choice as randchoice
from datetime import datetime
print("Starting...")
LOGGED_IN = False
LOGGED_IN_AS = ""
CURRENT_PAGE = -1
LOGGED_IN_ID = -1

first_names = [
    "James",
    "Robert",
    "John",
    "Michael",
    "William",
    "David",
    "Mary",
    "Patricia",
    "Elizabeth",
    "Susan",
    "Barbara",
]
last_names = [
    "Smith",
    "Johnson",
    "Williams",
    "Jones",
    "Brown",
    "Davis",
    "Miller",
    "Wilson",
    "Moore",
    "Taylor",
    "Anderson",
]


def cls():
    # Inter platform clear screen
    # cls is for windows, clear is for *nix platforms like linux
    # nt represents windows
    os.system("cls" if os.name == "nt" else "clear")


def login() -> Tuple[bool, str, int]:
    username = input("Login Username: ")
    password = input("Login Password: ")
    cursor.execute("SELECT role, employee_id FROM logins WHERE username = %s AND password = %s", (username, password))
    if cursor.rowcount == 1:
        print("Login Successful!")
        row = cursor.fetchone()
        return (True, row[0], row[1])
    else:
        print("Login Failed!")
        input("Press Enter to retry...")
        return (False, "", -1)


def prompt_input_int(input_str:str, minimum: int, maximum: Optional[int]=None):
    while True:
        try:
            user_choice = input(input_str)
            if int(user_choice) < minimum or (maximum and int(user_choice) > maximum):
                raise ValueError
        except ValueError:
            print("Invalid input! Try again")
            input("Press Enter to continue...")
            continue
        else:
            return int(user_choice)


def prompt_menu(page_name: str, choices: List[str]) -> int:

    while True:
        cls()
        print(f"\n{page_name}\n")
        print("Choose an option:")
        for i, choice in enumerate(choices):
            print(f"{i + 1}: {choice}")
        user_choice = input("\n> ")
        try:
            user_choice = int(user_choice)
            if user_choice < 1 or user_choice > len(choices):
                raise ValueError
        except ValueError:
            print("Invalid choice! Try again")
            input("Press Enter to continue...")

            continue
        else:
            return user_choice


def show_table(columns: List[str], rows: List[Tuple], to_cls=True) -> None:
    if to_cls:
        cls()
    space_deltas = []

    for i in range(len(columns)):
        col_name = columns[i]
        max_row = max(rows, key=lambda x: len(str(x[i])))
        delta = len(str(max_row[i])) - len(col_name) if len(str(max_row[i])) > len(col_name) else 0
        space_deltas.append(delta + 1)

    # ----------
    print("+", end="")
    for i, col in enumerate(columns):
        print(f"-" * (len(col) + space_deltas[i] + 1), end="")
        print("+", end="")
    print()
    # Columns
    for i, col in enumerate(columns):
        print("| ", end="")
        print(f"{col}" + " " * space_deltas[i], end="")
    print("|\n", end="")
    # ---------
    print("|", end="")
    for i, col in enumerate(columns):
        print(f"-" * (len(col) + space_deltas[i] + 1), end="")
        print("+" if i != len(columns) - 1 else "|", end="")
    # Rows
    for i, row in enumerate(rows):
        print("\n| ", end="")
        for j, col in enumerate(row):
            print(f"{col}" + " " * (space_deltas[j] - len(str(col)) + len(columns[j])), end="")
            print("| ", end="")
    # ----------
    print()
    print("+", end="")
    for i, col in enumerate(columns):
        print(f"-" * (len(col) + space_deltas[i] + 1), end="")
        print("+", end="")


def prompt_input(required_columns: dict, optional_columns: dict) -> Dict[str, Any]:
    result = {}
    for column in required_columns:
        while True:
            print(f"{column}: ", end="")
            user_input = input()
            try:
                user_input = required_columns[column](user_input)
                if user_input == "":
                    raise ValueError
            except ValueError:
                print("Invalid input! Try again")
                continue
            else:
                result[column] = user_input
                break

    for column in optional_columns:
        while True:
            print(f"{column}: ", end="")
            user_input = input()
            if user_input != "":
                try:
                    result[column] = optional_columns[column](user_input)
                except ValueError:
                    print("Invalid input! Try again")
                    continue
            else:
                result[column] = optional_columns[column]()
            break

    return result


def search_product(return_value=False):
    """Returns None if no product is found else Tuple of (model_number, name, price, quantity, discount, final_price)"""
    identifier = input("Enter the model number or name of the product: ").lower()
    if identifier == "":
        if not return_value:
            print("No product found with that identifier!")
            input("Press Enter to continue...")
        return
        
    cursor.execute(
        "SELECT model_number, name, price, quantity, discount, price - discount/100 * price FROM products WHERE lower(model_number) LIKE %s OR lower(name) LIKE %s",
        (f"%{identifier}%", f"%{identifier}%"),
    )
    data = cursor.fetchall()

    if len(data) > 1:
        show_table(["S. No", "Model Number", "Name", "Price", "Quantity", "Discount", "Final Price"], [(i+1, row[0], row[1], row[2], row[3], row[4], row[5]) for i, row in enumerate(data)], False)
        print("\n\n")
        user_choice = prompt_input_int("Choose a product: ", 1, len(data))
        data = data[user_choice - 1]
    elif len(data) == 1:
        data = data[0]

    if return_value:
        return data

    if not data:
        print("No product found with that identifier!")
        input("Press Enter to continue...")
    
    show_table(["Model Number", "Name", "Price", "Quantity", "Discount", "Final Price"], [data]),
    input("\n\nPress Enter to continue...")


def view_detailed_sale(invoice_number):
    cursor.execute("SELECT S.invoice_number, E.id AS 'Employee ID', E.name AS 'Employee name', C.name AS 'Customer Name', C.phone, S.sale_date, S.payment_method, P.name, S.base_price, S.discount, S.quantity, S.quantity* (S.base_price - ((S.discount/100) * S.base_price)) AS 'Final Price' FROM sales S, staff E, customers C, products P WHERE S.employee_id = E.id AND S.customer_id = C.id AND S.product_model_number = P.model_number AND S.invoice_number = %s;", (invoice_number,))
    data = cursor.fetchall()
    if not data:
        print("No sale found with that invoice number!")
        input("Press Enter to continue...")
        return
    employee_id, employee_name, customer_name, customer_phone, sale_date, payment_method = data[0][1:7]
    cls()
    print(f"Sale Details\n\nInvoice Number: {invoice_number}")
    print(f"Sale made by: {employee_name} (Id: {employee_id})")
    print(f"Customer Name: {customer_name}")
    print(f"Customer Phone: {customer_phone}")
    print(f"Date of Sale: {sale_date}")
    print(f"Mode of Payment: {payment_method}")

    print("\nProducts Sold:")
    show_table(["Product Name", "Price", "Quantity", "Discount", "Final Price"], [(row[7], row[8], row[10], row[9], f"{row[11]:.2f}") for row in data] + [("","","","",""),("", "", "", "Total", f"{sum([row[11] for row in data]):.2f}")], to_cls=False)
    input("\n\nPress Enter to continue...")


def view_multiple_sales(data):
    if not data:
        print("No sales made yet =(")
        input("Press Enter to continue...")
        return

    show_table(["Invoice Number", "Emloyee Name", "Customer Name", "Customer Phone Number", "Date of Sale", "Mode of Payment", "Total Amount"], data)
    print("\n\nEnter the invoice number of the sale you want to view. Enter 0 to go back.")
    invoice_number = prompt_input_int("Invoice Number: ", 0)
    if invoice_number == 0:
        return
        
    view_detailed_sale(invoice_number)


def inventory_management_menu():
    global CURRENT_PAGE, db
    choice = -1
    while True:
        choices = ["View Products", "Add Product", "Update Product", "Delete Product", "Back"]
        if choice == -1:
            choice = prompt_menu("Inventory Management", choices)
        cls()
        # View Products
        if choice == 1:
            view_choices = ["View All", "Sort", "Back"]
            view_choice = prompt_menu("View Products", view_choices)
            cls()
            # View All
            if view_choice == 1:
                cursor.execute(
                    "SELECT model_number, name, price, quantity, discount, price - discount/100 * price FROM products"
                )
                data = cursor.fetchall()
                if not data:
                    print("No products found!")
                else:
                    show_table(["Model Number", "Name", "Price", "Quantity", "Discount", "Final Price"], data)
                input("\nPress Enter to continue...")
            # Sort
            elif view_choice == 2:
                sort_by_choices = ["Sort by Name", "Sort by Price", "Sort by Quantity", "Sort by Discount", "Back"]
                sort_by_choice = prompt_menu("Sort Products", sort_by_choices)

                if sort_by_choice == 5:
                    continue

                sort_type_choices = ["Ascending", "Descending", "Back"]
                sort_type_choice = prompt_menu("Sort Type", sort_type_choices)
                if sort_type_choice == 3:
                    continue
                cls()
                query = "SELECT model_number, name, price, quantity, discount, price - discount/100 * price FROM products ORDER BY {} {}".format(
                    ["Name", "Price", "Quantity", "Discount"][sort_by_choice - 1].lower(),
                    ["ASC", "DESC"][sort_type_choice - 1].lower(),
                )
                cursor.execute(query)
                data = cursor.fetchall()
                if not data:
                    print("No products found!")
                else:
                    show_table(["Model Number", "Name", "Price", "Quantity", "Discount", "Final Price"], data)
                input("\nPress Enter to continue...")
            # Back
            elif view_choice == 3:
                pass

        # Add Product
        elif choice == 2:
            input_data = prompt_input(
                {"Model Number": str, "Name": str, "Price": float, "Quantity": int},
                {"Discount (leave blank for 0)": int},
            )
            discount = input_data["Discount (leave blank for 0)"]
            price = float(input_data["Price"])

            if discount < 0 or discount > 100:
                print("Discount must be between 0 and 100!")
                input("Press Enter to continue...")
                continue
            elif price < 0:
                print("Price must be greater than 0!")
                input("Press Enter to continue...")
                continue
            try:
                cursor.execute(
                    "INSERT INTO products (model_number, name, price, quantity, discount) VALUES (%s, %s, %s, %s, %s)",
                    (input_data["Model Number"], input_data["Name"], price, float(input_data["Quantity"]), discount),
                )
            except errors.DataError:
                print("Invalid input! Did you enter very long values? Please try again")
                input("Press Enter to continue...")
                continue
            db.commit()
            print("\nProduct added!")
            input("Press Enter to continue...")

        # Update Product
        elif choice == 3:
            data = search_product(return_value=True)
            if not data:
                print("No product found with that identifier!")
                input("Press Enter to continue...")
                choice = -1
                continue

            show_table(["Model Number", "Name", "Price", "Quantity", "Discount", "Final Price"], [data]),
            print()
            print("Edit row data. [] Indicate current value. Leave blank to keep current value.")
            input_data = prompt_input(
                {},
                {   f"Model Number [{data[0]}]": str,
                    f"Name [{data[1]}]": str,
                    f"Price [{data[2]}]": float,
                    f"Quantity [{data[3]}]": int,
                    f"Discount [{data[4]}]": int},
            )

            model_number = input_data[f"Model Number [{data[0]}]"] or data[0]
            name = input_data[f"Name [{data[1]}]"] or data[1]
            price = float(input_data[f"Price [{data[2]}]"]) or data[2]
            quantity = float(input_data[f"Quantity [{data[3]}]"]) or data[3]
            discount = float(input_data[f"Discount [{data[4]}]"]) or data[4] if float(input_data[f"Discount [{data[4]}]"]) != 0 else 0

            if discount < 0 or discount > 100:
                print("Discount must be between 0 and 100!")
                input("Press Enter to continue...")
                choice = -1
                continue
            elif price < 0:
                print("Price must be greater than 0!")
                input("Press Enter to continue...")
                choice = -1
                continue

            try:
                cursor.execute(
                    "UPDATE products SET model_number = %s, name = %s, price = %s, quantity = %s, discount = %s WHERE model_number = %s",
                    (model_number, name, price, quantity, discount, data[0]),
                )
            except errors.DataError:
                print("Invalid input! Did you enter very long values? Please try again")
                input("Press Enter to continue...")
                continue
            except errors.IntegrityError:
                print("Model number already exists!")
                input("Press Enter to continue...")
                choice = -1
                continue
            db.commit()
            print("\nProduct updated!")
            input("Press Enter to continue...")

        # Delete Product
        elif choice == 4:
            data = search_product(return_value=True)
            if not data:
                print("No product found with that identifier!")
                input("Press Enter to continue...")
                continue

            show_table(["Model Number", "Name", "Price", "Quantity", "Discount", "Final Price"], [data])
            print("\n\n")
            if input("Are you sure you want to delete this product? (Y/N): ").lower() == "y":
                cursor.execute("DELETE FROM products WHERE model_number = %s", (data[0],))
                db.commit()
                print("\nProduct deleted!")
                input("Press Enter to continue...")
            else:
                print("Product not deleted!")
                input("Press Enter to continue...")

        # Go back
        elif choice == 5:
            CURRENT_PAGE = -1
            return

        else:
            print("Invalid input! Try again")
            input("Press Enter to continue...")

        choice = -1


def staff_management_menu():
    global CURRENT_PAGE, db
    choice = -1
    while True:
        choices = ["View Staff", "Hire Staff", "Fire Staff", "Go Back"]
        if choice == -1:
            choice = prompt_menu("Staff Management", choices)
        cls()
        # View Staff
        if choice == 1:
            view_choices = ["View All", "Sort", "Back"]
            view_choice = prompt_menu("View Staff", view_choices)
            cls()
            # View All
            if view_choice == 1:
                cursor.execute("SELECT name, floor(DATEDIFF(CURRENT_DATE, dob)/365) AS 'Age', doj, base_pay, level FROM staff;")
                employees = cursor.fetchall()
                if not employees:
                    print("No employees hired yet!")
                else:
                    # TODO decide what 'level' is
                    show_table(["S. No", "Name", "Age", "Date of Joining", "Base Salary", '"Level"'], [(i+1,*emp) for i, emp in enumerate(employees)])
                input("\nPress Enter to Continue")
            # Sort
            elif view_choice == 2:
                sort_by_choices = ["Sort by Name", "Sort by Age", "Sort by Date of Joining", "Sort by Base Salary", "Back"]
                sort_by_choice = prompt_menu("Sort Products", sort_by_choices)

                if sort_by_choice == 5:
                    continue

                sort_type_choices = ["Ascending", "Descending", "Back"]
                sort_type_choice = prompt_menu("Sort Type", sort_type_choices)
                if sort_type_choice == 3:
                    continue
                cls()
                query = "SELECT name, floor(DATEDIFF(CURRENT_DATE, dob)/365) AS 'Age', doj, base_pay, level FROM staff ORDER BY {} {}".format(
                    ["Name", "Age", "doj", "base_pay"][sort_by_choice - 1].lower(),
                    ["ASC", "DESC"][sort_type_choice - 1].lower(),
                )
                cursor.execute(query)
                employees = cursor.fetchall()
                if not employees:
                    print("No employees hired yet!")
                else:
                    show_table(["S. No", "Name", "Age", "Date of Joining", "Base Salary", '"Level"'], [(i+1,*emp) for i, emp in enumerate(employees)])
                input("\nPress Enter to continue...")
            # Back
            elif view_choice == 3:
                pass
        # Hire Staff
        elif choice == 2:
            employees = [
                (str(i+1),f"{randchoice(first_names)} {randchoice(last_names)}", f"{randint(1, 31)}/{randint(1, 12)}/{randint(1980, 2000)}", f"{randint(1,5)} Years", f"₹{randint(3,8) * 1000}") 
                for i in range(5)
            ]
            show_table(["S. No", "Name", "Date of Birth", "Past Experience", "Expected Base Pay"], employees)
            print("\n\nChoose an employee to hire by entering the S. No. of the employee. Enter 0 to go back.")
            user_choice = prompt_input_int("\n> ", 0, 5)
                
            if user_choice == 0:
                choice = -1
                continue
            
            while True:
                print("Setup employee login details.")
                input_data = prompt_input(
                    {
                        "Username": str,
                        "Password": str,
                        "Confirm Password": str,
                    },{}
                )
                if input_data["Password"] != input_data["Confirm Password"]:
                    print("Passwords do not match!")
                    input("Press Enter to continue...")
                    continue
                break
            selected_employee = employees[user_choice-1]
            cursor.execute("INSERT INTO staff (name, dob, base_pay) VALUES (%s, %s, %s)",
                (selected_employee[1],  datetime.strptime(selected_employee[2], "%d/%m/%Y").date(), float(selected_employee[4][1:]),)
            )
            
            try:
                cursor.execute("INSERT INTO logins (username, password, role, employee_id) VALUES (%s, %s, %s, %s)", 
                (input_data["Username"], input_data["Password"], "employee", cursor.lastrowid)
                )
            except errors.IntegrityError:
                print("Username already exists!")
                input("Press Enter to continue...")
                continue

            db.commit()
            print("\nEmployee hired!")
            input("Press Enter to continue...")
        # Fire Staff
        elif choice == 3:
            name = (input("Enter the name of the employee you want to fire: ")).lower()
            cursor.execute(
                "SELECT id, name, floor(DATEDIFF(CURRENT_DATE, dob)/365) AS 'Age', doj, base_pay, level FROM staff WHERE lower(name) LIKE %s;",
                (f"%{name}%",)
            )
            data = cursor.fetchall()
            if not data:
                print("No employee found with that name!")
                input("Press Enter to continue...")
                continue
            
            show_table(["S. No", "Name", "Age", "Date of Joining", "Base Salary", '"Level"'], [(i+1,) + emp[1:] for i, emp in enumerate(data)])
            print(f"\n\nSelect the employee you want to fire by entering the S. No. of the employee. Enter 0 to go back.")
            user_choice = prompt_input_int("\n> ", 0, len(data))
            if user_choice == 0:
                choice = -1
                continue
            selected_employee = data[user_choice-1]
            print("\n\n")
            show_table(["Name", "Age", "Date of Joining", "Base Salary", '"Level"'], [selected_employee[1:]])
            if input("\n\nAre you sure you want to fire this employee? (Y/N): ").lower() == "y":
                cursor.execute("DELETE FROM logins WHERE employee_id=%s", (selected_employee[0],))
                cursor.execute("DELETE FROM staff WHERE id=%s", (selected_employee[0],))
                db.commit()
                print("\nEmployee fired!")
                input("Press Enter to continue...")
            else:
                print("Employee not fired!")
                input("Press Enter to continue...")
        # Go Back
        elif choice == 4:
            CURRENT_PAGE = -1
            return
        
        choice = -1


def sales_report_menu():
    
    global CURRENT_PAGE
    choice = -1
    while True:
        choices = ["View All Sales", "Sort Sales", "Filter Sales", "Back"]
        if choice == -1:
            choice = prompt_menu("Sales Report Menu", choices)
        cls()
        # View All Sales
        if choice == 1:
            cursor.execute("SELECT S.invoice_number, E.name AS 'Employee name', C.name AS 'Customer Name', C.phone, S.sale_date, S.payment_method, SUM(S.quantity* (S.base_price - ((S.discount/100) * S.base_price))) AS 'Total Amount' FROM sales S, staff E, customers C WHERE S.employee_id = E.id AND S.customer_id = C.id GROUP BY invoice_number ORDER BY invoice_number DESC;")
            data = cursor.fetchall()
            view_multiple_sales(data)
            return
        # Sort Sales
        elif choice == 2:
            sort_by_choices = ["Sort by Date of Sale", "Sort by Total Amount", "Back"]
            sort_by_choice = prompt_menu("Sort Sales", sort_by_choices)
            
            if sort_by_choice == 3:
                return
                
            sort_type_choices = ["Ascending", "Descending", "Back"]
            sort_type_choice = prompt_menu("Sort Type", sort_type_choices)

            if sort_type_choice == 3:
                continue
            
            cls()
            query = "SELECT S.invoice_number, E.name AS 'Employee name', C.name AS 'Customer Name', C.phone, S.sale_date, S.payment_method, SUM(S.quantity* (S.base_price - ((S.discount/100) * S.base_price))) AS 'Total Amount' FROM sales S, staff E, customers C WHERE S.employee_id = E.id AND S.customer_id = C.id GROUP BY invoice_number ORDER BY {} {};".format(
                ["sale_date", "Total Amount"][sort_by_choice - 1],
                ["ASC", "DESC"][sort_type_choice - 1],
            )
            cursor.execute(query)
            data = cursor.fetchall()

            view_multiple_sales(data)
            return
        # Filter Sales
        elif choice == 3:
            filter_by_choices = ["Filter by Employee Name", "Filter by Customer Name", "Filter by Product Name", "Filter by Payment Method", "Back"]
            filter_by_choice = prompt_menu("Filter Sales", filter_by_choices)
            
            cls()
            if filter_by_choice == 1:
                employee_name = input("Enter the employee name: ").lower()
                cursor.execute("SELECT id, name, floor(DATEDIFF(CURRENT_DATE, dob)/365) AS 'Age' FROM staff WHERE lower(name) LIKE %s", (f"%{employee_name}%",))
                employees = cursor.fetchall()
                # No employee found
                if not employees:
                    print("No employee found with that name!")
                    input("Press Enter to continue...")
                    continue
                # Exactly 1 employee found
                elif len(employees) == 1:
                    employee = employees[0]
                # Multiple employees found
                else:
                    show_table(["S. No", "ID", "Name", "Age"], [(i+1, employee[0], employee[1], f"{employee[2]} Years") for i, employee in enumerate(employees)])
                    print("\n\n")
                    employee_id = prompt_input_int("S. No: ", 1, len(employees))
                    employee = employees[employee_id - 1]
                
                cursor.execute("SELECT S.invoice_number, E.name AS 'Employee name', C.name AS 'Customer Name', C.phone, S.sale_date, S.payment_method, SUM(S.quantity* (S.base_price - ((S.discount/100) * S.base_price))) AS 'Total Amount' FROM sales S, staff E, customers C WHERE S.employee_id = E.id AND S.customer_id = C.id AND S.employee_id = %s GROUP BY invoice_number ORDER BY sale_date DESC;", (employee[0],))
                data = cursor.fetchall()
                view_multiple_sales(data)
                return
            elif filter_by_choice == 2:
                customer_identifier = input("Enter the customer name or phone :  ").lower()
                cursor.execute("SELECT id, name, phone FROM customers WHERE lower(name) LIKE %s OR phone LIKE %s", (f"%{customer_identifier}%", f"%{customer_identifier}%"))
                customers = cursor.fetchall()
                # No customer found
                if not customers:
                    print("No customer found with that name!")
                    input("Press Enter to continue...")
                    continue
                # Exactly one customer found
                elif len(customers) == 1:
                    customer = customers[0]
                # Multiple customers found
                else:
                    show_table(["S. No", "ID", "Name", "Phone"], [(i+1, customer[0], customer[1], customer[2]) for i, customer in enumerate(customers)])
                    print("\n\n")
                    customer_id = prompt_input_int("S. No: ", 1, len(customers))
                    customer = customers[customer_id - 1]
                
                cursor.execute("SELECT S.invoice_number, E.name AS 'Employee name', C.name AS 'Customer Name', C.phone, S.sale_date, S.payment_method, SUM(S.quantity* (S.base_price - ((S.discount/100) * S.base_price))) AS 'Total Amount' FROM sales S, staff E, customers C WHERE S.employee_id = E.id AND S.customer_id = C.id AND S.customer_id = %s GROUP BY invoice_number ORDER BY sale_date DESC;", (customer[0],))
                data = cursor.fetchall()
                view_multiple_sales(data)
                return
            elif filter_by_choice == 3:
                product_identifier = input("Enter the product name or model number: ").lower()
                cursor.execute("SELECT name, model_number, price, quantity FROM products WHERE lower(name) LIKE %s OR lower(model_number) LIKE %s", (f"%{product_identifier}%", f"%{product_identifier}%"))
                products = cursor.fetchall()
                # No product found
                if not products:
                    print("No product found with that identifier!")
                    input("Press Enter to continue...")
                    continue
                # Exactly one product found
                elif len(products) == 1:
                    product = products[0]
                # Multiple products found
                else: 
                    show_table(["S. No", "Name", "Model Number", "Price", "Quantity"], [(i+1, product[0], product[1], product[2], product[3]) for i, product in enumerate(products)])
                    print("\n\n")
                    product_id = prompt_input_int("S. No: ", 1, len(products))
                    product = products[product_id - 1]

                cursor.execute("SELECT S.invoice_number, E.name AS 'Employee name', C.name AS 'Customer Name', C.phone, S.sale_date, S.payment_method, SUM(S.quantity* (S.base_price - ((S.discount/100) * S.base_price))) AS 'Total Amount' FROM sales S, staff E, customers C, products P WHERE S.employee_id = E.id AND S.customer_id = C.id AND S.product_model_number = P.model_number AND S.product_model_number = %s GROUP BY invoice_number ORDER BY sale_date DESC;", (product[1],))
                data = cursor.fetchall()
                view_multiple_sales(data)
                return
            elif filter_by_choice == 4:
                payment_method = input("Enter the payment method: ").lower()
                cursor.execute("SELECT S.invoice_number, E.name AS 'Employee name', C.name AS 'Customer Name', C.phone, S.sale_date, S.payment_method, SUM(S.quantity* (S.base_price - ((S.discount/100) * S.base_price))) AS 'Total Amount' FROM sales S, staff E, customers C WHERE S.employee_id = E.id AND S.customer_id = C.id AND S.payment_method LIKE %s GROUP BY invoice_number ORDER BY sale_date DESC;", (f"%{payment_method}%",))
                data = cursor.fetchall()
                view_multiple_sales(data)
                return
            elif filter_by_choice == 5:
                return
        # Go back
        elif choice == 4:
            CURRENT_PAGE = -1
            return


def new_sale():
    global CURRENT_PAGE
    # Model Number : Product Info
    products: Dict[str, dict] = {}
    while True:
        cls()
        product = search_product(return_value=True)
        if not product:
            print("Product not found!")
            input("Press Enter to continue...")
            continue
        show_table(["Model Number", "Name", "Price", "Quantity", "Discount", "Final Price"], [product])
        print("\n")
        # Quantity check
        if product[3] == 0:
            print("Product is out of stock!")
            input("Press Enter to continue...")
            continue

        elif product[3] == 1:
            quantity = 1
        else:
            quantity = prompt_input_int("Enter the quantity: ", 1, product[3])
        model_number: str = product[0]
        products[model_number] = {"Model Number": model_number, "Name": product[1], "Price": product[2], "Quantity": quantity, "Discount": product[4], "Final Price": product[5] * quantity}
        
        if input("\n\nDo you want to add more products? (Y/N): ").lower() == "n":
            break
    cls()
    while True:
        customer_number = input("Enter the phone number of the customer: ")
        if customer_number.isnumeric() and len(customer_number) == 10:
            break
        print("Invalid phone number!")
        input("Press Enter to try again...")

    cursor.execute("SELECT id, name, address, phone, email FROM customers WHERE phone=%s", (customer_number,))
    existing_customer = cursor.fetchone()
    if not existing_customer:
        data = prompt_input({"Name":str, "Address": str, "Email": str}, {})
        cursor.execute("INSERT INTO customers(name, address, phone, email) VALUES (%s, %s, %s, %s);", (data["Name"], data["Address"], customer_number, data["Email"]))
        db.commit()
        customer = (cursor.lastrowid, data["Name"], data["Address"], customer_number, data["Email"])
        print("Customer added!")
    else:
        customer = existing_customer
        print("Customer found!")
    
    payment_method = input("Enter the payment method: ")

    show_table(["Model Number", "Name", "Price", "Quantity", "Discount", "Final Price"],
    [(model_number, product["Name"], product["Price"], product["Quantity"], product["Discount"], product["Final Price"]) for model_number, product in products.items()])
    print("\n\n")

    show_table(["Name", "Address", "Phone", "Email"], [customer[1:]], to_cls=False)
    print("\n\n")

    print(f"Payment Method: {payment_method}")
    print(f"Total Amount: {sum([product['Final Price'] for product in products.values()])}")
    if input("\n\nAre you sure you want to proceed? (Y/N): ").lower() != "y":
        print("Sale cancelled!")
        input("Press Enter to continue...")
        return
    
    cursor.execute("SELECT MAX(invoice_number) FROM sales;")
    last_invoice_number = cursor.fetchone()[0] or 0
    for model_number, product in products.items():
        cursor.execute("INSERT INTO sales(invoice_number, employee_id, customer_id, product_model_number, quantity, base_price, discount, payment_method) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", 
        (last_invoice_number+1, LOGGED_IN_ID, customer[0], model_number, product["Quantity"], product["Price"], product["Discount"], payment_method))
        cursor.execute("UPDATE products SET quantity=quantity-%s WHERE model_number=%s", (product["Quantity"], model_number))
    db.commit()
    print("Sale completed!")
    input("Press Enter to continue...")
    CURRENT_PAGE = -1


def main():
    global LOGGED_IN, LOGGED_IN_AS, LOGGED_IN_ID, CURRENT_PAGE
    while True:
        try:
            cls()
            print("Welcome to BananaCenter".center(100), "\n\n")

            if not LOGGED_IN:
                login_details = login()
                LOGGED_IN = login_details[0]
                if login_details[0]:
                    LOGGED_IN_AS = login_details[1]
                    LOGGED_IN_ID = login_details[2]
                    print(f"Logged in as: {LOGGED_IN_AS}")
                    print()
                    input("Press Enter to continue...")
                continue

            if LOGGED_IN_AS == "admin":
                if CURRENT_PAGE == -1:
                    # TODO Staff Management: Change login info
                    choices = ["Inventory Management", "Staff Management", "Sales Report", "Logout", "Exit"]
                    choice = prompt_menu("Administrator Main Menu", choices)
                    CURRENT_PAGE = choice
                else:
                    choice = CURRENT_PAGE
                if choice == 1:
                    inventory_management_menu()
                elif choice == 2:
                    staff_management_menu()
                elif choice == 3:
                    sales_report_menu()
                elif choice == 4:
                    LOGGED_IN = False
                    CURRENT_PAGE = -1
                elif choice == 5:
                    break

            elif LOGGED_IN_AS == "employee":
                if CURRENT_PAGE == -1:
                    choices = ["Search Prouct", "New Sale", "View Sales", "Logout", "Exit"]
                    choice = prompt_menu("Employee Main Menu", choices)
                    CURRENT_PAGE = choice
                else:
                    choice = CURRENT_PAGE
                cls()
                try:
                    if choice == 1:
                        search_product()
                    elif choice == 2:
                        new_sale()
                    elif choice == 3:
                        cursor.execute("SELECT DISTINCT invoice_number FROM sales WHERE employee_id=%s", (LOGGED_IN_ID,))
                        sales_by_emp = cursor.fetchall()
                        if not sales_by_emp:
                            print("You have made no sales yet. Get back to work.")
                            input("Press Enter to continue...")
                            CURRENT_PAGE = -1
                            continue
                        print(f"You have made {len(sales_by_emp)} sales.")
                        input("Press Enter to continue...")
                    elif choice == 4:
                        LOGGED_IN = False
                        CURRENT_PAGE = -1
                    elif choice == 5:
                        break
                except KeyboardInterrupt:
                    pass
                finally:
                    CURRENT_PAGE = -1

        except KeyboardInterrupt:
            if not LOGGED_IN:
                cls()
                break
            continue


with connect(host="localhost", user="root", password="1234") as db:
    with db.cursor() as cursor:
        cursor.execute("""
                        CREATE DATABASE IF NOT EXISTS BananaCenter;
                    """)
    db.database = "BananaCenter"
    cursor = db.cursor(buffered=True)
    setup(cursor)
    db.commit()
    main()

print("Have a nice day =)")

# TODO what if employee is fired after making sale
# TODO Same for product
# TODO Remove employee level