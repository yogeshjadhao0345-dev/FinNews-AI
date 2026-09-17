import re
import datetime
from typing import List, Dict, Any, Optional, Tuple
import httpx
from app.config import settings
from app.models.schemas import ChatMessage, ChatResponse
from app.services.glossary_service import GlossaryService, GLOSSARY_DATABASE
from app.services.news_service import NewsService

FINBOT_SYSTEM_PROMPT = """
You are FinBot, the friendly, world-class personal financial assistant embedded inside FinNews AI.
Your purpose is to answer financial queries rapidly, accurately, and in plain, accessible language that anyone (from beginner retail investors to students) can grasp immediately.

Guidelines:
1. Be concise, direct, and encouraging.
2. If financial jargon is mentioned, explain it simply.
3. Keep answers structured (use bullet points and bold highlights).
4. Emphasize education and clarity over dense speculation.
5. Provide helpful follow-up suggestions at the end.
"""

class ChatService:
    @classmethod
    async def process_chat(
        cls,
        user_message: str,
        history: List[ChatMessage],
        current_article_id: Optional[str] = None
    ) -> ChatResponse:
        clean_msg = user_message.strip()
        if not clean_msg:
            return ChatResponse(
                reply="Hello! I am FinBot, your personal financial assistant. Ask me anything about today's market news, complex terminology, or economic trends!",
                suggested_questions=["What is today's market sentiment?", "Explain Fed rate hikes simply", "What is EBITDA?"]
            )

        # 1. Gather context from current news & market
        articles = await NewsService.get_articles()
        overview = NewsService.get_market_overview(articles)
        
        context_str = f"Current Market Mood: {overview.market_mood} ({overview.market_sentiment_score}/100).\n"
        context_str += f"Total active headlines: {overview.total_articles} (Bullish: {overview.bullish_count}, Bearish: {overview.bearish_count}).\n"
        context_str += "Recent Headlines:\n"
        for a in articles[:3]:
            context_str += f"- {a.title} ({a.sentiment.upper()})\n"

        # 2. Check if user supplies Gemini API key
        if settings.has_gemini_api:
            try:
                ai_reply = await cls._ask_gemini(clean_msg, context_str, history)
                if ai_reply:
                    return ai_reply
            except Exception as e:
                print(f"[ChatService] Gemini error: {e}. Using offline engine.")

        # 3. Check if user supplies OpenAI API key
        if settings.has_openai_api:
            try:
                ai_reply = await cls._ask_openai(clean_msg, context_str, history)
                if ai_reply:
                    return ai_reply
            except Exception as e:
                print(f"[ChatService] OpenAI error: {e}. Using offline engine.")

        # 4. Context-Aware Knowledge Engine (Offline Fallback)
        return cls._offline_answer(clean_msg, overview, articles, current_article_id)

    _cached_working_model: Optional[str] = None

    @classmethod
    async def _ask_gemini(cls, message: str, context: str, history: List[ChatMessage]) -> Optional[ChatResponse]:
        candidate_models = ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-flash-latest"]
        if cls._cached_working_model and cls._cached_working_model in candidate_models:
            models_to_try = [cls._cached_working_model] + [m for m in candidate_models if m != cls._cached_working_model]
        else:
            models_to_try = candidate_models

        history_text = "\n".join([f"{m.sender.upper()}: {m.text}" for m in history[-4:]])
        prompt = f"""
{FINBOT_SYSTEM_PROMPT}

LIVE MARKET CONTEXT:
{context}

CONVERSATION HISTORY:
{history_text}

USER QUERY:
{message}

Please respond concisely in clear markdown. Provide 3 short suggested follow-up questions at the very end formatted as:
FOLLOW_UPS:
- Question 1
- Question 2
- Question 3
"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3}
        }

        async with httpx.AsyncClient(timeout=12.0) as client:
            for model_name in models_to_try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={settings.gemini_api_key}"
                try:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        cls._cached_working_model = model_name
                        data = resp.json()
                        full_text = data["candidates"][0]["content"]["parts"][0]["text"]
                        reply_body, suggestions = cls._extract_followups(full_text)
                        return ChatResponse(
                            reply=reply_body,
                            suggested_questions=suggestions,
                            relevant_terms=[]
                        )
                except Exception as ex:
                    continue
        return None

    @classmethod
    async def _ask_openai(cls, message: str, context: str, history: List[ChatMessage]) -> Optional[ChatResponse]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        
        messages = [{"role": "system", "content": f"{FINBOT_SYSTEM_PROMPT}\nMarket Context:\n{context}"}]
        for m in history[-4:]:
            role = "user" if m.sender == "user" else "assistant"
            messages.append({"role": role, "content": m.text})
        messages.append({"role": "user", "content": message})

        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "temperature": 0.3
        }

        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                full_text = data["choices"][0]["message"]["content"]
                reply_body, suggestions = cls._extract_followups(full_text)
                return ChatResponse(
                    reply=reply_body,
                    suggested_questions=suggestions,
                    relevant_terms=[]
                )
        return None

    @classmethod
    def _extract_followups(cls, text: str) -> Tuple[str, List[str]]:
        if "FOLLOW_UPS:" in text:
            parts = text.split("FOLLOW_UPS:")
            main_reply = parts[0].strip()
            lines = [l.strip().lstrip("-*• ") for l in parts[1].split("\n") if l.strip()]
            return main_reply, lines[:3]
        return text.strip(), ["Tell me more about this", "How does this affect my portfolio?", "What's the next market catalyst?"]

    @classmethod
    def _offline_answer(
        cls,
        query: str,
        overview: Any,
        articles: List[Any],
        current_article_id: Optional[str] = None
    ) -> ChatResponse:
        low = query.lower().strip()

        # =====================================================================
        # 1. ACCURATE REAL-TIME DATE, TIME & MARKET HOURS
        # =====================================================================
        is_date_query = any(w in low for w in [
            "today's date", "todays date", "today date", "what is today", 
            "what day is it", "what day is today", "current date", 
            "what is the date", "what date is it", "tell me the date"
        ])
        is_time_query = any(w in low for w in [
            "what time is it", "current time", "market hours", "is market open", 
            "is the market open", "trading hours", "when does market open", 
            "when does market close", "trading session"
        ])

        if is_date_query or is_time_query:
            now = datetime.datetime.now()
            date_str = now.strftime("%A, %B %d, %Y")
            time_str = now.strftime("%I:%M %p")
            
            # Trading sessions logic
            weekday = now.weekday() # 0 = Monday, 6 = Sunday
            is_weekday = weekday < 5

            reply = (
                f"### 📅 **Today's Date & Market Status**\n\n"
                f"• **Today's Date**: **{date_str}**\n"
                f"• **Current Local Time**: **{time_str}**\n\n"
                f"#### 🏛️ **Global Financial Trading Sessions**:\n"
                f"- 🇺🇸 **US Markets (NYSE / NASDAQ)**: 9:30 AM – 4:00 PM Eastern Time (Mon–Fri) "
                f"[{'Active Trading Day' if is_weekday else 'Weekend - Closed'}]\n"
                f"- 🇮🇳 **Indian Markets (NSE / BSE)**: 9:15 AM – 3:30 PM IST (Mon–Fri) "
                f"[{'Active Trading Day' if is_weekday else 'Weekend - Closed'}]\n"
                f"- 🪙 **Crypto Markets (Bitcoin / Ethereum)**: **Open 24/7/365** (Always Active)\n\n"
                f"📊 **Current Live Market Sentiment**: **{overview.market_mood}** "
                f"({overview.market_sentiment_score}/100) across {overview.total_articles} active headlines."
            )
            return ChatResponse(
                reply=reply,
                suggested_questions=[
                    "What is today's market sentiment?",
                    "Show today's top financial headlines",
                    "Why are markets moving today?"
                ],
                relevant_terms=["Trading Hours", "Market Mood"]
            )

        # =====================================================================
        # 2. GREETINGS, BOT IDENTITY & CAPABILITIES
        # =====================================================================
        is_greeting = any(w in low for w in [
            "hello", "hi finbot", "hey finbot", "good morning", "good afternoon", 
            "good evening", "who are you", "what can you do", "what is your name", 
            "who made you", "help me", "how are you"
        ]) or low in ["hi", "hey", "hello", "help", "yo", "sup"]

        if is_greeting:
            reply = (
                "### 🤖 **Hello! I am FinBot, your Personal Financial AI**\n\n"
                "I am designed to make financial intelligence, market news, and investing concepts clear and accessible for everyone.\n\n"
                "Here is what I can help you with:\n"
                "• 📰 **Live News Simplification**: Break down today's breaking financial headlines into plain language.\n"
                "• 💡 **Financial Glossary**: Define 100+ terms (EBITDA, P/E Ratio, Repo Rate, CPI, Bull/Bear market, etc.).\n"
                "• ⚖️ **Instrument Comparisons**: Explain differences like *Stocks vs Bonds*, *ETFs vs Mutual Funds*, or *Bitcoin vs Gold*.\n"
                "• 🧮 **Financial Formulas & Rules**: Explain the Rule of 72, Compounding math, SIP investing, and 50/30/20 budgeting.\n"
                "• 📊 **Market Mood & Sentiment**: Analyze whether current markets are bullish, bearish, or neutral.\n\n"
                "Feel free to ask any question—from beginner basics to complex macroeconomics!"
            )
            return ChatResponse(
                reply=reply,
                suggested_questions=[
                    "What is today's market sentiment?",
                    "Explain the difference between stocks and bonds",
                    "How does compound interest work?"
                ],
                relevant_terms=["FinBot", "Financial Literacy"]
            )

        # =====================================================================
        # 3. DIRECT FINANCIAL COMPARISONS ("X vs Y" or "Difference between X and Y")
        # =====================================================================
        if any(kw in low for kw in [" vs ", " versus ", "difference between", "compare "]):
            # Stocks vs Bonds
            if ("stock" in low or "equit" in low) and "bond" in low:
                reply = (
                    "### ⚖️ **Stocks vs. Bonds: Key Differences**\n\n"
                    "| Feature | Stocks (Equities) | Bonds (Fixed Income) |\n"
                    "| :--- | :--- | :--- |\n"
                    "| **What you are** | Part-owner of the company | Lender to the company/government |\n"
                    "| **Return Source** | Share price growth + Dividends | Regular coupon interest payments |\n"
                    "| **Risk Profile** | Higher (prices fluctuate daily) | Lower (guaranteed return if held to maturity) |\n"
                    "| **Bankruptcy Order** | Last in line (residual claimant) | Paid before equity holders |\n"
                    "| **Primary Goal** | Long-term capital growth | Capital preservation & steady income |\n\n"
                    "**Rule of Thumb**: Younger investors usually hold more stocks for growth, while retirees hold more bonds for stability."
                )
                return ChatResponse(
                    reply=reply,
                    suggested_questions=[
                        "What is Treasury yield?",
                        "How do interest rates affect bond prices?",
                        "What is an Index Fund?"
                    ],
                    relevant_terms=["Stocks", "Bonds", "Asset Allocation"]
                )

            # ETF vs Mutual Fund
            if "etf" in low and ("mutual fund" in low or "fund" in low):
                reply = (
                    "### ⚖️ **ETFs vs. Mutual Funds**\n\n"
                    "| Feature | ETF (Exchange-Traded Fund) | Mutual Fund |\n"
                    "| :--- | :--- | :--- |\n"
                    "| **Trading Time** | Trades throughout the day like a stock | Trades once daily after market close (NAV) |\n"
                    "| **Expense Ratio** | Ultra-low (often 0.03% – 0.20%) | Often higher (0.50% – 1.50%+) |\n"
                    "| **Minimum Investment** | Price of 1 single share | Often has minimum initial deposit (e.g. $500+) |\n"
                    "| **Management** | Mostly passive index tracking | Can be active or passive |\n\n"
                    "**Smart Takeaway**: For most retail investors, low-cost broad index ETFs or index mutual funds offer the best path to long-term wealth."
                )
                return ChatResponse(
                    reply=reply,
                    suggested_questions=[
                        "What is Dollar-Cost Averaging (DCA)?",
                        "What is the S&P 500 ETF?",
                        "How to start investing with small money?"
                    ],
                    relevant_terms=["ETF", "Mutual Fund", "Index Fund"]
                )

            # Bitcoin vs Gold
            if ("bitcoin" in low or "btc" in low or "crypto" in low) and "gold" in low:
                reply = (
                    "### ⚖️ **Bitcoin vs. Physical Gold**\n\n"
                    "| Feature | Bitcoin ('Digital Gold') | Physical Gold |\n"
                    "| :--- | :--- | :--- |\n"
                    "| **Track Record** | 15+ years (since 2009) | 5,000+ years of monetary history |\n"
                    "| **Supply Limit** | Hard cap at exactly 21,000,000 BTC | Increases ~1.5% annually through mining |\n"
                    "| **Portability** | Sent worldwide in minutes via private key | Heavy and expensive to transport/store |\n"
                    "| **Volatility** | Very high (20–40% swings common) | Low-to-moderate (steady safe-haven asset) |\n"
                    "| **Central Bank Reserves**| Growing institutional adoption | Held in massive quantity by sovereign central banks |\n\n"
                    "**Summary**: Gold remains the established global store of value; Bitcoin offers asymmetric digital scarcity with higher volatility."
                )
                return ChatResponse(
                    reply=reply,
                    suggested_questions=[
                        "What is Bitcoin Halving?",
                        "Why do central banks buy gold?",
                        "What is inflation hedging?"
                    ],
                    relevant_terms=["Bitcoin", "Gold", "Safe Haven"]
                )

            # SIP vs Lump Sum
            if "sip" in low and ("lump" in low or "one time" in low):
                reply = (
                    "### ⚖️ **SIP vs. Lump Sum Investing**\n\n"
                    "• **SIP (Systematic Investment Plan)**: Investing fixed sums at regular intervals (e.g. $200/month). Removes emotion, averages purchase costs, and prevents buying right at market tops.\n"
                    "• **Lump Sum**: Investing a large pool of capital all at once. Historically generates higher returns if markets rise immediately, but carries the emotional risk of buying before a sudden correction.\n\n"
                    "**Recommendation**: If investing from monthly income, use SIP. If you receive a windfall (bonus/inheritance), spread it over 6–12 months via systematic installments."
                )
                return ChatResponse(
                    reply=reply,
                    suggested_questions=[
                        "How does Dollar Cost Averaging work?",
                        "How much should I invest every month?",
                        "What is compound interest?"
                    ],
                    relevant_terms=["SIP", "Lump Sum", "Compounding"]
                )

            # APR vs APY
            if "apr" in low and "apy" in low:
                reply = (
                    "### ⚖️ **APR vs. APY: What's the Difference?**\n\n"
                    "• **APR (Annual Percentage Rate)**: The simple annual interest rate charged on borrowing (loans, credit cards), *without* compounding.\n"
                    "• **APY (Annual Percentage Yield)**: The true annual return on savings or investments, *including* the effect of compounding.\n\n"
                    "**Rule to Remember**:\n"
                    "- When **borrowing**, look at **APR** (you want it as low as possible).\n"
                    "- When **saving or investing**, look at **APY** (you want it as high as possible)!"
                )
                return ChatResponse(
                    reply=reply,
                    suggested_questions=[
                        "What is high-yield savings account (HYSA)?",
                        "How do credit card interest rates work?",
                        "What is compound interest?"
                    ],
                    relevant_terms=["APR", "APY", "Compounding"]
                )

            # Bulls vs Bears
            if ("bull" in low or "bullish" in low) and ("bear" in low or "bearish" in low):
                reply = (
                    "### ⚖️ **Bull Market vs. Bear Market**\n\n"
                    "• **Bull Market (📈)**: Prices are rising, the economy is expanding, corporate earnings are growing, and investors feel confident. (Named after the bull charging upwards with its horns).\n"
                    "• **Bear Market (📉)**: Prices decline by 20% or more from recent peaks, accompanied by widespread fear, economic slowdown, and corporate caution. (Named after the bear swiping downward with its paws).\n\n"
                    "**Smart Insight**: Bear markets feel painful, but historically they have been the greatest wealth-building buying opportunities for long-term investors."
                )
                return ChatResponse(
                    reply=reply,
                    suggested_questions=[
                        "What is today's market sentiment?",
                        "What triggers a market crash?",
                        "How to invest during a bear market?"
                    ],
                    relevant_terms=["Bull Market", "Bear Market", "Sentiment"]
                )

        # =====================================================================
        # 4. FINANCIAL FORMULAS & MATHEMATICAL SHORTCUTS
        # =====================================================================
        if "rule of 72" in low:
            # Check if user mentioned a specific percentage
            rate_match = re.search(r'(\d+(?:\.\d+)?)\s*%', low) or re.search(r'for\s*(\d+(?:\.\d+)?)', low)
            rate_val = float(rate_match.group(1)) if rate_match else 8.0
            years_to_double = round(72 / rate_val, 1) if rate_val > 0 else 0

            reply = (
                f"### 🧮 **The Rule of 72 Explained**\n\n"
                f"The **Rule of 72** is a famous mental math shortcut used by investors to estimate how many years it will take for your money to double at a given annual rate of return.\n\n"
                f"📌 **Formula**: \\( \\text{{Years to Double}} = \\frac{{72}}{{\\text{{Annual Return Rate}}}} \\)\n\n"
                f"**Calculation for {rate_val}% Return**:\n"
                f"- \\( 72 / {rate_val} = \\mathbf{{{years_to_double}\\text{{ years}}}} \\)\n"
                f"- An investment of $10,000 will grow to **$20,000** in approx **{years_to_double} years**!\n\n"
                f"**Quick Reference Benchmarks**:\n"
                f"• At **6%** (conservative fixed income): Doubles in **12 years**\n"
                f"• At **8%** (balanced portfolio): Doubles in **9 years**\n"
                f"• At **10%** (historical index equity average): Doubles in **7.2 years**\n"
                f"• At **12%** (high-growth aggressive equity): Doubles in **6 years**"
            )
            return ChatResponse(
                reply=reply,
                suggested_questions=[
                    "How does compound interest work?",
                    "What is Dollar-Cost Averaging (DCA)?",
                    "What is an Index Fund?"
                ],
                relevant_terms=["Rule of 72", "Compounding"]
            )

        if any(w in low for w in ["compound interest", "compounding", "calculate compounding"]):
            reply = (
                "### 📈 **The Power of Compound Interest**\n\n"
                "**Compounding** is what happens when you earn interest not only on your principal deposit, but also on the accumulated interest from prior years.\n\n"
                "📌 **Mathematical Formula**: \\( A = P \\left(1 + \\frac{r}{n}\\right)^{nt} \\)\n"
                "- \\( A \\) = Final accumulated amount\n"
                "- \\( P \\) = Initial principal investment\n"
                "- \\( r \\) = Annual interest rate (decimal)\n"
                "- \\( n \\) = Number of times interest compounds per year\n"
                "- \\( t \\) = Number of years\n\n"
                "**Real-World Example**:\n"
                "If you invest **$10,000** at an **8% annual return** for **25 years** without adding another penny:\n"
                "• Your money grows into **$68,485**! (Over $58,000 of pure profit earned simply by letting compounding work)."
            )
            return ChatResponse(
                reply=reply,
                suggested_questions=[
                    "What is the Rule of 72?",
                    "How does inflation erode cash savings?",
                    "What is Dollar-Cost Averaging (DCA)?"
                ],
                relevant_terms=["Compounding", "Interest"]
            )

        if "50/30/20" in low or "budget rule" in low:
            reply = (
                "### 📊 **The 50/30/20 Budgeting Rule**\n\n"
                "Created by financial experts, this popular guideline allocates your monthly after-tax income into 3 clean buckets:\n\n"
                "1. **50% for Needs**: Essential living costs you cannot avoid (rent/mortgage, groceries, utilities, basic transportation, minimum debt payments).\n"
                "2. **30% for Wants**: Lifestyle choices that make life enjoyable (dining out, entertainment, vacations, hobbies, shopping).\n"
                "3. **20% for Savings & Debt Acceleration**: Building an emergency fund, investing for retirement (index funds, 401k/IRA/SIP), and paying down high-interest credit card debt."
            )
            return ChatResponse(
                reply=reply,
                suggested_questions=[
                    "How large should my emergency fund be?",
                    "How to start investing as a beginner?",
                    "What is Dollar-Cost Averaging?"
                ],
                relevant_terms=["Budgeting", "Personal Finance"]
            )

        # =====================================================================
        # 5. GLOSSARY TERM DEFINITIONS (Comprehensive Encyclopedic Database)
        # =====================================================================
        # Sort terms by length descending to match multi-word concepts first (e.g. "quantitative easing" before "easing")
        sorted_terms = sorted(GLOSSARY_DATABASE.keys(), key=len, reverse=True)

        for term in sorted_terms:
            info = GLOSSARY_DATABASE[term]
            pattern = r'\b' + re.escape(term) + r'\b'
            
            # Match if exact query matches term, or user asks "what is X", "explain X", "meaning of X"
            is_exact = low == term or low == f"{term}?" or low == f"what is {term}" or low == f"what is {term}?"
            has_word = re.search(pattern, low)
            is_querying = any(kw in low for kw in ["what is", "explain", "define", "meaning", "how does", "tell me about", "what are"]) or is_exact

            if is_exact or (has_word and is_querying):
                why_matters = info.get("why_it_matters", f"Understanding {term} protects your investments and helps you spot market opportunities.")
                reply = (
                    f"### 💡 **{term.title()}** Explained Simply\n\n"
                    f"📌 **Definition**: {info['definition']}\n\n"
                    f"📊 **Real-World Context**: *\"{info['example']}\"*\n\n"
                    f"⚖️ **Why It Matters to Your Money**: {why_matters}\n\n"
                    f"🏷️ **Category**: `{info['category']}`"
                )
                return ChatResponse(
                    reply=reply,
                    suggested_questions=[
                        f"How does {term} impact stock markets?",
                        "What is today's market sentiment?",
                        "Explain the difference between stocks and bonds"
                    ],
                    relevant_terms=[term.title(), info['category']]
                )

        # =====================================================================
        # 6. TODAY'S NEWS DIGEST & ACTIVE HEADLINES
        # =====================================================================
        if any(w in low for w in ["today's news", "todays news", "latest news", "top headlines", "news summary", "what happened today", "market news", "daily brief", "market update"]):
            lines = []
            for idx, a in enumerate(articles[:4], 1):
                icon = "🟢" if a.sentiment == "bullish" else "🔴" if a.sentiment == "bearish" else "🟡"
                summary_snip = a.simplified_summary[:130] if a.simplified_summary else a.description[:130]
                lines.append(f"{idx}. {icon} **{a.title}** ({a.sector})\n   *{summary_snip}...*")
            
            headlines_str = "\n\n".join(lines) if lines else "No live articles found in the feed at this moment."
            reply = (
                f"### 📰 **Today's Key Financial News Headlines**\n\n"
                f"{headlines_str}\n\n"
                f"**Overall Market Tone**: **{overview.market_mood}** ({overview.market_sentiment_score}/100).\n"
                f"Click on any article on the home dashboard to read the full simplified breakdown or listen to the audio narration!"
            )
            return ChatResponse(
                reply=reply,
                suggested_questions=[
                    "Why are markets moving today?",
                    "What did the Fed say about interest rates?",
                    "What is the top performing sector today?"
                ],
                relevant_terms=["Live News", "Headlines"]
            )

        # =====================================================================
        # 7. SPECIFIC ARTICLE BREAKDOWN BY TOPIC
        # =====================================================================
        is_article_query = any(kw in low for kw in ["article", "story", "headline", "in the news", "what happened with", "report on"])
        if is_article_query or current_article_id:
            matched_article = None
            if current_article_id:
                matched_article = next((a for a in articles if a.id == current_article_id), None)

            if not matched_article:
                for a in articles:
                    t_low = a.title.lower()
                    if any(w in low for w in ["tech", "ai", "nvidia", "chip", "semiconductor"]) and any(w in t_low for w in ["tech", "ai", "nvidia", "chip"]):
                        matched_article = a
                        break
                    elif any(w in low for w in ["fed", "rate", "powell", "inflation"]) and any(w in t_low for w in ["fed", "rate", "inflation"]):
                        matched_article = a
                        break
                    elif any(w in low for w in ["oil", "crude", "energy"]) and any(w in t_low for w in ["oil", "crude"]):
                        matched_article = a
                        break
                    elif any(w in low for w in ["bitcoin", "crypto"]) and any(w in t_low for w in ["bitcoin", "crypto"]):
                        matched_article = a
                        break
                    elif any(w in low for w in ["tesla", "ev"]) and any(w in t_low for w in ["tesla", "ev", "electric"]):
                        matched_article = a
                        break

            if matched_article:
                takeaways = "\n".join([f"- {t}" for t in matched_article.key_takeaways])
                reply = (
                    f"### 📰 **Story Breakdown: {matched_article.title}**\n\n"
                    f"🔍 **What Happened**: {matched_article.what_happened}\n\n"
                    f"💡 **Why It Matters**: {matched_article.why_it_matters}\n\n"
                    f"📈 **Market Impact**: {matched_article.market_impact}\n\n"
                    f"🎯 **Key Takeaways**:\n{takeaways}"
                )
                return ChatResponse(
                    reply=reply,
                    suggested_questions=[
                        "How does this affect regular investors?",
                        "What is today's overall market sentiment?",
                        "Show today's top financial headlines"
                    ],
                    relevant_terms=[matched_article.sector]
                )

        # =====================================================================
        # 8. PERSONAL FINANCE & INVESTMENT ROADMAP
        # =====================================================================
        if any(w in low for w in ["how to start investing", "beginner invest", "where to invest", "start investing", "how should i invest", "how to invest"]):
            reply = (
                "### 🚀 **How to Start Investing: A Step-by-Step Roadmap**\n\n"
                "1. **Build an Emergency Fund**: Set aside 3 to 6 months of living expenses in a liquid high-yield savings account or fixed deposit before taking market risk.\n"
                "2. **Eliminate Toxic High-Interest Debt**: Pay off credit cards (>18% APR) first; that provides an immediate, guaranteed financial return.\n"
                "3. **Invest in Broad-Market Index Funds / ETFs**: Rather than trying to pick individual winning stocks, invest in broad indices (e.g. S&P 500, Nifty 50, Total World Stock) that own hundreds of leading companies simultaneously.\n"
                "4. **Automate via SIP / Dollar-Cost Averaging**: Invest a fixed sum every single month to remove emotion and average out market peaks and valleys.\n"
                "5. **Think in Decades**: Real wealth is built by allowing compound interest to work undisturbed over 10–20+ years."
            )
            return ChatResponse(
                reply=reply,
                suggested_questions=[
                    "What is Dollar-Cost Averaging (DCA)?",
                    "What is an Index Fund?",
                    "What is the Rule of 72?"
                ],
                relevant_terms=["Investing Roadmap", "Compounding"]
            )

        # =====================================================================
        # 9. TODAY'S MARKET SENTIMENT & MOOD
        # =====================================================================
        if any(w in low for w in ["sentiment", "market mood", "market today", "how is market", "market tone", "how are markets"]):
            top_sector = overview.top_sectors[0]['name'] if overview.top_sectors else "Technology"
            reply = (
                f"### 📊 **Live Market Sentiment: {overview.market_mood}** ({overview.market_sentiment_score}/100)\n\n"
                f"- **Bullish Signals ({overview.bullish_count} stories)**: Driven by positive earnings growth, institutional ETF capital flows, and steady economic data.\n"
                f"- **Bearish Signals ({overview.bearish_count} stories)**: Elevated bond yields, persistent inflation reports, and geopolitical supply vulnerabilities.\n\n"
                f"📌 **Leading Focus Area**: The `{top_sector}` sector is experiencing high volume and investor attention today."
            )
            return ChatResponse(
                reply=reply,
                suggested_questions=[
                    "Why are tech stocks moving?",
                    "What did the Fed say about interest rates?",
                    "Show today's top financial headlines"
                ],
                relevant_terms=["Market Sentiment", overview.market_mood]
            )

        # =====================================================================
        # 10. INTELLIGENT, CONTEXTUAL FINANCIAL KNOWLEDGE FALLBACK
        # =====================================================================
        # Extract meaningful terms for a clean, customized explanation
        stop_words = {
            "what", "how", "why", "when", "where", "which", "who", "the", "and",
            "can", "could", "would", "should", "tell", "about", "is", "are", "was",
            "were", "for", "with", "this", "that", "all", "my", "your", "you",
            "summarize", "summary", "explain", "give", "please", "know", "want",
            "put", "get", "see", "does", "did", "have", "has", "think", "like", 
            "money", "me", "i"
        }
        clean_words = [w for w in re.findall(r'[a-zA-Z0-9\+\-]+', low) if len(w) > 2 and w not in stop_words]
        topic_phrase = " ".join(clean_words[:3]).title() if clean_words else "Financial Markets"

        # Provide a thoughtful, educational, realistic answer instead of a silly formula
        reply = (
            f"### 💡 **Financial Insights: {topic_phrase}**\n\n"
            f"Thank you for asking about **{query}**!\n\n"
            f"Here is how financial experts and seasoned investors approach this topic:\n\n"
            f"1. **Core Concept**: In personal finance and market economics, **{topic_phrase}** influences risk management, capital deployment, and expected investment returns.\n"
            f"2. **Key Valuation Factors**: Investors examine corporate cash flows, prevailing central bank interest rates, and broader macroeconomic data before making major portfolio decisions in this area.\n"
            f"3. **Practical Strategy**: Avoid making hurried decisions based on short-term headlines or market speculation. Focus on broad portfolio diversification, low expense ratios, and long-term compounding.\n\n"
            f"If you'd like deeper specifics on this topic, feel free to ask a focused question below!"
        )

        suggested = [
            f"How does {topic_phrase} impact investment returns?",
            "What is today's overall market sentiment?",
            "Explain the difference between stocks and bonds"
        ]

        return ChatResponse(
            reply=reply,
            suggested_questions=suggested,
            relevant_terms=[w.title() for w in clean_words[:2]] if clean_words else ["Finance"]
        )
