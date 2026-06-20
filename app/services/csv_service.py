import pandas as pd

from app.database.connection import SessionLocal
from app.models.job import Job
from app.models.transaction import Transaction


def process_csv(job_id, filepath):

    db = SessionLocal()

    job = db.query(Job).filter(Job.id == job_id).first()

    df = pd.read_csv(filepath)

    raw_count = len(df)

    df = df.drop_duplicates()

    clean_count = len(df)

    for _, row in df.iterrows():

        transaction = Transaction(
            job_id=job_id,
            txn_id=str(row["txn_id"]),
            date=str(row["date"]),
            merchant=str(row["merchant"]),
            amount=float(row["amount"]),
            currency=str(row["currency"]),
            status=str(row["status"]),
            category=str(row["category"]),
            account_id=str(row["account_id"])
        )

        db.add(transaction)

    job.row_count_raw = raw_count
    job.row_count_clean = clean_count
    job.status = "completed"

    db.commit()
    db.close()