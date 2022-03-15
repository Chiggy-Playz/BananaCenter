try:
    from mysql.connector import connect, errors
    from setup import setup
except ModuleNotFoundError:
    print("Dependency not found. Please run 'pip install -r requirements.txt' to install all dependencies.")
    quit()

import os
from typing import List, Tuple, Dict, Any


def cls():
    # Inter platform clear screen
    os.system("cls" if os.name == "nt" else "clear")

# TODO: Replace ip with localhost
db = connect(host="38.242.201.218", user="root", password="1234", database="BananaCenter")

cursor = db.cursor(buffered=True)
setup(cursor)
db.commit()

LOGGED_IN = False
LOGGED_IN_AS = ""
CURRENT_PAGE = -1


def login() -> Tuple[bool, str]:
    username = input("Login Username: ")
    password = input("Login Password: ")
    cursor.execute("SELECT role FROM logins WHERE username = %s AND password = %s", (username, password))
    if cursor.rowcount == 1:
        print("Login Successful!")

        return (True, cursor.fetchone()[0])
    else:
        print("Login Failed!")
        input("Press Enter to retry...")
        return (False, "")


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
        except ValueError:
            print("Invalid choice! Try again")
            input("Press Enter to continue...")

            continue
        else:
            if user_choice < 1 or user_choice > len(choices):
                print("Invalid choice! Try again")
                input("Press Enter to continue...")
                continue
            else:
                return user_choice


def show_table(columns: List[str], rows: List[Tuple]) -> None:
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
                    "SELECT model_number, name, format(price,2,'N2'), quantity, discount, format(price - discount/100 * price,2, 'N2') FROM products"
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
                query = "SELECT model_number, name, format(price,2,'N2'), quantity, discount, format(price - discount/100 * price, 2, 'N2') FROM products ORDER BY {} {}".format(
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
            identifier = input("Enter the model number or name of the product you want to update: ")
            cursor.execute(
                "SELECT model_number, name, price, quantity, discount FROM products WHERE lower(model_number) LIKE %s OR lower(name) LIKE %s",
                (f"%{identifier}%", f"%{identifier}%"),
            )
            data = cursor.fetchone()
            if not data:
                print("No product found with that identifier!")
                input("Press Enter to continue...")
                choice = -1
                continue

            show_table(["Model Number", "Name", "Price", "Quantity", "Discount"], [data]),
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
            db.commit()
            print("\nProduct updated!")
            input("Press Enter to continue...")

        # Delete Product
        elif choice == 4:
            identifier = input("Enter the model number or name of the product you want to delete: ")
            cursor.execute(
                "SELECT model_number, name, price, quantity, discount FROM products WHERE lower(model_number) LIKE %s OR lower(name) LIKE %s",
                (f"%{identifier}%", f"%{identifier}%"),
            )
            data = cursor.fetchone()
            if not data:
                print("No product found with that identifier!")
                input("Press Enter to continue...")
                continue

            show_table(["Model Number", "Name", "Price", "Quantity", "Discount"], [data])
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


while True:
    try:
        cls()
        print("Welcome to BananaCenter".center(100), "\n\n")

        if not LOGGED_IN:
            login_details = login()
            LOGGED_IN = login_details[0]
            if login_details[0]:
                LOGGED_IN_AS = login_details[1]
                print(f"Logged in as: {LOGGED_IN_AS}")
                print()
                input("Press Enter to continue...")
            continue

        if LOGGED_IN_AS == "admin":
            if CURRENT_PAGE == -1:
                choices = ["Inventory Management", "Staff Management", "Sales Report", "Logout", "Exit"]
                choice = prompt_menu("Administrator Main Menu", choices)
                CURRENT_PAGE = choice
            else:
                choice = CURRENT_PAGE
            if choice == 1:
                inventory_management_menu()
            if choice == 4:
                LOGGED_IN = False
                CURRENT_PAGE = -1
            if choice == 5:
                break
            else:
                CURRENT_PAGE = -1  # TODO PROPER error

    except KeyboardInterrupt:
        continue

print("Thank you for visiting BananaCenter. Have a nice day :)")
