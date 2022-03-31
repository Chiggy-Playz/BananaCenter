from mysql.connector.errors import IntegrityError

logins_table = """
CREATE TABLE IF NOT EXISTS logins (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(30),
    role VARCHAR(50),
    employee_id INT NULL
);
"""

inventory_table = """
CREATE TABLE IF NOT EXISTS products (
    model_number VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL,
    discount DECIMAL(10,2) NOT NULL DEFAULT 0
);
"""

staff_table = """
CREATE TABLE IF NOT EXISTS staff (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    dob DATE NOT NULL,
    base_pay DECIMAL(10,2) NOT NULL,
    level INT NOT NULL DEFAULT 0,
    doj DATE NOT NULL DEFAULT (CURRENT_DATE)
);
"""

customers_table = """
CREATE TABLE IF NOT EXISTS customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    address VARCHAR(100),
    phone CHAR(10) UNIQUE,
    email VARCHAR(50)
);
"""

sales_table = """
CREATE TABLE IF NOT EXISTS sales (
    id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_number INT NOT NULL,
    employee_id INT,
    customer_id INT,
    product_model_number VARCHAR(50),
    sale_date Date NOT NULL DEFAULT (CURRENT_DATE),
    quantity INT NOT NULL,
    payment_method VARCHAR(20),
    base_price DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) NOT NULL DEFAULT 0
);
"""


def setup(cur):
    cur.execute(logins_table)
    cur.execute(inventory_table)
    cur.execute(staff_table)
    cur.execute(customers_table)
    cur.execute(sales_table)
    cur.execute("ALTER TABLE logins ADD FOREIGN KEY (employee_id) REFERENCES staff(id);")
    cur.execute("ALTER TABLE sales ADD FOREIGN KEY (employee_id) REFERENCES staff(id);")
    cur.execute("ALTER TABLE sales ADD FOREIGN KEY (customer_id) REFERENCES customers(id);")
    cur.execute("ALTER TABLE sales ADD FOREIGN KEY (product_model_number) REFERENCES products(model_number);")
    try:
        cur.execute("""INSERT INTO logins (username, password, role, employee_id) VALUES ('admin', 'admin', 'admin', NULL);""")
    except IntegrityError:
        pass  # admin row already exists


