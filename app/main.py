from fastapi import FastAPI

from app.database import init_db
from app.routers import auth, todos


app = FastAPI(title="Todo List API") # the app object we use to attach routes, middleware, settings etc., as the app grows

# basic check to ensure the server is alive before proceeding further
@app.get("/health")
async def health_check():
    return {"status": "ok"}


init_db()

app.include_router(auth.router)
app.include_router(todos.router)
