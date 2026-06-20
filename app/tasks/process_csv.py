import pandas as pd
from datetime import datetime

from app.database.connection import SessionLocal
from app.models.job import Job
from app.models.transaction import Transaction
from app.models.summary import JobSummary
from app.models.insight import Insight
from app.services.llm_service import generate_narrative_summary
from app.celery_app import celery


@celery.task
def process_csv(job_id, filepath):

    db = SessionLocal()

    try:

        job = db.query(Job).filter(Job.id == job_id).first()

        job.status = "processing"

        db.commit()

        df = pd.read_csv(filepath)

        raw_count = len(df)

        df = df.drop_duplicates()

        clean_count = len(df)

        amount_series = (
            df["amount"]
            .astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
            .astype(float)
        )

        df["clean_amount"] = amount_series

        account_medians = (
            df.groupby("account_id")["clean_amount"]
            .median()
            .to_dict()
        )

        domestic_merchants = [
            "Swiggy",
            "Ola",
            "IRCTC"
        ]

        for _, row in df.iterrows():

            txn_id = str(row["txn_id"])

            existing_transaction = (
                db.query(Transaction)
                .filter(Transaction.txn_id == txn_id)
                .first()
            )

            if existing_transaction:
                continue

            amount = float(
                str(row["amount"])
                .replace("$", "")
                .replace(",", "")
            )

            account_id = str(row["account_id"])

            median_amount = account_medians[account_id]

            merchant = str(row["merchant"])

            currency = str(row["currency"]).upper()

            is_anomaly = False
            anomaly_reason = None

            if amount > 3 * median_amount:
                is_anomaly = True
                anomaly_reason = "Amount exceeds 3x account median"

            if merchant in domestic_merchants and currency == "USD":
                is_anomaly = True
                anomaly_reason = "Domestic merchant with USD currency"

            transaction = Transaction(
                job_id=job_id,
                txn_id=txn_id,
                date=pd.to_datetime(
                    row["date"],
                    dayfirst=True
                ).strftime("%Y-%m-%d"),
                merchant=merchant,
                amount=amount,
                currency=currency,
                status=str(row["status"]).upper(),
                category=(
                    "Uncategorized"
                    if pd.isna(row["category"]) or str(row["category"]).strip() == ""
                    else str(row["category"])
                ),
                account_id=account_id,
                notes="" if pd.isna(row["notes"]) else str(row["notes"]),
                is_anomaly=is_anomaly,
                anomaly_reason=anomaly_reason
            )

            db.add(transaction)

        job.row_count_raw = raw_count
        job.row_count_clean = clean_count
        job.status = "completed"
        job.completed_at = datetime.now()

        total_amount = float(amount_series.sum())

        successful_transactions = int(
            (
                df["status"]
                .astype(str)
                .str.upper() == "SUCCESS"
            ).sum()
        )

        failed_transactions = int(
            (
                df["status"]
                .astype(str)
                .str.upper() == "FAILED"
            ).sum()
        )

        anomaly_count = int(
            (
                df["clean_amount"]
                >
                df["account_id"].map(account_medians) * 3
            ).sum()
        )

        duplicate_count = raw_count - clean_count

        existing_summary = (
            db.query(JobSummary)
            .filter(JobSummary.job_id == job_id)
            .first()
        )

        if existing_summary is None:

            summary = JobSummary(
                job_id=job_id,
                total_transactions=clean_count,
                total_amount=total_amount,
                successful_transactions=successful_transactions,
                failed_transactions=failed_transactions,
                anomaly_count=anomaly_count,
                duplicate_count=duplicate_count
            )

            db.add(summary)

        existing_insight = (
            db.query(Insight)
            .filter(Insight.job_id == job_id)
            .first()
        )

        if existing_insight is None:

            merchants = (
                df["merchant"]
                .value_counts()
                .head(3)
                .index
                .tolist()
            )

            total_spend_inr = float(
                df.loc[
                    df["currency"].str.upper() == "INR",
                    "clean_amount"
                ].sum()
            )

            total_spend_usd = float(
                df.loc[
                    df["currency"].str.upper() == "USD",
                    "clean_amount"
                ].sum()
            )

            llm_input = {
                "total_spend_inr": total_spend_inr,
                "total_spend_usd": total_spend_usd,
                "top_3_merchants": merchants,
                "anomaly_count": anomaly_count
            }

            insight_data = generate_narrative_summary(
                llm_input
            )

            insight = Insight(
                job_id=job_id,
                total_spend_inr=insight_data["total_spend_inr"],
                total_spend_usd=insight_data["total_spend_usd"],
                top_3_merchants=", ".join(
                    insight_data["top_3_merchants"]
                ),
                anomaly_count=insight_data["anomaly_count"],
                narrative=insight_data["narrative"],
                risk_level=insight_data["risk_level"]
            )

            db.add(insight)

        db.commit()

    except Exception as e:

        job = db.query(Job).filter(Job.id == job_id).first()

        if job:

            job.status = "failed"
            job.error_message = str(e)

            db.commit()

    finally:

        db.close()