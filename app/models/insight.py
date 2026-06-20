from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.database.base import Base


class Insight(Base):

    __tablename__ = "insights"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))

    total_spend_inr = Column(Float)
    total_spend_usd = Column(Float)

    top_3_merchants = Column(String)
    anomaly_count = Column(Integer)

    narrative = Column(String)
    risk_level = Column(String)