from fastapi import FastAPI
from app.routes import applications, jobs, users
from dotenv import load_dotenv
import os

load_dotenv()


app = FastAPI(title="ATS API")

app.include_router(applications.router)
app.include_router(jobs.router)
app.include_router(users.router)
