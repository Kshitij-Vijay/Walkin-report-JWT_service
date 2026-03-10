from datetime import datetime
from fastapi import APIRouter, HTTPException, Header,Request
from jose import JWTError
import jwt
from config import ALGORITHM, SECRET_KEY
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

    # Check username
    cursor.execute(
        "SELECT * FROM users WHERE name=%s",
        (user.name,)
    )
    existing_user = cursor.fetchone()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check email
    cursor.execute(
        "SELECT * FROM users WHERE email=%s",
        (user.email,)
    )
    existing_email = cursor.fetchone()

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user.password)

    cursor.execute(
        """
        INSERT INTO users (name, email, password, type, roles)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user.name, user.email, hashed, user.type, "0")
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
def get_users(request: Request):

    user = request.state.user

    if not user:
        return {"error": "Unauthorized"}

    if user["type"] != "admin":
        return {"error": "Admin only"}

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id,name,type,roles FROM users")

    return cursor.fetchall()


# --------------------------
# GET ALL ACTIONS
# --------------------------
@router.get("/actions")
def get_actions(request: Request):

    user = request.state.user

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if user["type"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

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

    query = "UPDATE users SET name='" + user.name +  "', type='" + user.type + "', roles='" + user.roles +"' WHERE id=" + str(user.id)

    cursor.execute(query)

    db.commit()

    return {"message": "User updated",
            "query" : query}


@router.post("/logs")
def create_log(log: LogModel):

    db = get_db()
    cursor = db.cursor()

    current_time = datetime.now()

    cursor.execute(
        """
        INSERT INTO logs (username, query, description, status, clock)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (log.username, log.query, log.description, log.status, current_time)
    )

    db.commit()

    return {"message": "Log inserted successfully"}


@router.get("/token_validity")
def token_validity(authorization: str = Header(None)):

    if not authorization:
        return {"valid": False, "message": "Authorization header missing"}

    # Extract token
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization

    # Check token format before decoding
    if token.count(".") != 2:
        return {"valid": False, "message": "Invalid token format"}

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        exp = payload.get("exp")
        exp_time = datetime.fromtimestamp(exp)
        remaining = exp_time - datetime.utcnow()

        return {
            "valid": True,
            "expires_at": exp_time,
            "seconds_remaining": int(remaining.total_seconds())
        }

    except jwt.ExpiredSignatureError:
        return {"valid": False, "message": "Token expired"}

    except jwt.InvalidTokenError:
        return {"valid": False, "message": "Invalid token"}
    

@router.get("/GetWalkins", response_model=List[Walkins])
def GetWalkins():

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM walkins")

    rows = cursor.fetchall()

    walkins_list = []

    for row in rows:
        walkins_list.append(Walkins(**row))

    return walkins_list


@router.get("/GetStores", response_model=List[Store])
def GetStores():

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM store")

    rows = cursor.fetchall()

    stores = [Store(**row) for row in rows]

    return stores

@router.get("/GetCategor", response_model=list[Categor])
def GetCategor():

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM categor")

    return cursor.fetchall()

@router.get("/GetStaff", response_model=list[Staff])
def GetStaff():

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM staff")

    return cursor.fetchall()

@router.get("/GetStatus", response_model=list[Status])
def GetStatus(): 

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM status")

    return cursor.fetchall()


@router.get("/getroles")
def getroles(username: str):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT roles FROM users WHERE name=%s",
        (username,)
    )

    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    return result["roles"]


@router.get("/GetWalkinColumns", response_model=List[str])
def GetWalkinColumns():

    db = get_db()
    cursor = db.cursor()

    query = """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'walkins'
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    columns = [row[0] for row in rows]

    return columns


@router.put("/UpdateWalkin")
def update_walkin(w: Walkins):

    db = get_db()
    cursor = db.cursor()

    query = """
    UPDATE walkins SET
        name = %s,
        area = %s,
        pin = %s,
        phone = %s,
        source = %s,
        team = %s,
        status = %s,
        categor = %s,
        products = %s,
        store = %s,
        remarks = %s,
        created_at = %s,
        amount = %s,
        followup = %s
    WHERE id = %s
    """

    try:
        cursor.execute(
            query,
            (
                w.name,
                w.area,
                w.pin,
                w.phone,
                w.source,
                w.team,
                w.status,
                w.categor,
                w.products,
                w.store,
                w.remarks,
                w.created_at,
                w.amount,
                w.followup,
                w.id
            )
        )
        db.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Walkin not found")

        return {"message": "Walkin updated successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/InsertWalkin")
def insert_walkin(w: Walkins):

    db = get_db()
    cursor = db.cursor()

    query = """
    INSERT INTO walkins
    (name, area, pin, phone, source, team, status, categor, products, store, remarks, created_at, amount, followup)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # If created_at is not provided, use current timestamp
    created_at = w.created_at or datetime.now()

    try:
        cursor.execute(
            query,
            (
                w.name,
                w.area,
                w.pin,
                w.phone,
                w.source,
                w.team,
                w.status,
                w.categor,
                w.products,
                w.store,
                w.remarks,
                created_at,
                w.amount,
                w.followup
            )
        )
        db.commit()
        return {"message": "Walkin inserted successfully", "id": cursor.lastrowid}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/DeleteWalkin/{id}")
def delete_walkin(id: int):
    db = get_db()
    cursor = db.cursor()

    query = "DELETE FROM walkins WHERE id = %s"

    try:
        cursor.execute(query, (id,))
        db.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="No record found with the given ID")

        return {"message": "Walkin deleted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.post("/backup_walkins")
def backup_walkins():
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Drop backup table if exists
        cursor.execute("DROP TABLE IF EXISTS walkins_backup;")
        # Create backup table and copy all records
        cursor.execute("CREATE TABLE walkins_backup LIKE walkins;")
        cursor.execute("INSERT INTO walkins_backup SELECT * FROM walkins;")
        db.commit()
        return {"message": "Backup successful"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")