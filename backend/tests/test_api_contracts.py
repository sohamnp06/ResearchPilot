import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_research_assistant.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("MAIL_USERNAME", "test@example.com")
os.environ.setdefault("MAIL_PASSWORD", "test-password")
os.environ.setdefault("MAIL_FROM", "test@example.com")

from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password
from app.database.database import Base, SessionLocal, engine
from app.database.models import Paper, User
from app.main import app


Base.metadata.create_all(bind=engine)
client = TestClient(app)


def seed_paper() -> str:
    paper_id = "paper-transformer-demo"
    db = SessionLocal()
    existing = db.query(Paper).filter(Paper.id == paper_id).first()
    if not existing:
        paper = Paper(
            id=paper_id,
            title="Attention Is All You Need",
            authors='["Ashish Vaswani", "Noam Shazeer"]',
            year=2017,
            source="arxiv",
            abstract="The Transformer architecture removes recurrence and convolutions.",
            pdf_url="https://example.com/transformer.pdf",
            citation_count=123,
            references=10,
            user_id=None,
            file_path="/tmp/transformer.pdf",
            status="published",
        )
        db.add(paper)
        db.commit()
    db.close()
    return paper_id


def test_search_returns_paper_results():
    seed_paper()

    response = client.get("/api/papers/search?q=transformer")

    assert response.status_code == 200, response.text
    payload = response.json()
    assert "papers" in payload
    assert len(payload["papers"]) >= 1
    first = payload["papers"][0]
    assert first["title"]
    assert first["source"]
    assert "authors" in first


def test_library_reader_and_notes_flow():
    paper_id = seed_paper()

    db = SessionLocal()
    existing_user = db.query(User).filter(User.email == "library-user@example.com").first()
    if not existing_user:
        user = User(
            username="library-user",
            email="library-user@example.com",
            password_hash=hash_password("StrongPass123!"),
            email_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user = existing_user
    db.close()

    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    upload_response = client.post(
        "/api/papers/upload",
        files={"file": ("demo.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")},
        headers=headers,
    )
    assert upload_response.status_code == 201, upload_response.text
    uploaded = upload_response.json()
    assert uploaded["id"]
    assert uploaded["pdfUrl"].endswith(".pdf")

    library_response = client.post("/api/library", json={"paper_id": paper_id}, headers=headers)
    assert library_response.status_code == 200, library_response.text
    assert library_response.json()["paper"]["id"] == paper_id

    list_response = client.get("/api/library", headers=headers)
    assert list_response.status_code == 200, list_response.text
    assert len(list_response.json()["papers"]) >= 1

    reader_response = client.post(
        "/api/reader/progress",
        json={"paper_id": paper_id, "current_page": 7},
        headers=headers,
    )
    assert reader_response.status_code == 200, reader_response.text
    assert reader_response.json()["current_page"] == 7

    current_reader = client.get("/api/reader", headers=headers)
    assert current_reader.status_code == 200, current_reader.text
    assert current_reader.json()["paper_id"] == paper_id

    notes_response = client.post(
        f"/api/papers/{paper_id}/notes",
        json={"title": "Important idea", "content": "This paper changes the architecture."},
        headers=headers,
    )
    assert notes_response.status_code == 201, notes_response.text
    note_id = notes_response.json()["id"]

    get_notes = client.get(f"/api/papers/{paper_id}/notes", headers=headers)
    assert get_notes.status_code == 200, get_notes.text
    assert len(get_notes.json()["notes"]) >= 1

    update_response = client.put(
        f"/api/papers/{paper_id}/notes",
        json={"id": note_id, "title": "Updated title", "content": "Updated content"},
        headers=headers,
    )
    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["title"] == "Updated title"


def test_delete_library_and_reader_entries():
    paper_id = seed_paper()

    db = SessionLocal()
    existing_user = db.query(User).filter(User.email == "delete-user@example.com").first()
    if not existing_user:
        user = User(
            username="delete-user",
            email="delete-user@example.com",
            password_hash=hash_password("StrongPass123!"),
            email_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user = existing_user
    db.close()

    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/library", json={"paper_id": paper_id}, headers=headers)
    client.post("/api/reader/progress", json={"paper_id": paper_id, "current_page": 6}, headers=headers)

    library_delete = client.delete(f"/api/library/{paper_id}", headers=headers)
    assert library_delete.status_code == 200, library_delete.text

    list_response = client.get("/api/library", headers=headers)
    assert list_response.status_code == 200, list_response.text
    assert all(item["id"] != paper_id for item in list_response.json()["papers"])

    reader_create = client.post("/api/reader/progress", json={"paper_id": paper_id, "current_page": 4}, headers=headers)
    assert reader_create.status_code == 200, reader_create.text

    reader_delete = client.delete(f"/api/reader/{paper_id}", headers=headers)
    assert reader_delete.status_code == 200, reader_delete.text

    reader_response = client.get("/api/reader", headers=headers)
    assert reader_response.status_code == 200, reader_response.text
    assert reader_response.json()["paper_id"] is None
