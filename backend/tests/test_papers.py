from fastapi.testclient import TestClient

from app.main import app
from app.database.database import SessionLocal
from app.database.models import Paper, ReaderProgress, User
from app.core.security import hash_password

client = TestClient(app)


def _create_user(email="reader@example.com", username="readeruser"):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(username=username, email=email, password_hash=hash_password("Pass123!"), email_verified=True)
        db.add(user)
        db.commit()
        db.refresh(user)
    db.close()
    return user


def test_reader_history_returns_all_opened_papers():
    user = _create_user()
    db = SessionLocal()
    paper_a = db.query(Paper).filter(Paper.id == "paper-transformer-demo").first()
    paper_b = db.query(Paper).filter(Paper.id == "paper-bert-demo").first()
    if not paper_a:
        paper_a = Paper(id="paper-transformer-demo", title="Demo A", authors="[]", source="arxiv", abstract="", pdf_url="/demo-a.pdf", status="published", filename="demo-a.pdf")
        db.add(paper_a)
    if not paper_b:
        paper_b = Paper(id="paper-bert-demo", title="Demo B", authors="[]", source="arxiv", abstract="", pdf_url="/demo-b.pdf", status="published", filename="demo-b.pdf")
        db.add(paper_b)
    db.commit()
    db.refresh(paper_a)
    db.refresh(paper_b)

    db.query(ReaderProgress).filter(
        ReaderProgress.user_id == user.id,
        ReaderProgress.paper_id.in_([paper_a.id, paper_b.id]),
    ).delete(synchronize_session=False)
    db.add_all([
        ReaderProgress(paper_id=paper_a.id, user_id=user.id, current_page=1),
        ReaderProgress(paper_id=paper_b.id, user_id=user.id, current_page=2),
    ])
    db.commit()
    db.close()

    token = client.post("/auth/login", json={"email": user.email, "password": "Pass123!"}).json()["access_token"]
    response = client.get("/api/reader/history", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    ids = [item["id"] for item in response.json()["papers"]]
    assert "paper-transformer-demo" in ids
    assert "paper-bert-demo" in ids
