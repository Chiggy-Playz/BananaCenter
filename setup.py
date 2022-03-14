from mysql.connector.errors import IntegrityError

logins_table = """
CREATE TABLE IF NOT EXISTS logins (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(30),
    role VARCHAR(50)
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

def setup(cur):

    cur.execute(logins_table)
    cur.execute(inventory_table)

    try:
        cur.execute("""INSERT INTO logins (username, password, role) VALUES ('admin', 'admin', 'admin');""")
    except IntegrityError:
        pass  # admin row exists


