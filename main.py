import uvicorn
from fastapi import FastAPI
from database import engine, Base
from routes import auth as auth_router, posts as posts_router, comments as comments_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Blog API", version="1.0.0")

app.include_router(auth_router.router)
app.include_router(posts_router.router)
app.include_router(comments_router.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)