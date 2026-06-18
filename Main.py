import email

from django import db
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from Database import init_db, get_db
from Auth import (
    create_token,
    hash_password,
    verify_password
)

from Schemas import customer,Login

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-frontend-domain.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()


# -----------------------------
# CUSTOMER REGISTRATION
# -----------------------------
@app.post("/Register")
def register(cust: customer):
    try:
        hashed_password = hash_password(cust.password)
        with get_db() as db:
            db.execute(
                """
                INSERT INTO customer
                (name, email, password, phone_no, gender, age)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING cust_id
                """,
                (
                    cust.name,
                    cust.email,
                    hashed_password,
                    cust.phone_no,
                    cust.gender,
                    cust.age
                )
            )
            customer_id = db.fetchone()[0]   # ✅ fetchone INSIDE with block
        return {
            "message": "Customer registered successfully",
            "customer_id": customer_id
        }
    except Exception as e:
        print("🔴 REGISTER ERROR:", str(e))  # 👈 Add this line
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------
# CUSTOMER LOGIN
# -----------------------------
from Schemas import customer, Login

@app.post("/login")
def login(data: Login):
    email = data.email
    password = data.password
    try:
        with get_db() as db:
            db.execute("""
                SELECT cust_id, password, name, email
                FROM customer WHERE email=%s
            """, (email,))

            result = db.fetchone()
            print("RESULT =", result)

            if result is None:
                raise HTTPException(
                    status_code=404,
                    detail="Customer not found"
                )

            cust_id        = result[0]
            hashed_password = result[1]
            name           = result[2]
            email_result   = result[3]

            if not verify_password(password, hashed_password):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid Password"
                )

            token = create_token(cust_id)

            return {
                "access_token": token,
                "token_type": "bearer",
                "cust_id": cust_id,        # ✅ now visible
                "name": name,              # ✅ now visible
                "email": email_result      # ✅ now visible
            }

    except HTTPException:
        raise   # ✅ re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    



@app.get("/customers")
def customers():

    with get_db() as db:
        db.execute(
            """
            SELECT cust_id, name, email
            FROM customer
            """
        )

        result = db.fetchall()

    return result