import mysql.connector
import os

# ---------- MYSQL CONNECTION ----------
def get_connection(database=None):
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="*1+1J_Zero00",
        database=database
    )


# ---------- OPTION 1 : COPY STRUCTURE ----------
def copy_structure():
    db_name = input("Enter database name: ")

    conn = get_connection(db_name)
    cursor = conn.cursor()

    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    with open("create_statements.sql", "w", encoding="utf-8") as f:
        for table in tables:
            table_name = table[0]

            cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
            result = cursor.fetchone()

            create_statement = result[1]

            f.write(create_statement + ";\n\n")

    print("✅ Database structure copied to create_statements.sql")

    cursor.close()
    conn.close()


# ---------- OPTION 2 : COPY INSERTS ----------
def format_value(value):
    if value is None:
        return "NULL"
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"
    return str(value)


def copy_inserts():
    db_name = input("Enter database name: ")

    conn = get_connection(db_name)
    cursor = conn.cursor()

    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    with open("insert_statements.sql", "w", encoding="utf-8") as f:

        for table in tables:
            table_name = table[0]

            cursor.execute(f"SELECT * FROM `{table_name}`")
            rows = cursor.fetchall()

            if not rows:
                continue

            columns = [col[0] for col in cursor.description]
            column_list = ", ".join([f"`{c}`" for c in columns])

            for row in rows:
                values = ", ".join(format_value(v) for v in row)

                insert_sql = f"INSERT INTO `{table_name}` ({column_list}) VALUES ({values});"
                f.write(insert_sql + "\n")

            f.write("\n")

    print("✅ Insert statements copied to insert_statements.sql")

    cursor.close()
    conn.close()


# ---------- OPTION 3 : DEPLOY ----------
def execute_sql_file(cursor, filename):

    if not os.path.exists(filename):
        print(f"❌ {filename} not found")
        return

    with open(filename, "r", encoding="utf-8") as f:
        sql_commands = f.read().split(";")

    for command in sql_commands:
        command = command.strip()
        if command:
            try:
                cursor.execute(command)
            except Exception as e:
                print("Error executing:", command[:80])
                print(e)


def deploy():
    db_name = input("Enter database name to deploy into: ")

    conn = get_connection(db_name)
    cursor = conn.cursor()

    print("Running create_statements.sql...")
    execute_sql_file(cursor, "create_statements.sql")

    print("Running insert_statements.sql...")
    execute_sql_file(cursor, "insert_statements.sql")

    conn.commit()

    cursor.close()
    conn.close()

    print("✅ Deployment complete")


# ---------- MAIN MENU ----------
def main():

    while True:

        print("\nMYSQL BACKUP TOOL")
        print("1. Copy database structure")
        print("2. Copy database inserts")
        print("3. Deploy database")
        print("4. Exit")

        choice = input("Choose option: ")

        if choice == "1":
            copy_structure()

        elif choice == "2":
            copy_inserts()

        elif choice == "3":
            deploy()

        elif choice == "4":
            break

        else:
            print("Invalid option")


if __name__ == "__main__":
    main()