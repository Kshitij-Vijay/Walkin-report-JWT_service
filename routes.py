from fastapi import APIRouter, HTTPException
from database import get_db
from models import *
from auth import hash_password, verify_password, create_token

router = APIRouter()

# -------------------
# HEALTH ROUTE
# -------------------
@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "fastapi-backend"
    }


# -------------------
# REGISTER
# -------------------
@router.post("/register")
def register(user: RegisterModel):

    if user.type not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Invalid user type")

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE name=%s",
        (user.name,)
    )

    existing = cursor.fetchone()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = hash_password(user.password)

    cursor.execute(
        """
        INSERT INTO users (name,password,type,roles)
        VALUES (%s,%s,%s,%s)
        """,
        (user.name, hashed, user.type, "0")
    )

    db.commit()

    return {"message": "User registered successfully"}


# -------------------
# LOGIN
# -------------------
@router.post("/login")
def login(user: LoginModel):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE name=%s",
        (user.name,)
    )

    db_user = cursor.fetchone()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({
        "id": db_user["id"],
        "name": db_user["name"],
        "type": db_user["type"]
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }




# --------------------------
# GET ALL USERS
# --------------------------
@router.get("/users")
def get_users():

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id,name,type,roles FROM users")

    users = cursor.fetchall()

    return users


# --------------------------
# GET ALL ACTIONS
# --------------------------
@router.get("/actions")
def get_actions():

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM actions")

    actions = cursor.fetchall()

    return actions


# --------------------------
# UPDATE USER ROLES
# --------------------------
@router.post("/update_user")
def update_user(user: User):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE users
        SET name=%s, type=%s, roles=%s
        WHERE id=%s
        """,
        (user.name, user.type, user.roles, user.id)
    )

    db.commit()

    return {"message": "User updated"}