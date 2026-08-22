import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings


def _database_url():
    configured = getattr(settings, "DATABASE_URL", None) or os.getenv("DATABASE_URL")
    return configured or "sqlite:///./research_assistant.db"


def _build_engine():
    database_url = _database_url()
    engine_kwargs = {}
    if database_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    try:
        engine = create_engine(database_url, **engine_kwargs)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return engine
    except Exception:
        if database_url.startswith("postgresql"):
            fallback_url = "sqlite:///./research_assistant.db"
            engine = create_engine(fallback_url, connect_args={"check_same_thread": False})
            return engine
        raise


engine = _build_engine()


def _ensure_library_schema():
    with engine.begin() as connection:
        try:
            index_names = connection.execute(
                text("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='library_items'")
            ).fetchall()
            index_names = [row[0] for row in index_names]

            if "uq_library_item_paper" in index_names:
                connection.execute(text("DROP INDEX IF EXISTS uq_library_item_paper"))

            has_user_paper_index = "uq_library_item_user_paper" in index_names
            if not has_user_paper_index:
                connection.execute(
                    text(
                        "CREATE UNIQUE INDEX IF NOT EXISTS uq_library_item_user_paper "
                        "ON library_items (paper_id, user_id)"
                    )
                )

            connection.execute(text("DELETE FROM library_items WHERE user_id IS NULL"))
        except Exception:
            pass


def _ensure_reader_progress_schema():
    with engine.begin() as connection:
        try:
            table_info = connection.execute(text("PRAGMA table_info(reader_progress)")).fetchall()
            if not table_info:
                return

            columns = {row[1] for row in table_info}
            if "user_id" not in columns:
                connection.execute(text("ALTER TABLE reader_progress RENAME TO reader_progress_legacy"))
                connection.execute(
                    text(
                        """
                        CREATE TABLE reader_progress (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            paper_id VARCHAR(255) NOT NULL,
                            user_id INTEGER NULL,
                            current_page INTEGER NOT NULL DEFAULT 1,
                            last_read_at DATETIME NOT NULL,
                            FOREIGN KEY (paper_id) REFERENCES papers(id),
                            FOREIGN KEY (user_id) REFERENCES users(id)
                        )
                        """
                    )
                )
                connection.execute(
                    text(
                        """
                        INSERT INTO reader_progress (id, paper_id, user_id, current_page, last_read_at)
                        SELECT id, paper_id,
                               (SELECT papers.user_id FROM papers WHERE papers.id = reader_progress_legacy.paper_id),
                               current_page,
                               last_read_at
                        FROM reader_progress_legacy
                        """
                    )
                )
                connection.execute(text("DROP TABLE reader_progress_legacy"))

            index_names = connection.execute(
                text("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='reader_progress'")
            ).fetchall()
            index_names = {row[0] for row in index_names}

            if "uq_reader_progress_paper_id" in index_names:
                connection.execute(text("DROP INDEX IF EXISTS uq_reader_progress_paper_id"))
            if "uq_reader_progress_user_paper" not in index_names:
                connection.execute(
                    text(
                        "CREATE UNIQUE INDEX IF NOT EXISTS uq_reader_progress_user_paper "
                        "ON reader_progress (paper_id, user_id)"
                    )
                )

            legacy_indexes = connection.execute(
                text("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='reader_progress'")
            ).fetchall()
            legacy_names = {row[0] for row in legacy_indexes}
            for legacy_name in sorted(legacy_names):
                if legacy_name != "uq_reader_progress_user_paper" and "user_paper" not in legacy_name:
                    connection.execute(text(f"DROP INDEX IF EXISTS {legacy_name}"))

            connection.execute(text("DELETE FROM reader_progress WHERE user_id IS NULL"))
        except Exception:
            pass


def _ensure_paper_display_id_schema():
    with engine.begin() as connection:
        try:
            table_info = connection.execute(text("PRAGMA table_info(papers)")).fetchall()
            columns = {row[1] for row in table_info}

            if "display_id" not in columns:
                connection.execute(text("ALTER TABLE papers ADD COLUMN display_id VARCHAR(20)"))

            index_names = connection.execute(
                text("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='papers'")
            ).fetchall()
            index_names = {row[0] for row in index_names}

            if "idx_papers_display_id" not in index_names:
                connection.execute(
                    text("CREATE INDEX IF NOT EXISTS idx_papers_display_id ON papers (display_id)")
                )

            existing_null = connection.execute(
                text("SELECT id FROM papers WHERE display_id IS NULL ORDER BY created_at ASC, id ASC")
            ).fetchall()

            if existing_null:
                for idx, (paper_id,) in enumerate(existing_null, start=1):
                    display_id = f"RP-{idx:03d}"
                    connection.execute(
                        text("UPDATE papers SET display_id = :display_id WHERE id = :paper_id"),
                        {"display_id": display_id, "paper_id": paper_id},
                    )
        except Exception:
            pass


_ensure_library_schema()
_ensure_reader_progress_schema()
_ensure_paper_display_id_schema()

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()