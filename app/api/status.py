from fastapi import APIRouter
from app.models.transaction import Transaction
import pandas as pd

from app.database.connection import SessionLocal
from app.models.job import Job
from app.models.summary import JobSummary

router = APIRouter()


@router.get("/jobs/{job_id}/status")
def get_job_status(job_id: int):

    db = SessionLocal()

    job = db.query(Job).filter(Job.id == job_id).first()

    db.close()

    if job is None:
        return {
            "message": "Job not found"
        }

    return {
        "job_id": job.id,
        "status": job.status
    }


@router.get("/jobs/{job_id}/summary")
def get_job_summary(job_id: int):

    db = SessionLocal()

    summary = (
        db.query(JobSummary)
        .filter(JobSummary.job_id == job_id)
        .first()
    )

    db.close()

    if summary is None:
        return {
            "message": "Summary not found"
        }

    return {
        "job_id": summary.job_id,
        "total_transactions": summary.total_transactions,
        "total_amount": summary.total_amount,
        "successful_transactions": summary.successful_transactions,
        "failed_transactions": summary.failed_transactions,
        "anomaly_count": summary.anomaly_count,
        "duplicate_count": summary.duplicate_count
    }
    
@router.get("/jobs/{job_id}/results")
def get_job_results(job_id: int):

    db = SessionLocal()

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    summary = (
        db.query(JobSummary)
        .filter(JobSummary.job_id == job_id)
        .first()
    )

    db.close()

    if job is None:
        return {
            "message": "Job not found"
        }

    if summary is None:
        return {
            "message": "Summary not found"
        }

    return {
        "job_id": job.id,
        "status": job.status,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
        "summary": {
            "total_transactions": summary.total_transactions,
            "total_amount": summary.total_amount,
            "successful_transactions": summary.successful_transactions,
            "failed_transactions": summary.failed_transactions,
            "anomaly_count": summary.anomaly_count,
            "duplicate_count": summary.duplicate_count
        }
    }    
    
@router.get("/jobs/{job_id}/analytics")
def get_job_analytics(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "merchant": t.merchant,
            "amount": t.amount,
            "status": t.status,
            "category": t.category
        }
        for t in transactions
    ])

    top_merchant = (
        df["merchant"]
        .value_counts()
        .idxmax()
    )

    highest_transaction = float(df["amount"].max())

    average_transaction_amount = float(
        round(df["amount"].mean(), 2)
    )

    success_rate = round(
        (
            len(df[df["status"] == "SUCCESS"])
            / len(df)
        ) * 100,
        2
    )

    failure_rate = round(
        (
            len(df[df["status"] == "FAILED"])
            / len(df)
        ) * 100,
        2
    )

    category_spending = (
        df.groupby("category")["amount"]
        .sum()
        .to_dict()
    )

    return {
        "job_id": job_id,
        "top_merchant": top_merchant,
        "highest_transaction": highest_transaction,
        "average_transaction_amount": average_transaction_amount,
        "success_rate": success_rate,
        "failure_rate": failure_rate,
        "category_spending": category_spending
    }    
    
@router.get("/jobs/{job_id}/insights")
def get_job_insights(job_id: int):

    db = SessionLocal()

    summary = (
        db.query(JobSummary)
        .filter(JobSummary.job_id == job_id)
        .first()
    )

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if summary is None:
        return {
            "message": "Summary not found"
        }

    if not transactions:
        return {
            "message": "Transactions not found"
        }

    df = pd.DataFrame([
        {
            "merchant": t.merchant
        }
        for t in transactions
    ])

    top_merchant = df["merchant"].value_counts().idxmax()

    insight = (
        f"Processed {summary.total_transactions} transactions totaling ₹{summary.total_amount:.2f}. "
        f"{summary.successful_transactions} transactions were successful and "
        f"{summary.failed_transactions} failed. "
        f"Detected {summary.anomaly_count} anomalies and removed "
        f"{summary.duplicate_count} duplicates. "
        f"{top_merchant} was the most frequent merchant."
    )

    return {
        "job_id": job_id,
        "insight": insight
    }    
    
@router.get("/jobs/{job_id}/top-merchants")
def get_top_merchants(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "merchant": t.merchant
        }
        for t in transactions
    ])

    top_merchants = (
        df["merchant"]
        .value_counts()
        .head(10)
        .to_dict()
    )

    return {
        "job_id": job_id,
        "top_merchants": top_merchants
    }    
    
@router.get("/jobs/{job_id}/top-transactions")
def get_top_transactions(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "txn_id": t.txn_id,
            "merchant": t.merchant,
            "amount": t.amount,
            "category": t.category
        }
        for t in transactions
    ])

    top_transactions = (
        df.sort_values(
            by="amount",
            ascending=False
        )
        .head(10)
        .to_dict(orient="records")
    )

    return {
        "job_id": job_id,
        "top_transactions": top_transactions
    }    
    
@router.get("/jobs/{job_id}/categories")
def get_category_spending(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "category": t.category,
            "amount": t.amount
        }
        for t in transactions
    ])

    category_spending = (
        df.groupby("category")["amount"]
        .sum()
        .round(2)
        .to_dict()
    )

    return {
        "job_id": job_id,
        "category_spending": category_spending
    }
    
@router.get("/jobs/{job_id}/success-rate")
def get_success_rate(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "status": t.status
        }
        for t in transactions
    ])

    success_count = int(
        (df["status"] == "SUCCESS").sum()
    )

    failed_count = int(
        (df["status"] == "FAILED").sum()
    )

    total = len(df)

    success_rate = round(
        success_count * 100 / total,
        2
    )

    failure_rate = round(
        failed_count * 100 / total,
        2
    )

    return {
        "job_id": job_id,
        "success_rate": success_rate,
        "failure_rate": failure_rate
    }


@router.get("/jobs/{job_id}/outliers")
def get_outliers(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "txn_id": t.txn_id,
            "merchant": t.merchant,
            "amount": t.amount
        }
        for t in transactions
    ])

    mean_amount = df["amount"].mean()

    std_amount = df["amount"].std()

    threshold = mean_amount + 2 * std_amount

    outliers = (
        df[df["amount"] > threshold]
        .sort_values(by="amount", ascending=False)
        .to_dict(orient="records")
    )

    return {
        "job_id": job_id,
        "threshold": round(float(threshold), 2),
        "outlier_count": len(outliers),
        "outliers": outliers
    }
    
@router.get("/jobs/{job_id}/merchant-leaderboard")
def get_merchant_leaderboard(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "merchant": t.merchant
        }
        for t in transactions
    ])

    total_transactions = len(df)

    merchant_counts = df["merchant"].value_counts()

    leaderboard = {}

    for merchant, count in merchant_counts.items():

        leaderboard[merchant] = {
            "count": int(count),
            "percentage": round(
                count * 100 / total_transactions,
                2
            )
        }

    return {
        "job_id": job_id,
        "merchant_leaderboard": leaderboard
    }
    
@router.get("/jobs/{job_id}/merchant-spending")
def get_merchant_spending(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "merchant": t.merchant,
            "amount": t.amount
        }
        for t in transactions
    ])

    merchant_spending = (
        df.groupby("merchant")["amount"]
        .sum()
        .sort_values(ascending=False)
        .round(2)
        .to_dict()
    )

    return {
        "job_id": job_id,
        "merchant_spending": merchant_spending
    }
    
@router.get("/jobs/{job_id}/top-spending-merchants")
def get_top_spending_merchants(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "merchant": t.merchant,
            "amount": t.amount
        }
        for t in transactions
    ])

    top_spending = (
        df.groupby("merchant")["amount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .round(2)
        .to_dict()
    )

    return {
        "job_id": job_id,
        "top_spending_merchants": top_spending
    }
    
@router.get("/jobs/{job_id}/zscore-outliers")
def get_zscore_outliers(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "txn_id": t.txn_id,
            "merchant": t.merchant,
            "amount": t.amount
        }
        for t in transactions
    ])

    mean_amount = df["amount"].mean()
    std_amount = df["amount"].std()

    df["z_score"] = (
        (df["amount"] - mean_amount)
        / std_amount
    )

    outliers = (
        df[
            df["z_score"].abs() > 2
        ]
        .sort_values(
            by="z_score",
            ascending=False
        )
        .round(2)
        .to_dict(orient="records")
    )

    return {
        "job_id": job_id,
        "outlier_count": len(outliers),
        "outliers": outliers
    }
    
@router.get("/jobs/{job_id}/monthly-spending")
def get_monthly_spending(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "date": t.date,
            "amount": t.amount
        }
        for t in transactions
    ])

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
        dayfirst=True
    )

    df["month"] = df["date"].dt.strftime("%Y-%m")

    monthly_spending = (
        df.groupby("month")["amount"]
        .sum()
        .round(2)
        .sort_index()
        .to_dict()
    )

    return {
        "job_id": job_id,
        "monthly_spending": monthly_spending
    }
    
@router.get("/jobs/{job_id}/category-ranking")
def get_category_ranking(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "category": t.category,
            "amount": t.amount
        }
        for t in transactions
    ])

    category_ranking = (
        df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
        .round(2)
        .to_dict()
    )

    return {
        "job_id": job_id,
        "category_ranking": category_ranking
    }
    
@router.get("/jobs/{job_id}/risk-score")
def get_risk_score(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "amount": t.amount,
            "status": t.status,
            "notes": t.notes
        }
        for t in transactions
    ])

    failed_count = (
        df["status"]
        .astype(str)
        .str.upper()
        .eq("FAILED")
        .sum()
    )

    suspicious_count = (
        df["notes"]
        .astype(str)
        .str.upper()
        .str.contains("SUSPICIOUS")
        .sum()
    )

    anomaly_count = (
        df["amount"] > 100000
    ).sum()

    risk_score = (
        failed_count * 2
        + suspicious_count * 5
        + anomaly_count * 10
    )

    if risk_score < 30:
        level = "LOW"
    elif risk_score < 70:
        level = "MEDIUM"
    else:
        level = "HIGH"

    return {
        "job_id": job_id,
        "risk_score": int(risk_score),
        "risk_level": level
    }
    
@router.get("/jobs/{job_id}/ai-summary")
def get_ai_summary(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "merchant": t.merchant,
            "amount": t.amount,
            "status": t.status,
            "notes": t.notes
        }
        for t in transactions
    ])

    total_transactions = len(df)

    total_amount = round(df["amount"].sum(), 2)

    top_spending_merchant = (
        df.groupby("merchant")["amount"]
        .sum()
        .idxmax()
    )

    most_frequent_merchant = (
        df["merchant"]
        .value_counts()
        .idxmax()
    )

    anomaly_count = int(
        (df["amount"] > 100000).sum()
    )

    failed_count = int(
        (
            df["status"]
            .astype(str)
            .str.upper()
            .eq("FAILED")
        ).sum()
    )

    risk_score = (
        failed_count * 2
        + anomaly_count * 10
    )

    if risk_score < 30:
        risk_level = "LOW"
    elif risk_score < 70:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    summary = (
        f"Processed {total_transactions} transactions totaling ₹{total_amount}. "
        f"{top_spending_merchant} contributed the highest spending while "
        f"{most_frequent_merchant} was the most frequent merchant. "
        f"{anomaly_count} anomalies were detected. "
        f"Overall risk level is {risk_level}."
    )

    return {
        "job_id": job_id,
        "summary": summary
    }
    
@router.get("/jobs/{job_id}/fraud-alerts")
def get_fraud_alerts(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    alerts = []

    for t in transactions:

        reasons = []

        if t.amount > 100000:
            reasons.append("High Amount")

        if str(t.status).upper() == "FAILED":
            reasons.append("Failed Transaction")

        if "SUSPICIOUS" in str(t.notes).upper():
            reasons.append("Suspicious Note")

        if reasons:

            alerts.append({
                "txn_id": t.txn_id,
                "merchant": t.merchant,
                "amount": t.amount,
                "reasons": reasons
            })

    return {
        "job_id": job_id,
        "fraud_alert_count": len(alerts),
        "alerts": alerts
    }
    
@router.get("/jobs/{job_id}/currency-breakdown")
def get_currency_breakdown(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "currency": t.currency
        }
        for t in transactions
    ])

    breakdown = (
        df["currency"]
        .value_counts()
        .to_dict()
    )

    return {
        "job_id": job_id,
        "currency_breakdown": breakdown
    }
    
@router.get("/jobs/{job_id}/status-breakdown")
def get_status_breakdown(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "status": t.status
        }
        for t in transactions
    ])

    breakdown = (
        df["status"]
        .value_counts()
        .to_dict()
    )

    return {
        "job_id": job_id,
        "status_breakdown": breakdown
    }

@router.get("/jobs/{job_id}/account-summary")
def get_account_summary(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "account_id": t.account_id,
            "amount": t.amount
        }
        for t in transactions
    ])

    summary = (
        df.groupby("account_id")["amount"]
        .sum()
        .round(2)
        .sort_values(ascending=False)
        .to_dict()
    )

    return {
        "job_id": job_id,
        "account_summary": summary
    }
    
@router.get("/jobs/{job_id}/merchant-health")
def get_merchant_health(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    health = {}

    merchants = set(t.merchant for t in transactions)

    for merchant in merchants:

        merchant_txns = [
            t for t in transactions
            if t.merchant == merchant
        ]

        risk_score = 0

        for t in merchant_txns:

            if str(t.status).upper() == "FAILED":
                risk_score += 2

            if "SUSPICIOUS" in str(t.notes).upper():
                risk_score += 5

            if t.amount > 100000:
                risk_score += 10

        if risk_score < 10:
            level = "GOOD"
        elif risk_score < 20:
            level = "MEDIUM RISK"
        else:
            level = "HIGH RISK"

        health[merchant] = level

    return {
        "job_id": job_id,
        "merchant_health": health
    }    
    
@router.get("/jobs/{job_id}/narrative-summary")
def get_narrative_summary(job_id: int):

    db = SessionLocal()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    db.close()

    if not transactions:
        return {
            "message": "No transactions found"
        }

    df = pd.DataFrame([
        {
            "merchant": t.merchant,
            "amount": t.amount,
            "currency": t.currency,
            "is_anomaly": t.is_anomaly
        }
        for t in transactions
    ])

    total_spend_inr = round(
        df[df["currency"] == "INR"]["amount"].sum(),
        2
    )

    total_spend_usd = round(
        df[df["currency"] == "USD"]["amount"].sum(),
        2
    )

    top_merchants = (
        df.groupby("merchant")["amount"]
        .sum()
        .sort_values(ascending=False)
        .head(3)
        .index
        .tolist()
    )

    anomaly_count = int(
        df["is_anomaly"].sum()
    )

    if anomaly_count < 3:
        risk_level = "LOW"
    elif anomaly_count < 7:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    narrative = (
        f"Most spending occurred on {', '.join(top_merchants)}. "
        f"{anomaly_count} anomalies were detected. "
        f"Overall risk level is {risk_level}."
    )

    return {
        "job_id": job_id,
        "total_spend_inr": total_spend_inr,
        "total_spend_usd": total_spend_usd,
        "top_merchants": top_merchants,
        "risk_level": risk_level,
        "narrative": narrative
    }                            