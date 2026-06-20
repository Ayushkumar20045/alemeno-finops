from fastapi import FastAPI

from app.database.base import Base
from app.database.connection import engine
from app.api.status import router as status_router

from app.models.job import Job
from app.models.transaction import Transaction
from app.models.summary import JobSummary
from app.api.jobs import router


app = FastAPI(
    title="Alemeno FinOps API",
    version="1.0.0"
)

app.include_router(router)
app.include_router(status_router)
# Create all database tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {
        "message": "Alemeno FinOps API Running"
    }