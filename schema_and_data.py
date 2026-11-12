import duckdb

def build_db():
    con = duckdb.connect(":memory:")
    con.execute("""
    CREATE TABLE departments (
        dept_id INTEGER, dept_name VARCHAR
    )""")
    con.execute("""
    CREATE TABLE employees (
        emp_id INTEGER, emp_name VARCHAR, dept_id INTEGER,
        salary INTEGER, hire_date DATE, manager_id INTEGER
    )""")
    con.execute("""
    CREATE TABLE orders (
        order_id INTEGER, emp_id INTEGER, customer VARCHAR,
        amount DECIMAL(10,2), order_date DATE
    )""")
    con.executemany("INSERT INTO departments VALUES (?, ?)", [
        (1, "Sales"), (2, "Engineering"), (3, "Marketing"), (4, "HR"),
    ])
    con.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?)", [
        (1, "Alice Chen", 2, 145000, "2019-03-04", None),
        (2, "Bob Smith", 2, 132000, "2020-07-13", 1),
        (3, "Carol Diaz", 1, 98000, "2021-01-25", 4),
        (4, "David Kim", 1, 121000, "2018-11-02", None),
        (5, "Emma Wilson", 3, 89000, "2022-05-16", 6),
        (6, "Frank Lee", 3, 104000, "2019-09-30", None),
        (7, "Grace Ho", 2, 132000, "2021-08-23", 1),
        (8, "Henry Ford", 4, 76000, "2023-02-06", 9),
        (9, "Irene Adler", 4, 99000, "2020-04-14", None),
        (10, "Jack Ma", 1, 88000, "2022-10-31", 4),
        (11, "Karen Page", 2, 118000, "2023-06-19", 1),
        (12, "Leo Park", 3, 91000, "2024-01-08", 6),
    ])
    con.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", [
        (101, 3, "Acme Corp", 12500.00, "2024-02-11"),
        (102, 4, "Globex", 30200.50, "2024-03-05"),
        (103, 3, "Initech", 9800.00, "2024-05-21"),
        (104, 10, "Acme Corp", 15400.75, "2024-06-14"),
        (105, 4, "Umbrella", 22100.00, "2024-07-02"),
        (106, 10, "Globex", 7300.25, "2024-08-19"),
        (107, 3, "Hooli", 41000.00, "2024-09-23"),
        (108, 4, "Initech", 18900.00, "2024-10-07"),
        (109, 10, "Umbrella", 5600.00, "2024-11-15"),
        (110, 3, "Globex", 26750.00, "2025-01-09"),
        (111, 4, "Hooli", 33400.00, "2025-02-17"),
        (112, 10, "Acme Corp", 9100.50, "2025-03-28"),
        (113, 3, "Umbrella", 14800.00, "2025-04-11"),
        (114, 4, "Globex", 19999.99, "2025-05-06"),
        (115, 10, "Initech", 11250.00, "2025-06-20"),
    ])
    return con


if __name__ == "__main__":
    con = build_db()
    print(con.execute("SELECT COUNT(*) FROM employees").fetchall())
    print(con.execute("SELECT COUNT(*) FROM orders").fetchall())