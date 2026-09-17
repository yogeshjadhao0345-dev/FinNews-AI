import os
import re
import asyncio
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx

from app.config import settings
from app.models.schemas import (
    NewsArticle, SimplifyRequest, SimplifyResponse, GlossaryTerm,
    SettingsUpdateRequest, SettingsResponse, MarketOverview,
    UserRegisterRequest, UserLoginRequest, AuthResponse, UserProfile,
    ChatRequest, ChatResponse
)
from app.services.news_service import NewsService
from app.services.ai_service import AIService
from app.services.glossary_service import GlossaryService
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService

app = FastAPI(
    title="FinNews AI - Financial News Simplifier",
    description="Transforms complex financial news into simple, actionable insights using AI.",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent.parent

# Mount Static Files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "app": "FinNews AI",
        "version": "1.0.0",
        "has_news_api": settings.has_news_api,
        "has_gemini_api": settings.has_gemini_api,
        "has_openai_api": settings.has_openai_api
    }

@app.get("/api/news")
async def get_news(
    category: str = Query("all", description="Category filter: all, fed_macro, tech_stocks, crypto, commodities, banking"),
    q: Optional[str] = Query(None, description="Search query"),
    lang: str = Query("English", description="Target language: English, Hindi, Spanish, French, German")
):
    articles = await NewsService.get_articles(category=category, query=q, language=lang)
    overview = NewsService.get_market_overview(articles, language=lang)
    return {
        "articles": articles,
        "overview": overview,
        "count": len(articles),
        "language": lang
    }

@app.post("/api/simplify", response_model=SimplifyResponse)
async def simplify_article(payload: SimplifyRequest):
    text_to_simplify = ""
    title = "Financial News Analysis"

    if payload.article_id:
        articles = await NewsService.get_articles()
        matched = next((a for a in articles if a.id == payload.article_id), None)
        if matched:
            text_to_simplify = f"{matched.title}. {matched.description or ''} {matched.content or ''}"
            title = matched.title
        else:
            raise HTTPException(status_code=404, detail="Article ID not found.")
    elif payload.text and len(payload.text.strip()) > 10:
        text_to_simplify = payload.text.strip()
        title = text_to_simplify[:60] + "..." if len(text_to_simplify) > 60 else text_to_simplify
    else:
        raise HTTPException(status_code=400, detail="Please provide article_id or article text to simplify.")

    response = await AIService.simplify_text(
        text=text_to_simplify,
        title=title,
        language=payload.language,
        complexity=payload.complexity_target
    )
    return response

def chunk_text_for_tts(text: str, max_len: int = 80) -> List[str]:
    clean = re.sub(r'\s+', ' ', text).strip()
    if not clean:
        return []
    if len(clean) <= max_len:
        return [clean]

    # Split on sentence enders and punctuation (Hindi/Marathi danda ।, periods, commas, questions, exclamations)
    sentences = re.split(r'([।\.!\?;\,\n]+)', clean)
    tokens = []
    for i in range(0, len(sentences) - 1, 2):
        tokens.append(sentences[i] + sentences[i+1])
    if len(sentences) % 2 == 1 and sentences[-1]:
        tokens.append(sentences[-1])

    chunks = []
    current_chunk = ""
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        if len(token) > max_len:
            words = token.split(" ")
            for w in words:
                if not w:
                    continue
                if len(current_chunk) + len(w) + 1 <= max_len:
                    current_chunk = f"{current_chunk} {w}".strip()
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = w
        elif len(current_chunk) + len(token) + 1 <= max_len:
            current_chunk = f"{current_chunk} {token}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = token

    if current_chunk:
        chunks.append(current_chunk)
    return chunks

@app.get("/api/tts")
async def text_to_speech(
    text: str = Query(..., description="Text to synthesize"),
    lang: str = Query("hi", description="Language code (e.g. hi, mr, en, es, fr, de)")
):
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    clean_text = text.strip()[:800]
    chunks = chunk_text_for_tts(clean_text, max_len=80)
    if not chunks:
        raise HTTPException(status_code=400, detail="No speakable text found.")

    tts_url = "https://translate.google.com/translate_tts"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            async def fetch_chunk(chunk_str: str) -> bytes:
                params = {
                    "ie": "UTF-8",
                    "client": "tw-ob",
                    "tl": lang,
                    "q": chunk_str
                }
                r = await client.get(tts_url, params=params, headers=headers)
                if r.status_code == 200:
                    return r.content
                return b""

            audio_pieces = await asyncio.gather(*(fetch_chunk(c) for c in chunks))
            combined_mp3 = b"".join(audio_pieces)

            if combined_mp3:
                return Response(
                    content=combined_mp3,
                    media_type="audio/mpeg",
                    headers={
                        "Accept-Ranges": "bytes",
                        "Content-Length": str(len(combined_mp3)),
                        "Cache-Control": "public, max-age=86400"
                    }
                )
    except Exception as e:
        print(f"[TTS Error] {e}")

    raise HTTPException(status_code=500, detail="TTS audio generation failed.")

@app.get("/api/glossary", response_model=List[GlossaryTerm])
async def get_glossary():
    return GlossaryService.get_all_terms()

@app.get("/api/settings", response_model=SettingsResponse)
async def get_settings():
    def mask_key(k: str) -> str:
        if not k or len(k) < 6:
            return ""
        return k[:3] + "•" * (len(k) - 6) + k[-3:]

    return SettingsResponse(
        has_news_api=settings.has_news_api,
        has_gemini_api=settings.has_gemini_api,
        has_openai_api=settings.has_openai_api,
        news_api_masked=mask_key(settings.news_api_key),
        gemini_api_masked=mask_key(settings.gemini_api_key),
        openai_api_masked=mask_key(settings.openai_api_key)
    )

@app.post("/api/settings", response_model=SettingsResponse)
async def update_settings(payload: SettingsUpdateRequest):
    settings.update_keys(
        news_api_key=payload.news_api_key,
        gemini_api_key=payload.gemini_api_key,
        openai_api_key=payload.openai_api_key
    )
    return await get_settings()

# Authentication Endpoints
@app.post("/api/auth/register", response_model=AuthResponse)
async def register(payload: UserRegisterRequest):
    success, msg, profile, token = AuthService.register(payload.name, payload.email, payload.password)
    if not success:
        return AuthResponse(success=False, message=msg)
    return AuthResponse(success=True, message=msg, token=token, user=profile)

@app.post("/api/auth/login", response_model=AuthResponse)
async def login(payload: UserLoginRequest):
    success, msg, profile, token = AuthService.login(payload.email, payload.password)
    if not success:
        return AuthResponse(success=False, message=msg)
    return AuthResponse(success=True, message=msg, token=token, user=profile)

@app.post("/api/auth/demo", response_model=AuthResponse)
async def demo_login():
    profile, token = AuthService.demo_login()
    return AuthResponse(success=True, message="Logged in as Demo Investor!", token=token, user=profile)

@app.get("/api/auth/me", response_model=AuthResponse)
async def get_current_user(token: Optional[str] = Query(None)):
    if not token:
        return AuthResponse(success=False, message="No session token provided.")
    profile = AuthService.verify_token(token)
    if not profile:
        return AuthResponse(success=False, message="Session expired or invalid.")
    return AuthResponse(success=True, message="Session active", user=profile, token=token)

# FinBot Personal Chatbot Endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_finbot(payload: ChatRequest):
    response = await ChatService.process_chat(
        user_message=payload.message,
        history=payload.history,
        current_article_id=payload.current_article_id
    )
    return response
