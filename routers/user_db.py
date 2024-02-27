from fastapi import status, HTTPException, APIRouter
from models.user import users
from schemas.user import User
from typing import List
from cryptography.fernet import Fernet
from config.db import conn

#Crea un router con el prefijo /userdb
user = APIRouter(prefix="/userdb",
                   tags=["userdb"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

#Variables para encriptar la contraseña
key = Fernet.generate_key()
f = Fernet(key)

#Devuelve todos los usuarios de la DB
@user.get("/", response_model=List[User], description= "Get a list of all users")
async def get_users():
    return conn.execute(users.select()).fetchall()

#Devuelve un usuario 
@user.get("/{id}", response_model=User,description= "Get a single user by id")
async def get_user(id: int):

    result = search_user(id)
    #Comprueba si existe el usuario
    if(result ==None):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe"
        )
    return result

#Crea un usuario
@user.post("/", response_model= User, description="Create a new user",status_code=status.HTTP_201_CREATED)
async def create_user(user: User):

    #Comprueba si existe en la base de datos por email
    if ( conn.execute(users.select().where(users.c.email == user.email)).first()!= None):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El usuario ya existe"
        )
    
    #Crea un diccionario que tenga los datos del usuario y lo inserta en la DB
    new_user = {"name" : user.name, "email": user.email}
    new_user["password"] = f.encrypt(user.password.encode("utf-8"))
    result = conn.execute(users.insert().values(new_user))
    return conn.execute(users.select().where(users.c.id == result.lastrowid)).first()

#Actualiza un usuario
@user.put("/", response_model=User, description="Update a User by id")
async def update_user(user: User):
    
    exception = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="El usuario no existe")
    
    try:
        #Verifica si existe el usuario con id sino lanza la excepcion
        if (search_user(user.id) == None):
            raise exception
        
        #Actualiza los campos del usuario encontrado por id
        conn.execute(
            users.update().values(name = user.name, 
                                email = user.email, 
                                password = f.encrypt(user.password.encode("utf-8")))
            .where(users.c.id == user.id)
        )
        #Retorna al usuario actualizado
        return search_user(user.id)
    
    except:
        raise exception

    

#Elimina un usuario recibido por {id}
@user.delete("/{id}",response_model=User)
async def delete_user(id: int):
    
    #Verifica si existe el usuario
    user = search_user(id)

    #Si no existe lanza una excepción
    if(user==None): 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="El usuario no existe")
    
    #Como existe, lo elimina y luego retorna al usuario eliminado
    conn.execute(users.delete().where(users.c.id == id))
    return user

#Busca un usuario por un campo
def search_user(id:int):
    return conn.execute(users.select().where(users.c.id == id)).first()
