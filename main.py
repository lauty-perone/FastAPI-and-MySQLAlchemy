from fastapi import FastAPI
from routers import user_db

#Crea una instancia de FastAPI
app = FastAPI()

#Incluye el router user
app.include_router(user_db.user)

#Devuelve en "/" "Hola Mundo"
@app.get("/")
async def root():
    return ("Hola Mundo")