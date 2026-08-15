from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    username: Mapped[str] = mapped_column(String(50), nullable=False)

    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    email_verified: Mapped[bool] = mapped_column(default=False, nullable=False)

    verification_code: Mapped[str | None] = mapped_column(String(6), nullable=True)

    verification_expires: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    papers: Mapped[list["Paper"]] = relationship(back_populates="owner")


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False, default="Untitled paper")

    authors: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    source: Mapped[str] = mapped_column(String(100), nullable=False, default="arxiv")

    abstract: Mapped[str] = mapped_column(Text, nullable=False, default="")

    pdf_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    citation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    references: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    filename: Mapped[str | None] = mapped_column(String(255), nullable=True)

    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[str] = mapped_column(String(50), default="published", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner: Mapped[User | None] = relationship(back_populates="papers")
    notes: Mapped[list["PaperNote"]] = relationship(back_populates="paper", cascade="all, delete-orphan")
    library_items: Mapped[list["LibraryItem"]] = relationship(back_populates="paper", cascade="all, delete-orphan")
    reader_progress: Mapped["ReaderProgress | None"] = relationship(back_populates="paper", uselist=False, cascade="all, delete-orphan")


class LibraryItem(Base):
    __tablename__ = "library_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    paper_id: Mapped[str] = mapped_column(ForeignKey("papers.id"), nullable=False, index=True)

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    paper: Mapped[Paper] = relationship(back_populates="library_items")

    __table_args__ = (
        UniqueConstraint("paper_id", "user_id", name="uq_library_item_user_paper"),
    )


class ReaderProgress(Base):
    __tablename__ = "reader_progress"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    paper_id: Mapped[str] = mapped_column(ForeignKey("papers.id"), nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)

    current_page: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    last_read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    paper: Mapped[Paper] = relationship(back_populates="reader_progress")

    __table_args__ = (
        UniqueConstraint("paper_id", "user_id", name="uq_reader_progress_user_paper"),
    )


class PaperNote(Base):
    __tablename__ = "paper_notes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    paper_id: Mapped[str] = mapped_column(ForeignKey("papers.id"), nullable=False, index=True)

    title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    content: Mapped[str] = mapped_column(Text, nullable=False, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    paper: Mapped[Paper] = relationship(back_populates="notes")
