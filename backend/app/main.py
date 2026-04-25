from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, logs, alerts, analytics, ws
from app.database import engine, Base
import os
import json

# Ensure tables are created
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Insider Threat Detection API")

# Add CORS for localhost:3000 and Vite
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(logs.router)
app.include_router(alerts.router)
app.include_router(analytics.router)
app.include_router(ws.router)

@app.get("/")
def read_root():
    return {"message": "Insider Threat Detection API is running"}
