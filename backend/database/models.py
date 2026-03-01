import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database.connection import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="pending")
    output_type = Column(String, nullable=False)  # "image" or "video"

    user_input_text = Column(Text, nullable=False)
    user_input_github = Column(Text, nullable=True)
    user_input_code = Column(Text, nullable=True)
    style_config = Column(Text, nullable=True)  # JSON string

    generated_prompt = Column(Text, nullable=True)
    output_url = Column(Text, nullable=True)
    caption = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    revisions = relationship("ImageRevision", back_populates="job", order_by="ImageRevision.revision_number")


class ImageRevision(Base):
    __tablename__ = "image_revisions"

    id = Column(String, primary_key=True, default=generate_uuid)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    revision_number = Column(Integer, nullable=False)
    revision_prompt = Column(Text, nullable=False)
    output_url = Column(Text, nullable=True)
    caption = Column(Text, nullable=True)
    generated_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    job = relationship("Job", back_populates="revisions")
