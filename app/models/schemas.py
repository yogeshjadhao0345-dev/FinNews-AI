from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class JargonItem(BaseModel):
    term: str
    definition: str
    in_text: Optional[str] = None

class NewsArticle(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    url_to_image: Optional[str] = None
    source: str = "Financial Wire"
    published_at: str = ""
    category: str = "all"
    sector: str = "Economy"
    reading_time_original_mins: int = 4
    is_simplified: bool = False
    simplified_summary: Optional[str] = None
    what_happened: Optional[str] = None
    why_it_matters: Optional[str] = None
    market_impact: Optional[str] = None
    key_takeaways: List[str] = Field(default_factory=list)
    sentiment: str = "neutral"  # bullish | bearish | neutral
    sentiment_score: float = 0.0 # -1.0 to 1.0
    reading_time_simplified_mins: int = 1
    jargon_terms: List[JargonItem] = Field(default_factory=list)

class SimplifyRequest(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None
    article_id: Optional[str] = None
    language: str = "English"
    complexity_target: str = "simple"  # simple, teen, executive

class SimplifyResponse(BaseModel):
    success: bool = True
    id: Optional[str] = None
    title: str
    original_text: str
    simplified_summary: str
    what_happened: str
    why_it_matters: str
    market_impact: str
    key_takeaways: List[str]
    sentiment: str
    sentiment_score: float
    sector: str
    reading_time_original_mins: int
    reading_time_simplified_mins: int
    reading_time_saved_percent: int
    jargon_terms: List[JargonItem]
    language: str
    engine_used: str

class GlossaryTerm(BaseModel):
    term: str
    definition: str
    example: str
    category: str

class SettingsUpdateRequest(BaseModel):
    news_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

class SettingsResponse(BaseModel):
    has_news_api: bool
    has_gemini_api: bool
    has_openai_api: bool
    news_api_masked: str
    gemini_api_masked: str
    openai_api_masked: str

class MarketOverview(BaseModel):
    total_articles: int
    bullish_count: int
    bearish_count: int
    neutral_count: int
    market_sentiment_score: float  # 0 to 100
    market_mood: str               # "Moderately Bullish", etc.
    top_sectors: List[Dict[str, Any]]

# Authentication Models
class UserRegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    initials: str
    role: str = "Retail Investor"

class AuthResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[UserProfile] = None

# Chatbot Models
class ChatMessage(BaseModel):
    sender: str  # "user" or "bot"
    text: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = Field(default_factory=list)
    current_article_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    suggested_questions: List[str] = Field(default_factory=list)
    relevant_terms: List[str] = Field(default_factory=list)
