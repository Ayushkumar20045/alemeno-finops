from fastapi import APIRouter, UploadFile, File
from datetime import datetime
from typing import Optional

from app.database.connection import SessionLocal
from app.models.job import Job
from app.models.summary import JobSummary
from app.models.transaction import Transaction
from app.tasks.process_csv import process_csv

router = APIRouter()


@router.post("/jobs/upload")
def upload_csv(file: UploadFile = File(...)):

    filepath = f"uploads/{file.filename}"

    with open(filepath, "wb") as buffer:
        buffer.write(file.file.read())

    db = SessionLocal()

    job = Job(
        filename=file.filename,
        status="pending",
        row_count_raw=0,
        row_count_clean=0,
        created_at=datetime.now()
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    job_id = job.id

    db.close()

    process_csv.delay(job_id, filepath)

    return {
        "job_id": job_id,
        "status": "pending"
    }


@router.get("/jobs")
def get_jobs(status: Optional[str] = None):

    db = SessionLocal()

    query = db.query(Job)

    if status:
        query = query.filter(Job.status == status)

    jobs = query.all()

    result = []

    for job in jobs:
        result.append({
            "id": job.id,
            "filename": job.filename,
            "status": job.status,
            "row_count_raw": job.row_count_raw,
            "row_count_clean": job.row_count_clean,
            "created_at": job.created_at,
            "completed_at": job.completed_at
        })

    db.close()

    return result


@router.get("/jobs/{job_id}/status")
def get_job_status(job_id: int):

    db = SessionLocal()

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if job is None:
        db.close()
        return {
            "message": "Job not found"
        }

    response = {
        "job_id": job.id,
        "status": job.status
    }

    if job.status == "completed":

        summary = (
            db.query(JobSummary)
            .filter(JobSummary.job_id == job_id)
            .first()
        )

        if summary:

            response["summary"] = {
                "total_transactions": summary.total_transactions,
                "total_amount": summary.total_amount,
                "successful_transactions": summary.successful_transactions,
                "failed_transactions": summary.failed_transactions,
                "anomaly_count": summary.anomaly_count,
                "duplicate_count": summary.duplicate_count
            }

    db.close()

    return response


@router.get("/jobs/{job_id}/results")
def get_job_results(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    summary = (
        db.query(JobSummary)
        .filter(JobSummary.job_id == job_id)
        .first()
    )

    cleaned_transactions = []

    flagged_anomalies = []

    category_breakdown = {}

    for txn in transactions:

        transaction_data = {
            "txn_id": txn.txn_id,
            "date": txn.date,
            "merchant": txn.merchant,
            "amount": txn.amount,
            "currency": txn.currency,
            "status": txn.status,
            "category": txn.category,
            "account_id": txn.account_id,
            "notes": txn.notes
        }

        cleaned_transactions.append(transaction_data)

        if txn.is_anomaly:

            flagged_anomalies.append({
                "txn_id": txn.txn_id,
                "merchant": txn.merchant,
                "amount": txn.amount,
                "reason": txn.anomaly_reason
            })

        if txn.category not in category_breakdown:
            category_breakdown[txn.category] = 0

        category_breakdown[txn.category] += txn.amount

    response = {
        "cleaned_transactions": cleaned_transactions,
        "flagged_anomalies": flagged_anomalies,
        "category_breakdown": category_breakdown
    }

    if summary:

        response["summary"] = {
            "total_transactions": summary.total_transactions,
            "total_amount": summary.total_amount,
            "successful_transactions": summary.successful_transactions,
            "failed_transactions": summary.failed_transactions,
            "anomaly_count": summary.anomaly_count,
            "duplicate_count": summary.duplicate_count
        }

    db.close()

    return response


@router.get("/transactions")
def get_transactions(
    category: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
):

    db = SessionLocal()

    query = db.query(Transaction)

    if category:
        query = query.filter(
            Transaction.category == category
        )

    if status:
        query = query.filter(
            Transaction.status == status.upper()
        )

    transactions = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []

    for txn in transactions:

        result.append({
            "txn_id": txn.txn_id,
            "date": txn.date,
            "merchant": txn.merchant,
            "amount": txn.amount,
            "currency": txn.currency,
            "status": txn.status,
            "category": txn.category,
            "account_id": txn.account_id,
            "notes": txn.notes,
            "is_anomaly": txn.is_anomaly,
            "anomaly_reason": txn.anomaly_reason
        })

    db.close()

    return result