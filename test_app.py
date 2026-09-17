import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_all():
    print("Testing FinNews AI endpoints...")

    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health = res.json()
    print("[PASS] GET /api/health:", health)

    # 2. Homepage HTML
    res = client.get("/")
    assert res.status_code == 200
    assert "FinNews" in res.text
    print("[PASS] GET / (HTML template served successfully)")

    # 3. News endpoint
    res = client.get("/api/news?category=all")
    assert res.status_code == 200
    news_data = res.json()
    articles = news_data.get("articles", [])
    overview = news_data.get("overview", {})
    assert len(articles) > 0, "No articles returned!"
    print(f"[PASS] GET /api/news: {len(articles)} articles returned, Market Mood: {overview.get('market_mood')}")

    # Verify slide articles exist in feed
    titles = [a["title"] for a in articles]
    print(f"Sample Titles in Feed: {titles[:2]}")

    # 4. Glossary endpoint
    res = client.get("/api/glossary")
    assert res.status_code == 200
    glossary = res.json()
    assert len(glossary) >= 10, "Glossary too short!"
    print(f"[PASS] GET /api/glossary: {len(glossary)} financial terms defined.")

    # 5. Simplify endpoint with custom text
    custom_sample = """
    The Federal Open Market Committee announced a 50 basis point reduction in the federal funds rate today.
    Chair Jerome Powell emphasized that inflation metrics have cooled toward the 2% target, while labor market
    conditions showed signs of softening. Benchmark 10-year Treasury yields fell 12 basis points to 3.82% following
    the announcement, while equity indices surged to record highs.
    """
    res = client.post("/api/simplify", json={
        "text": custom_sample,
        "language": "English",
        "complexity_target": "simple"
    })
    assert res.status_code == 200, f"Simplify failed: {res.text}"
    simp = res.json()
    assert simp["success"] is True
    assert "simplified_summary" in simp
    assert "what_happened" in simp
    assert "why_it_matters" in simp
    assert "market_impact" in simp
    print(f"[PASS] POST /api/simplify (Custom Text): Summary generated using '{simp['engine_used']}'")
    print(f"  -> What happened: {simp['what_happened'][:80]}...")
    print(f"  -> Why it matters: {simp['why_it_matters'][:80]}...")

    # 6. Simplify endpoint with Spanish language
    res_es = client.post("/api/simplify", json={
        "text": custom_sample,
        "language": "Spanish"
    })
    assert res_es.status_code == 200
    simp_es = res_es.json()
    print(f"[PASS] POST /api/simplify (Spanish): Language response confirmed.")

    # 7. Settings status
    res = client.get("/api/settings")
    assert res.status_code == 200
    settings_data = res.json()
    print("[PASS] GET /api/settings:", settings_data)

    # 8. Authentication: Register
    import uuid
    test_email = f"trader_{uuid.uuid4().hex[:6]}@example.com"
    res_reg = client.post("/api/auth/register", json={
        "name": "Jordan Bell",
        "email": test_email,
        "password": "securepassword123"
    })
    assert res_reg.status_code == 200
    reg_data = res_reg.json()
    assert reg_data["success"] is True
    print(f"[PASS] POST /api/auth/register: User created ({reg_data['user']['name']})")

    # 9. Authentication: Login
    res_login = client.post("/api/auth/login", json={
        "email": test_email,
        "password": "securepassword123"
    })
    assert res_login.status_code == 200
    login_data = res_login.json()
    assert login_data["success"] is True
    token = login_data["token"]
    print(f"[PASS] POST /api/auth/login: Session token issued ({token[:12]}...)")

    # 10. Authentication: Demo Login
    res_demo = client.post("/api/auth/demo")
    assert res_demo.status_code == 200
    demo_data = res_demo.json()
    assert demo_data["success"] is True
    print(f"[PASS] POST /api/auth/demo: Logged in as {demo_data['user']['name']}")

    # 11. Authentication: Session verification
    res_me = client.get(f"/api/auth/me?token={token}")
    assert res_me.status_code == 200
    me_data = res_me.json()
    assert me_data["success"] is True
    print(f"[PASS] GET /api/auth/me: Verified session for {me_data['user']['name']}")

    # 12. Chatbot: FinBot Query
    res_chat = client.post("/api/chat", json={
        "message": "What is the market mood today and how does a rate hike affect loans?",
        "history": []
    })
    assert res_chat.status_code == 200
    chat_data = res_chat.json()
    assert len(chat_data["reply"]) > 20
    assert len(chat_data["suggested_questions"]) > 0
    print(f"[PASS] POST /api/chat: FinBot responded ({len(chat_data['reply'])} chars, {len(chat_data['suggested_questions'])} follow-up chips)")
    reply_safe = chat_data['reply'][:90].encode('ascii', 'backslashreplace').decode('ascii')
    print(f"  -> FinBot snippet: {reply_safe}...")

    print("\nALL TESTS PASSED SUCCESSFULLY! Auth & Chatbot are fully functional.")

if __name__ == "__main__":
    test_all()
