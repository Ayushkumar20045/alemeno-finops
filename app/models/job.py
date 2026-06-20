from sqlalchemy import Column, Integer, String, DateTime

from app.database.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String)

    status = Column(String)

    row_count_raw = Column(Integer)

    row_count_clean = Column(Integer)

    created_at = Column(DateTime)

    completed_at = Column(DateTime)

    error_message = Column(String)