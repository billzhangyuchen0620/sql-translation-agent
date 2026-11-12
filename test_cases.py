TEST_CASES = [
    {
        "id": 1,
        "pitfall": "TOP -> LIMIT",
        "tsql": "SELECT TOP 3 emp_name, salary FROM employees ORDER BY salary DESC",
        "reference": "SELECT emp_name, salary FROM employees ORDER BY salary DESC LIMIT 3",
    },
    {
        "id": 2,
        "pitfall": "GETDATE() -> CURRENT_DATE",
        "tsql": "SELECT CAST(GETDATE() AS DATE) AS today",
        "reference": "SELECT CURRENT_DATE AS today",
    },
    {
        "id": 3,
        "pitfall": "ISNULL -> COALESCE",
        "tsql": (
            "SELECT emp_name, ISNULL(CAST(manager_id AS VARCHAR), 'No Manager') AS manager "
            "FROM employees ORDER BY emp_id"
        ),
        "reference": (
            "SELECT emp_name, COALESCE(CAST(manager_id AS VARCHAR), 'No Manager') AS manager "
            "FROM employees ORDER BY emp_id"
        ),
    },
    {
        "id": 4,
        "pitfall": "Bracket identifiers -> double quotes",
        "tsql": "SELECT [emp_name], [salary] FROM [employees] WHERE [salary] > 100000 ORDER BY [salary]",
        "reference": 'SELECT "emp_name", "salary" FROM "employees" WHERE "salary" > 100000 ORDER BY "salary"',
    },
    {
        "id": 5,
        "pitfall": "String concatenation + -> ||",
        "tsql": (
            "SELECT e.emp_name + ' (' + d.dept_name + ')' AS label "
            "FROM employees e JOIN departments d ON e.dept_id = d.dept_id ORDER BY e.emp_id"
        ),
        "reference": (
            "SELECT e.emp_name || ' (' || d.dept_name || ')' AS label "
            "FROM employees e JOIN departments d ON e.dept_id = d.dept_id ORDER BY e.emp_id"
        ),
    },
    {
        "id": 6,
        "pitfall": "LEN -> LENGTH",
        "tsql": "SELECT emp_name, LEN(emp_name) AS name_len FROM employees ORDER BY emp_id",
        "reference": "SELECT emp_name, LENGTH(emp_name) AS name_len FROM employees ORDER BY emp_id",
    },
    {
        "id": 7,
        "pitfall": "YEAR() grouping (compatible function, dialect-safe)",
        "tsql": (
            "SELECT YEAR(order_date) AS y, SUM(amount) AS total FROM orders "
            "GROUP BY YEAR(order_date) ORDER BY y"
        ),
        "reference": (
            "SELECT YEAR(order_date) AS y, SUM(amount) AS total FROM orders "
            "GROUP BY YEAR(order_date) ORDER BY y"
        ),
    },
    {
        "id": 8,
        "pitfall": "Control case: already compatible, must pass unchanged",
        "tsql": "SELECT dept_id, AVG(salary) AS avg_salary FROM employees GROUP BY dept_id ORDER BY dept_id",
        "reference": "SELECT dept_id, AVG(salary) AS avg_salary FROM employees GROUP BY dept_id ORDER BY dept_id",
    },
    {
        "id": 9,
        "pitfall": "TOP + ISNULL combined",
        "tsql": (
            "SELECT TOP 5 emp_name, ISNULL(CAST(manager_id AS VARCHAR), 'None') AS mgr "
            "FROM employees ORDER BY hire_date"
        ),
        "reference": (
            "SELECT emp_name, COALESCE(CAST(manager_id AS VARCHAR), 'None') AS mgr "
            "FROM employees ORDER BY hire_date LIMIT 5"
        ),
    },
    {
        "id": 10,
        "pitfall": "GETDATE() in WHERE clause",
        "tsql": "SELECT COUNT(*) AS senior_count FROM employees WHERE hire_date <= GETDATE()",
        "reference": "SELECT COUNT(*) AS senior_count FROM employees WHERE hire_date <= CURRENT_DATE",
    },
    {
        "id": 11,
        "pitfall": "DATEADD -> date + INTERVAL (result must stay DATE)",
        "tsql": "SELECT emp_name, DATEADD(day, 90, hire_date) AS probation_end FROM employees ORDER BY emp_id",
        "reference": "SELECT emp_name, CAST(hire_date + INTERVAL 90 DAY AS DATE) AS probation_end FROM employees ORDER BY emp_id",
    },
    {
        "id": 12,
        "pitfall": "DATEDIFF argument style + GETDATE()",
        "tsql": (
            "SELECT emp_name, DATEDIFF(year, hire_date, GETDATE()) AS years_of_service "
            "FROM employees WHERE DATEDIFF(year, hire_date, GETDATE()) >= 5 ORDER BY emp_name"
        ),
        "reference": (
            "SELECT emp_name, DATEDIFF('year', hire_date, CURRENT_DATE) AS years_of_service "
            "FROM employees WHERE DATEDIFF('year', hire_date, CURRENT_DATE) >= 5 ORDER BY emp_name"
        ),
    },
    {
        "id": 13,
        "pitfall": "DATEPART argument style",
        "tsql": (
            "SELECT DATEPART(month, order_date) AS order_month, COUNT(*) AS order_count "
            "FROM orders GROUP BY DATEPART(month, order_date) ORDER BY order_month"
        ),
        "reference": (
            "SELECT DATEPART('month', order_date) AS order_month, COUNT(*) AS order_count "
            "FROM orders GROUP BY DATEPART('month', order_date) ORDER BY order_month"
        ),
    },
    {
        "id": 14,
        "pitfall": "CHARINDEX -> INSTR",
        "tsql": "SELECT emp_name, CHARINDEX('o', emp_name) AS first_o_pos FROM employees ORDER BY emp_id",
        "reference": "SELECT emp_name, INSTR(emp_name, 'o') AS first_o_pos FROM employees ORDER BY emp_id",
    },
    {
        "id": 15,
        "pitfall": "EOMONTH -> LAST_DAY",
        "tsql": (
            "SELECT EOMONTH(order_date) AS month_end, SUM(amount) AS total "
            "FROM orders GROUP BY EOMONTH(order_date) ORDER BY month_end"
        ),
        "reference": (
            "SELECT LAST_DAY(order_date) AS month_end, SUM(amount) AS total "
            "FROM orders GROUP BY LAST_DAY(order_date) ORDER BY month_end"
        ),
    },
    {
        "id": 16,
        "pitfall": "Composite report query: TOP + string concat + ISNULL + LEN in one query",
        "tsql": (
            "SELECT TOP 5 e.emp_name + ' (' + d.dept_name + ')' AS label, "
            "ISNULL(CAST(e.manager_id AS VARCHAR), 'None') AS mgr, LEN(e.emp_name) AS name_len "
            "FROM employees e JOIN departments d ON e.dept_id = d.dept_id ORDER BY e.hire_date"
        ),
        "reference": (
            "SELECT e.emp_name || ' (' || d.dept_name || ')' AS label, "
            "COALESCE(CAST(e.manager_id AS VARCHAR), 'None') AS mgr, LENGTH(e.emp_name) AS name_len "
            "FROM employees e JOIN departments d ON e.dept_id = d.dept_id ORDER BY e.hire_date LIMIT 5"
        ),
    },
]