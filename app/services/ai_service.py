import json
import re
from typing import Dict, Any, List, Optional
import httpx
from app.config import settings
from app.models.schemas import SimplifyResponse, JargonItem
from app.services.glossary_service import GlossaryService
from app.services.sentiment_service import SentimentService
from app.services.translation_service import TranslationService

class AIService:
    @staticmethod
    def _estimate_reading_time(text: str) -> int:
        words = len(re.findall(r'\w+', text or ""))
        return max(1, round(words / 200))

    @staticmethod
    async def simplify_text(
        text: str,
        title: str = "Financial News Article",
        language: str = "English",
        complexity: str = "simple"
    ) -> SimplifyResponse:
        original_mins = AIService._estimate_reading_time(text)
        detected_jargon = GlossaryService.find_jargon_in_text(text)
        sentiment_data = SentimentService.analyze(text)

        # 1. Try Google Gemini API if configured
        if settings.has_gemini_api:
            try:
                res = await AIService._call_gemini(text, title, language, complexity)
                if res:
                    res["engine_used"] = "Google Gemini 3.6 Flash"
                    return AIService._format_response(res, text, title, original_mins, detected_jargon, language)
            except Exception as e:
                print(f"[AI Service] Gemini call failed: {e}. Falling back...")

        # 2. Try OpenAI API if configured
        if settings.has_openai_api:
            try:
                res = await AIService._call_openai(text, title, language, complexity)
                if res:
                    res["engine_used"] = "OpenAI GPT-4o-mini"
                    return AIService._format_response(res, text, title, original_mins, detected_jargon, language)
            except Exception as e:
                print(f"[AI Service] OpenAI call failed: {e}. Falling back...")

        # 3. Fallback: Offline Intelligent Heuristic Simplifier
        res = await AIService._offline_simplify(text, title, language, sentiment_data, detected_jargon)
        res["engine_used"] = "FinNews Heuristic AI Engine (Offline Ready)"
        return AIService._format_response(res, text, title, original_mins, detected_jargon, language)

    @staticmethod
    async def _call_gemini(text: str, title: str, language: str, complexity: str) -> Optional[Dict[str, Any]]:
        prompt = f"""
You are FinNews AI, a world-class financial communicator.
Your task is to transform complex financial news with heavy industry jargon into simple, crystal-clear insights that anyone (students, retail investors, everyday people) can instantly understand.

Target Language: {language}
Reading Complexity: {complexity} (Keep sentences concise, explain financial acronyms in plain English, and preserve factual numbers and dates).

Article Title: {title}
Article Content:
{text}

Respond ONLY with a valid JSON object strictly matching this schema:
{{
  "title": "Clear simplified headline",
  "simplified_summary": "A 2 to 3 sentence plain-language summary explaining what this means without confusing jargon.",
  "what_happened": "1-2 sentences on the exact core news event.",
  "why_it_matters": "Why an everyday person or retail investor should care.",
  "market_impact": "Direct impact on stocks, interest rates, currency, or crypto.",
  "key_takeaways": [
    "First crucial bullet point with key facts/numbers",
    "Second crucial bullet point with key facts/numbers",
    "Third actionable takeaway"
  ],
  "sentiment": "bullish" | "bearish" | "neutral",
  "sentiment_score": float between -1.0 and 1.0,
  "sector": "Tech & AI" | "Economy & Fed" | "Crypto & Web3" | "Banking & Finance" | "Energy & Commodities" | "Automotive & Retail"
}}
"""
        candidate_models = ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-flash-latest"]
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            for model_name in candidate_models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={settings.gemini_api_key}"
                try:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        text_out = data["candidates"][0]["content"]["parts"][0]["text"]
                        res_obj = json.loads(text_out)
                        res_obj["engine_used"] = f"Google Gemini ({model_name})"
                        return res_obj
                except Exception as ex:
                    continue
        return None

    @staticmethod
    async def _call_openai(text: str, title: str, language: str, complexity: str) -> Optional[Dict[str, Any]]:
        prompt = f"""
You are FinNews AI. Simplify this financial news into plain {language} for everyday readers.
Title: {title}
Content: {text}
Output valid JSON only with keys: title, simplified_summary, what_happened, why_it_matters, market_impact, key_takeaways (array of 3 strings), sentiment, sentiment_score, sector.
"""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
        return None

    @staticmethod
    async def _offline_simplify(
        text: str,
        title: str,
        language: str,
        sentiment_data: Dict[str, Any],
        detected_jargon: List[JargonItem]
    ) -> Dict[str, Any]:
        # Split sentences cleanly
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 20]
        
        core_sentence = sentences[0] if sentences else text[:150]
        second_sentence = sentences[1] if len(sentences) > 1 else ""

        # Plain language replacements
        plain_core = core_sentence
        for j in detected_jargon:
            pattern = re.compile(re.escape(j.term), re.IGNORECASE)
            plain_core = pattern.sub(f"{j.term} (i.e., {j.definition.split('.')[0].lower()})", plain_core)

        # Multilingual prefix support for fallback
        prefix_map = {
            "Spanish": "Resumen Simplificado: ",
            "Hindi": "सरल वित्तीय सारांश: ",
            "French": "Résumé Simplifié: ",
            "German": "Vereinfachte Zusammenfassung: ",
            "English": "Simplified Overview: "
        }
        prefix = prefix_map.get(language, "Simplified Overview: ")

        simplified_summary = (
            f"{prefix}{core_sentence} In simple terms, this event directly impacts market borrowing costs, "
            f"corporate earnings expectations, and general consumer confidence."
        )

        what_happened = f"{core_sentence} {second_sentence}".strip()
        why_it_matters = (
            "When interest rates, company earnings, or market valuations shift, it trickles down to personal finances "
            "— including loan rates, 401(k)/retirement portfolio returns, and job security across the sector."
        )
        
        impact_label = sentiment_data["label"]
        market_impact = (
            f"Current trend leans {impact_label.upper()}. Investors are actively adjusting asset allocations, "
            f"closely monitoring upcoming inflation and central bank announcements for directional momentum."
        )

        takeaways = [
            f"Core Development: {core_sentence[:120]}...",
            f"Primary Sector Affected: {sentiment_data['sector']} with a {impact_label.lower()} market stance.",
            f"Key Financial Concept: {detected_jargon[0].term + ' - ' + detected_jargon[0].definition if detected_jargon else 'Market sentiment remains sensitive to economic data releases.'}"
        ]

        result_data = {
            "title": f"Simplified: {title}",
            "simplified_summary": simplified_summary,
            "what_happened": what_happened,
            "why_it_matters": why_it_matters,
            "market_impact": market_impact,
            "key_takeaways": takeaways,
            "sentiment": sentiment_data["sentiment"],
            "sentiment_score": sentiment_data["score"],
            "sector": sentiment_data["sector"]
        }

        target_norm = language.strip().lower()
        if target_norm not in ("english", "en"):
            result_data = await TranslationService.translate_article_data(result_data, language)

        return result_data

    @staticmethod
    def _format_response(
        raw: Dict[str, Any],
        original_text: str,
        title: str,
        original_mins: int,
        jargon_items: List[JargonItem],
        language: str
    ) -> SimplifyResponse:
        summary_text = raw.get("simplified_summary", "")
        simplified_mins = max(1, AIService._estimate_reading_time(summary_text))
        saved_percent = max(0, int(((original_mins - simplified_mins) / max(1, original_mins)) * 100))
        if original_mins <= 1:
            saved_percent = 50

        return SimplifyResponse(
            success=True,
            title=raw.get("title", title),
            original_text=original_text,
            simplified_summary=summary_text,
            what_happened=raw.get("what_happened", "Data updated."),
            why_it_matters=raw.get("why_it_matters", "Direct economic relevance."),
            market_impact=raw.get("market_impact", "Financial index movement."),
            key_takeaways=raw.get("key_takeaways", []),
            sentiment=raw.get("sentiment", "neutral"),
            sentiment_score=float(raw.get("sentiment_score", 0.0)),
            sector=raw.get("sector", "Economy"),
            reading_time_original_mins=original_mins,
            reading_time_simplified_mins=simplified_mins,
            reading_time_saved_percent=saved_percent,
            jargon_terms=jargon_items,
            language=language,
            engine_used=raw.get("engine_used", "FinNews AI Engine")
        )
