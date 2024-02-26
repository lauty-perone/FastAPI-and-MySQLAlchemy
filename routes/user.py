from fastapi import APIRouter, status, HTTPException
from models.user import users
from schemas.user import User, UserCount
from typing import List
from sqlalchemy import func, select
from cryptography.fernet import Fernet
from config.db import conn

user = APIRouter(prefix="/userdb",
                   tags=["userdb"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

key = Fernet.generate_key()
f = Fernet(key)

@user.get("/", response_model=List[User], description= "Get a list of all users")
async def get_users():
    return conn.execute(users.select()).fetchall()

@user.get("/users/count", response_model=UserCount)
async def get_users_count():
    result = conn.execute(select([func.count()]).select_from(users))
    return {"total": tuple(result)[0][0]}

@user.get("/users/{id}", response_model= User, description= "Get a single user by id")
async def get_user(id: str):
    return conn.execute(users.select().where(users.c.id == id)).first()

@user.post("/", response_model= User, description="Create a new user",
            status_code=status.HTTP_201_CREATED)
async def create_user(user: User):

    if (conn.execute(users.select().where(users.c.email == user.email)) == None):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El usuario ya existe"
        )

    new_user = {"name" : user.name, "email": user.email}
    new_user["password"] = f.encrypt(user.password.encode("utf-8"))
    result = conn.execute(users.insert().values(new_user))
    return conn.execute(users.select().where(users.c.id == result.lastrowid)).first()

@user.put("/", response_model=User, description="Update a User by id")
async def update_user(user: User, id: str):
    try:
        conn.execute(
            users.update().values(name = user.name, email = user.email, password = user.password)
            .where(users.c.id == id)
        )
    except:
        return {"Error: No se ha actualizado el usuario"}
    return conn.execute(users.select().where(users.c.id == id)).first()

@user.delete("/{id}",  status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: str):
    try:
        conn.execute(users.delete().where(users.c.id == id))
    except:
        return {"Error: No se ha encontrado el usuario"}
    return conn.execute(users.select().where(users.c.id == id)).first()



