from fastapi import FastAPI
from routes.user import user

app = FastAPI()

app.include_router(user.routes)

@app.get("/")
async def root():
    return ("Hola Mundo")