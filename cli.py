import requests
import jwt
from config import *

BASE_URL = "http://127.0.0.1:8000"


token = None
user_type = None


# -----------------------------
# HEALTH
# -----------------------------
def health():

    r = requests.get(f"{BASE_URL}/health")

    print("\nServer Response:")
    print(r.json())


# -----------------------------
# REGISTER
# -----------------------------
def register():

    print("\n------ REGISTER ------")

    name = input("Username: ")
    password = input("Password: ")
    type = input("Type (admin/user): ")

    data = {
        "name": name,
        "password": password,
        "type": type
    }

    r = requests.post(f"{BASE_URL}/register", json=data)

    print(r.json())


# -----------------------------
# LOGIN
# -----------------------------
def login():

    global token
    global user_type

    print("\n------ LOGIN ------")

    name = input("Username: ")
    password = input("Password: ")

    data = {
        "name": name,
        "password": password
    }

    r = requests.post(f"{BASE_URL}/login", json=data)

    res = r.json()

    if "access_token" not in res:
        print(res)
        return False

    token = res["access_token"]

    print(token)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    print(decoded)

    user_type = decoded["type"]

    print(f"\nLogged in as {user_type}")

    return True


# -----------------------------
# GET USERS
# -----------------------------
def get_users():

    headers = {
        "Authorization": f"Bearer {token}"
    }

    r = requests.get(f"{BASE_URL}/users", headers=headers)

    users = r.json()

    if isinstance(users, dict) and "detail" in users:
        print(users["detail"])
        return []

    print("\n------ USERS ------")

    for u in users:
        print(f"{u['id']} | {u['name']} | {u['type']} | roles={u['roles']}")

    return users


# -----------------------------
# GET ACTIONS
# -----------------------------
def get_actions():

    r = requests.get(f"{BASE_URL}/actions")

    actions = r.json()

    print("\n------ ACTIONS ------")

    for a in actions:
        print(f"{a['id']} | {a['name']} | {a['description']}")

    return actions


# -----------------------------
# ADMIN : EDIT USER ROLES
# -----------------------------
def edit_user_roles():

    users = get_users()

    uid = int(input("\nSelect user id: "))

    selected_user = None

    for u in users:
        if u["id"] == uid:
            selected_user = u
            break

    if not selected_user:
        print("Invalid user")
        return

    actions = get_actions()

    roles = input("\nEnter action ids (comma separated): ")

    role_list = [int(x.strip()) for x in roles.split(",")]

    updated_user = {
        "id": selected_user["id"],
        "name": selected_user["name"],
        "type": selected_user["type"],
        "roles": str(role_list)
    }

    r = requests.post(f"{BASE_URL}/update_user", json=updated_user)

    print(r.json())


# -----------------------------
# ADMIN MENU
# -----------------------------
def admin_menu():

    while True:

        print("\n------ ADMIN MENU ------")
        print("1. Edit User Roles")
        print("2. Health")
        print("3. Exit")

        choice = input("Select option: ")

        if choice == "1":
            edit_user_roles()

        elif choice == "2":
            health()

        elif choice == "3":
            break

        else:
            print("Invalid option")


# -----------------------------
# USER MENU
# -----------------------------
def user_menu():

    while True:

        print("\n------ USER MENU ------")
        print("1. Health")
        print("2. Exit")

        choice = input("Select option: ")

        if choice == "1":
            health()

        elif choice == "2":
            break

        else:
            print("Invalid option")


# -----------------------------
# MAIN MENU
# -----------------------------
def main():

    while True:

        print("\n====== MAIN MENU ======")
        print("1. Health")
        print("2. Register")
        print("3. Login")
        print("4. Exit")

        choice = input("Select option: ")

        if choice == "1":
            health()

        elif choice == "2":
            register()

        elif choice == "3":

            if login():

                if user_type == "admin":
                    admin_menu()
                else:
                    user_menu()

        elif choice == "4":
            break

        else:
            print("Invalid option")


if __name__ == "__main__":
    main()