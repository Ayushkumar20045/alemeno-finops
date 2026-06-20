from sqlalchemy import Column, Integer, Float

from app.database.base import Base


class JobSummary(Base):
    __tablename__ = "job_summaries"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(Integer)

    total_transactions = Column(Integer)

    total_amount = Column(Float)

    successful_transactions = Column(Integer)

    failed_transactions = Column(Integer)

    anomaly_count = Column(Integer)

    duplicate_count = Column(Integer)