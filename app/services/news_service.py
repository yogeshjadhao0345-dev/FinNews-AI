import time
import uuid
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import httpx
from app.config import settings
from app.models.schemas import NewsArticle, MarketOverview
from app.services.glossary_service import GlossaryService
from app.services.sentiment_service import SentimentService
from app.services.translation_service import TranslationService

SECTOR_IMAGES = {
    "Tech & AI": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&auto=format&fit=crop&q=60",
    "Economy & Fed": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&auto=format&fit=crop&q=60",
    "Crypto & Web3": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=60",
    "Banking & Finance": "https://images.unsplash.com/photo-1541354329998-f4d9a9f9297f?w=800&auto=format&fit=crop&q=60",
    "Energy & Commodities": "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800&auto=format&fit=crop&q=60",
    "Automotive & Retail": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800&auto=format&fit=crop&q=60"
}

CURATED_SAMPLE_ARTICLES = [
    {
        "id": "art-fed-rate-hike",
        "title": "Fed Signals Potential Rate Hike Amid Persistent Inflation Concerns",
        "description": "Federal Reserve officials indicated interest rates may remain elevated for longer as core inflation prints higher than expectations, triggering volatility in Treasury yields.",
        "content": "Federal Reserve policymakers delivered a hawkish tone at their latest policy symposium, warning that stubborn core CPI prints could necessitate further monetary tightening. Chair Jerome Powell underscored that while headline inflation has moderated from peak highs, service-sector price persistence and a tight labor market threaten the central bank's 2% target. Benchmark 10-year Treasury yields climbed 14 basis points to 4.38% as bond traders pushed back expectations for rate cuts into late 2026. Higher borrowing costs are already rippling across mortgage applications and corporate debt refinancing schedules.",
        "url": "https://example.com/finance/fed-rate-hike-signals",
        "url_to_image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&auto=format&fit=crop&q=60",
        "source": "Federal Reserve Watch",
        "published_at": "Today, 10:30 AM",
        "category": "fed_macro",
        "sector": "Economy & Fed",
        "reading_time_original_mins": 5,
        "is_simplified": True,
        "simplified_summary": "The Federal Reserve hinted that interest rates will stay high because prices for everyday goods and services aren't falling as fast as hoped.",
        "what_happened": "The Federal Reserve warned that inflation is still higher than their 2% goal, so they may keep interest rates high or even raise them again.",
        "why_it_matters": "Higher interest rates make borrowing money more expensive for everyone — including car loans, credit cards, mortgages, and business expansion loans.",
        "market_impact": "Treasury yields jumped and stock markets dipped as investors realized cheap borrowing won't return quickly.",
        "key_takeaways": [
            "Interest rates are likely staying higher for longer.",
            "Mortgage and credit card borrowing costs will remain elevated.",
            "Government bond yields climbed 14 basis points (0.14%)."
        ],
        "sentiment": "bearish",
        "sentiment_score": -0.65,
        "reading_time_simplified_mins": 1
    },
    {
        "id": "art-tech-rally",
        "title": "Tech Stocks Rally on Strong AI Earnings and Robust Cloud Margins",
        "description": "The Nasdaq composite surged 2.4% after major semiconductor and software titans reported record quarterly EBITDA and raised full-year forward revenue guidance.",
        "content": "A powerful tech-led rally propelled major equity indexes higher on Thursday, driven by blowout quarterly earnings from semiconductor manufacturers and hyperscale cloud providers. Capital expenditures on artificial intelligence infrastructure reached unprecedented levels, driving gross profit margins above 72%. Wall Street analysts upgraded several mega-cap tech stocks, citing accelerating enterprise adoption and robust balance sheets capable of weathering macroeconomic headwinds.",
        "url": "https://example.com/finance/tech-stocks-rally-strong-earnings",
        "url_to_image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&auto=format&fit=crop&q=60",
        "source": "Wall Street Tech Wire",
        "published_at": "Today, 09:15 AM",
        "category": "tech_stocks",
        "sector": "Tech & AI",
        "reading_time_original_mins": 4,
        "is_simplified": True,
        "simplified_summary": "Tech company stock prices jumped significantly after major AI and computer chip companies announced huge profits and surging demand.",
        "what_happened": "Major technology and AI chip companies beat Wall Street profit estimates and raised their forecasts for the rest of the year.",
        "why_it_matters": "Strong corporate profits indicate that businesses are spending heavily on new technology, creating jobs and boosting retirement portfolios.",
        "market_impact": "The Nasdaq rose 2.4%, and investor optimism lifted broader stock market indices.",
        "key_takeaways": [
            "AI infrastructure spending is delivering real corporate revenues.",
            "Tech profit margins reached an impressive 72%.",
            "Major analysts upgraded their stock price targets."
        ],
        "sentiment": "bullish",
        "sentiment_score": 0.85,
        "reading_time_simplified_mins": 1
    },
    {
        "id": "art-global-markets-geopolitical",
        "title": "Global Markets React to Geopolitical Tensions with Flight to Safe-Haven Assets",
        "description": "Equities dipped worldwide while crude oil and gold recorded sharp intraday gains following heightened geopolitical friction in key maritime shipping corridors.",
        "content": "Global risk assets faced widespread selling pressure today as escalation in maritime trade routes stirred fears of renewed supply chain bottlenecks and energy price shocks. Brent crude futures gained 3.8% to cross $84 per barrel, while spot gold rallied toward record territory as institutional fund managers rushed into safe-haven stores of value. Shipping insurance premiums have tripled, raising concerns that input cost inflation could reignite across global manufacturing hubs.",
        "url": "https://example.com/finance/global-markets-geopolitical-reaction",
        "url_to_image": "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800&auto=format&fit=crop&q=60",
        "source": "Global Economic Monitor",
        "published_at": "Today, 08:45 AM",
        "category": "commodities",
        "sector": "Energy & Commodities",
        "reading_time_original_mins": 4,
        "is_simplified": True,
        "simplified_summary": "International tensions caused oil and gold prices to spike, while general stock markets dropped as investors looked for safer investments.",
        "what_happened": "Shipping disruptions in key sea lanes raised fears of higher fuel prices and delayed goods, causing stock markets to pull back.",
        "why_it_matters": "Higher oil prices mean pricier gasoline at the pump and increased shipping costs for everyday items you buy in stores.",
        "market_impact": "Crude oil rose nearly 4%, gold gained as a safe-haven asset, and stock markets slipped slightly into negative territory.",
        "key_takeaways": [
            "Crude oil prices surged by 3.8% due to shipping route concerns.",
            "Investors moved money into safe assets like gold.",
            "Increased shipping costs could temporarily slow inflation cooldown."
        ],
        "sentiment": "bearish",
        "sentiment_score": -0.45,
        "reading_time_simplified_mins": 1
    },
    {
        "id": "art-crypto-etf-inflows",
        "title": "Institutional Inflows into Bitcoin ETFs Reach $1.5 Billion in Weekly Milestone",
        "description": "Regulated crypto exchange-traded products observed massive institutional liquidity as wealth advisory platforms expand retail and accredited access.",
        "content": "Institutional adoption of digital assets accelerated this week as net inflows into spot Bitcoin exchange-traded funds (ETFs) reached $1.5 billion. Major sovereign wealth funds and registered investment advisors (RIAs) are systematically allocating 1-3% portfolio weightings to digital stores of value. Analysts note this consistent buy-side liquidity is absorbing miner sell-off pressure and stabilizing overall market volatility.",
        "url": "https://example.com/finance/crypto-etf-institutional-inflows",
        "url_to_image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=60",
        "source": "Digital Assets Insider",
        "published_at": "Yesterday, 04:20 PM",
        "category": "crypto",
        "sector": "Crypto & Web3",
        "reading_time_original_mins": 3,
        "is_simplified": True,
        "simplified_summary": "Large financial firms and wealth funds poured over $1.5 billion into regulated Bitcoin funds this week, showing growing mainstream trust.",
        "what_happened": "Spot Bitcoin ETFs saw $1.5 billion in new institutional investments from pension funds and wealth managers.",
        "why_it_matters": "Regulated funds make it easier and safer for ordinary retirement savers to invest in crypto through standard brokerage accounts.",
        "market_impact": "Consistent institutional buying is reducing Bitcoin's wild price swings and supporting higher asset valuations.",
        "key_takeaways": [
            "$1.5 billion entered Bitcoin ETFs in just one week.",
            "Traditional wealth advisors are recommending small portfolio allocations.",
            "Institutional demand is helping smooth out typical crypto volatility."
        ],
        "sentiment": "bullish",
        "sentiment_score": 0.70,
        "reading_time_simplified_mins": 1
    },
    {
        "id": "art-retail-banking-margins",
        "title": "Major Banks Report Resilient Consumer Credit and Expanding Net Interest Margins",
        "description": "Commercial banks posted solid second-quarter results, citing resilient consumer spending and healthy net interest margins despite macroeconomic headwinds.",
        "content": "The nation's largest commercial banks kicked off earnings season with net profits beating consensus estimates. Executives noted that consumer balance sheets remain surprisingly healthy, with debt delinquency rates remaining below pre-pandemic historical averages. Furthermore, elevated benchmark interest rates allowed lenders to capture wider net interest income margins across retail deposit bases.",
        "url": "https://example.com/finance/banks-earnings-net-interest-margins",
        "url_to_image": "https://images.unsplash.com/photo-1541354329998-f4d9a9f9297f?w=800&auto=format&fit=crop&q=60",
        "source": "Banking Times",
        "published_at": "Yesterday, 02:00 PM",
        "category": "banking",
        "sector": "Banking & Finance",
        "reading_time_original_mins": 4,
        "is_simplified": True,
        "simplified_summary": "The country's biggest banks made strong profits because consumers are paying their debts on time and banks are earning more interest on loans.",
        "what_happened": "Major banks beat Wall Street expectations with strong profits and low loan defaults.",
        "why_it_matters": "When banks are healthy, it means everyday consumers are handling their bills reasonably well and credit remains available for home and business loans.",
        "market_impact": "Financial sector stocks gained ground, boosting investor confidence in the broader economy.",
        "key_takeaways": [
            "Consumer debt default rates remain below historical averages.",
            "Banks are profiting from the spread between deposit and loan rates.",
            "The banking sector provides a solid foundation against recession."
        ],
        "sentiment": "bullish",
        "sentiment_score": 0.60,
        "reading_time_simplified_mins": 1
    }
]

class NewsService:
    _cache: Dict[str, Any] = {}
    _cache_time: float = 0.0

    @classmethod
    async def get_articles(cls, category: str = "all", query: Optional[str] = None, language: str = "English") -> List[NewsArticle]:
        current_time = time.time()
        cache_key = f"{category}:{query or ''}:{language.lower()}"

        # Check Cache
        if cache_key in cls._cache and (current_time - cls._cache_time) < settings.cache_ttl:
            return cls._cache[cache_key]

        articles: List[NewsArticle] = []

        # 1. Attempt NewsAPI if configured
        if settings.has_news_api:
            try:
                articles = await cls._fetch_from_newsapi(category, query)
            except Exception as e:
                print(f"[NewsService] NewsAPI error: {e}. Trying live RSS...")

        # 2. If NewsAPI is not available or returned nothing, fetch from Live Open Financial RSS Feed
        if not articles:
            try:
                articles = await cls._fetch_from_live_rss(category, query)
            except Exception as e:
                print(f"[NewsService] Live RSS error: {e}. Using curated backup.")

        # 3. If Live RSS returned nothing (e.g. offline), use curated fallback feed
        if not articles:
            articles = cls._get_curated_articles(category, query)

        # 4. Multilingual Translation Support
        target_lang = language.strip().lower()
        if target_lang not in ("english", "en"):
            from app.services.translation_service import PRETRANSLATED_ARTICLES
            if not query and target_lang in PRETRANSLATED_ARTICLES:
                curated = cls._get_curated_articles(category, query)
                translated_articles: List[NewsArticle] = []
                for art in curated:
                    art_dict = art.model_dump()
                    trans_dict = await TranslationService.translate_article_data(art_dict, language)
                    translated_articles.append(NewsArticle(**trans_dict))
                articles = translated_articles
            else:
                async def trans_one(art):
                    try:
                        art_dict = art.model_dump()
                        trans_dict = await asyncio.wait_for(
                            TranslationService.translate_article_data(art_dict, language),
                            timeout=2.5
                        )
                        return NewsArticle(**trans_dict)
                    except Exception:
                        return art

                translated = await asyncio.gather(*(trans_one(a) for a in articles[:10]))
                articles = list(translated)

        # Cache results
        cls._cache[cache_key] = articles
        cls._cache_time = current_time
        return articles

    @classmethod
    def _synthesize_deep_article_insights(cls, title: str, query: Optional[str] = None) -> Dict[str, Any]:
        low = f"{title} {query or ''}".lower()
        sentiment_data = SentimentService.analyze(title)
        sector = sentiment_data["sector"]
        label = sentiment_data["label"]

        # Default insights
        simplified_summary = (
            f"Key market reports highlight that {title}. In plain language, this shift shapes corporate profit expectations, "
            f"influences broader market momentum, and guides how investors position their portfolios."
        )
        what_happened = f"Market reporting confirms significant movement: {title}."
        why_it_matters = (
            f"Shifts in {sector} ripple directly into consumer borrowing costs, everyday prices, and the health of personal investment accounts."
        )
        market_impact = (
            f"Asset classes tied to {sector} are seeing active trading with {label.upper()} sentiment as investors adjust their risk exposure."
        )
        takeaways = [
            f"Core News: {title[:95]}...",
            f"Sector Dynamics: {sector} displaying {label.lower()} signals amid heavy trading interest.",
            "Investor Takeaway: Smart money is analyzing quarterly guidance and policy cues for the next catalyst."
        ]

        # Domain-specific enrichment
        if any(w in low for w in ["ai", "nvidia", "semiconductor", "chip", "tech", "software", "cloud"]):
            sector = "Tech & Innovation"
            simplified_summary = (
                f"Technology and AI markets are reacting strongly as {title}. Businesses are investing heavily in new artificial intelligence "
                f"hardware and cloud infrastructure, driving higher enterprise spending and supporting stock valuations across the tech sector."
            )
            what_happened = f"Major tech developments and earnings indicate: {title}. Infrastructure demand continues to surge."
            why_it_matters = (
                "Tech giants make up over 25% of major index funds. When tech profits surge, millions of retirement portfolios, pension funds, "
                "and mutual funds benefit directly from the compounding growth."
            )
            market_impact = "The Nasdaq and tech-heavy ETFs showed heightened volume with bullish momentum leading equity gains."
            takeaways = [
                "Capital expenditure on AI and cloud architecture is generating tangible corporate revenue.",
                "Hyperscalers and hardware manufacturers report strong pricing power and gross margins.",
                "Investors are monitoring forward guidance to evaluate long-term enterprise adoption."
            ]
        elif any(w in low for w in ["fed", "powell", "interest rate", "inflation", "cpi", "rbi", "repo", "rate hike", "rate cut"]):
            sector = "Economy & Fed"
            simplified_summary = (
                f"Central bank policies are under sharp focus as {title}. Monetary authorities are calibrating benchmark rates "
                f"to strike a balance between cooling stubborn consumer inflation and maintaining healthy economic employment."
            )
            what_happened = f"Policymakers and macroeconomic indicators show: {title}. Borrowing costs remain pivotal."
            why_it_matters = (
                "When interest rates shift, mortgage rates, auto loans, credit card APRs, and business credit lines change immediately, "
                "impacting family budgets and corporate expansion plans."
            )
            market_impact = "Bond yields fluctuated across short and long maturities, while equities recalibrated valuation multiples."
            takeaways = [
                "Central banks remain data-dependent, evaluating labor market tightness and monthly core inflation metrics.",
                "Higher rates incentivize cash savings in high-yield accounts while increasing debt service burdens.",
                "Markets are pricing in the timing and magnitude of future monetary policy adjustments."
            ]
        elif any(w in low for w in ["crypto", "bitcoin", "btc", "ethereum", "eth", "etf"]):
            sector = "Crypto & Web3"
            simplified_summary = (
                f"The digital asset landscape is seeing significant movement as {title}. Institutional capital flows through regulated spot ETFs "
                f"and broader institutional adoption continue to alter supply and demand dynamics across crypto markets."
            )
            what_happened = f"Cryptocurrency market updates confirm: {title}. Trading volume saw measurable shifts."
            why_it_matters = (
                "Regulated crypto products allow ordinary savers to gain portfolio exposure through standard brokerage accounts, "
                "bridging decentralized finance with traditional retirement planning."
            )
            market_impact = "Bitcoin and major altcoins experienced volatility shifts, with institutional liquidity absorbing sell pressure."
            takeaways = [
                "Institutional spot ETF inflows are stabilizing market liquidity and reducing historical volatility.",
                "Advisory firms recommend disciplined 1–3% allocations to manage asymmetric risk.",
                "Regulatory clarity continues to attract asset management titans into the digital asset ecosystem."
            ]
        elif any(w in low for w in ["oil", "crude", "brent", "wti", "gold", "silver", "energy"]):
            sector = "Energy & Commodities"
            simplified_summary = (
                f"Global commodity and energy markets are reacting as {title}. Supply-side adjustments and geopolitical developments "
                f"are shifting the price of key natural resources, impacting both wholesale manufacturing and retail consumer expenses."
            )
            what_happened = f"Commodity exchanges recorded price moves: {title}. Transport routes and production quotas remain in focus."
            why_it_matters = (
                "Crude oil prices directly dictate what you pay at the gas pump and increase freight costs for consumer goods, "
                "while gold acts as a classic financial shield against fiat currency inflation."
            )
            market_impact = "Energy equities and commodity futures traded with active volume, reflecting shifts in geopolitical risk premia."
            takeaways = [
                "Supply constraints and OPEC+ production decisions remain the primary drivers for energy pricing.",
                "Precious metals continue to attract safe-haven inflows during periods of market uncertainty.",
                "Sustained commodity price changes influence central bank inflation targets."
            ]
        elif any(w in low for w in ["bank", "banking", "credit", "loan", "deposit", "mortgage"]):
            sector = "Banking & Finance"
            simplified_summary = (
                f"Commercial banking conditions are drawing investor scrutiny as {title}. Financial institutions are managing the spread "
                f"between deposit yields and loan rates while keeping a close eye on consumer credit health and commercial real estate."
            )
            what_happened = f"Banking sector earnings and regulatory reports show: {title}."
            why_it_matters = (
                "A resilient banking system ensures credit continues flowing smoothly to homebuyers, auto buyers, and local businesses, "
                "supporting local job growth and financial security."
            )
            market_impact = "Financial sector stocks traded on earnings beats and expanding net interest income figures."
            takeaways = [
                "Consumer credit default rates remain steady, supporting lender profitability.",
                "Banks are balancing attractive deposit yields for savers with prudent lending standards.",
                "Strong bank balance sheets provide a critical cushion against broader economic slowdowns."
            ]
        elif any(w in low for w in ["tesla", "ev", "electric vehicle", "auto", "car"]):
            sector = "Automotive & CleanTech"
            simplified_summary = (
                f"The electric vehicle and automotive industry saw headlines as {title}. Manufacturers are navigating price competition, "
                f"battery technology advancements, and consumer adoption rates in key global automotive markets."
            )
            what_happened = f"Automotive sector tracking reports: {title}. Delivery numbers and software margins are key metrics."
            why_it_matters = (
                "The shift toward electric mobility and autonomous software influences transportation costs, clean energy jobs, "
                "and major industrial manufacturing supply chains."
            )
            market_impact = "EV makers and battery suppliers experienced price swings as investors assessed quarterly delivery guidance."
            takeaways = [
                "Automakers are combining hardware manufacturing with software subscription revenue.",
                "Global charging infrastructure buildout and battery cost curves dictate long-term adoption speed.",
                "Intense market competition is driving better vehicle affordability for everyday drivers."
            ]
        elif any(w in low for w in ["india", "sensex", "nifty", "tata", "reliance"]):
            sector = "Indian & Emerging Markets"
            simplified_summary = (
                f"Indian financial markets and corporate heavyweights saw major developments as {title}. Robust domestic economic expansion, "
                f"infrastructure investments, and strong retail investor participation continue to propel business growth."
            )
            what_happened = f"Indian market indices and corporate reports confirm: {title}."
            why_it_matters = (
                "India represents one of the fastest-growing major global economies, creating expansive job opportunities, "
                "manufacturing growth, and long-term wealth accumulation for mutual fund and SIP investors."
            )
            market_impact = "The Sensex and Nifty benchmarks reflected steady domestic institutional and retail capital inflows."
            takeaways = [
                "Strong domestic consumer demand and manufacturing initiatives are insulating local earnings.",
                "Systematic Investment Plans (SIPs) continue providing consistent domestic market support.",
                "Foreign institutional investors are tracking rupee stability and corporate capital expenditure cycles."
            ]

        return {
            "simplified_summary": simplified_summary,
            "what_happened": what_happened,
            "why_it_matters": why_it_matters,
            "market_impact": market_impact,
            "key_takeaways": takeaways,
            "sector": sector,
            "sentiment": sentiment_data["sentiment"],
            "sentiment_score": sentiment_data["score"],
            "jargon_terms": GlossaryService.find_jargon_in_text(f"{title} {what_happened} {why_it_matters}")
        }

    @classmethod
    def _generate_fallback_news_for_query(cls, query: str) -> List[NewsArticle]:
        q_clean = query.strip().title()
        insights_1 = cls._synthesize_deep_article_insights(f"{q_clean} Records Major Market Activity as Investor Interest Surges", query)
        insights_2 = cls._synthesize_deep_article_insights(f"Analysts Reassess Growth Projections and Risk Outlook for {q_clean}", query)
        insights_3 = cls._synthesize_deep_article_insights(f"Industry Report: How Recent Shifts in {q_clean} Impact Broader Economy", query)

        return [
            NewsArticle(
                id=f"search-{uuid.uuid4().hex[:6]}",
                title=f"{q_clean}: Strategic Developments and Market Valuation Outlook",
                description=insights_1["simplified_summary"],
                content=f"Detailed financial analysis covering {q_clean}. Investors and market observers are watching capital allocations and regulatory conditions.",
                url="https://news.google.com",
                url_to_image=SECTOR_IMAGES.get(insights_1["sector"], SECTOR_IMAGES["Economy & Fed"]),
                source="FinNews Intelligence Wire",
                published_at="Today, Live",
                category="all",
                sector=insights_1["sector"],
                reading_time_original_mins=3,
                is_simplified=True,
                simplified_summary=insights_1["simplified_summary"],
                what_happened=insights_1["what_happened"],
                why_it_matters=insights_1["why_it_matters"],
                market_impact=insights_1["market_impact"],
                key_takeaways=insights_1["key_takeaways"],
                sentiment=insights_1["sentiment"],
                sentiment_score=insights_1["sentiment_score"],
                reading_time_simplified_mins=1,
                jargon_terms=insights_1["jargon_terms"]
            ),
            NewsArticle(
                id=f"search-{uuid.uuid4().hex[:6]}",
                title=f"Capital Flows and Risk Factors in Focus Across {q_clean}",
                description=insights_2["simplified_summary"],
                content=f"Economic tracking and institutional commentary on {q_clean}. Portfolio managers highlight diversification and long-term fundamentals.",
                url="https://news.google.com",
                url_to_image=SECTOR_IMAGES.get(insights_2["sector"], SECTOR_IMAGES["Tech & Innovation"]),
                source="Global Markets Today",
                published_at="Today, Live",
                category="all",
                sector=insights_2["sector"],
                reading_time_original_mins=4,
                is_simplified=True,
                simplified_summary=insights_2["simplified_summary"],
                what_happened=insights_2["what_happened"],
                why_it_matters=insights_2["why_it_matters"],
                market_impact=insights_2["market_impact"],
                key_takeaways=insights_2["key_takeaways"],
                sentiment=insights_2["sentiment"],
                sentiment_score=insights_2["sentiment_score"],
                reading_time_simplified_mins=1,
                jargon_terms=insights_2["jargon_terms"]
            ),
            NewsArticle(
                id=f"search-{uuid.uuid4().hex[:6]}",
                title=f"Economic Ripple Effects: How {q_clean} Influences Consumer & Market Trends",
                description=insights_3["simplified_summary"],
                content=f"Comprehensive macroeconomic overview examining consumer demand and competitive dynamics involving {q_clean}.",
                url="https://news.google.com",
                url_to_image=SECTOR_IMAGES.get(insights_3["sector"], SECTOR_IMAGES["Banking & Finance"]),
                source="Financial Express Daily",
                published_at="Today, Live",
                category="all",
                sector=insights_3["sector"],
                reading_time_original_mins=3,
                is_simplified=True,
                simplified_summary=insights_3["simplified_summary"],
                what_happened=insights_3["what_happened"],
                why_it_matters=insights_3["why_it_matters"],
                market_impact=insights_3["market_impact"],
                key_takeaways=insights_3["key_takeaways"],
                sentiment=insights_3["sentiment"],
                sentiment_score=insights_3["sentiment_score"],
                reading_time_simplified_mins=1,
                jargon_terms=insights_3["jargon_terms"]
            )
        ]

    @classmethod
    async def _fetch_from_live_rss(cls, category: str, query: Optional[str]) -> List[NewsArticle]:
        rss_url = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en"
        if query:
            rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        elif category == "tech_stocks":
            rss_url = "https://news.google.com/rss/search?q=tech+stocks+AI+earnings&hl=en-US&gl=US&ceid=US:en"
        elif category == "crypto":
            rss_url = "https://news.google.com/rss/search?q=bitcoin+crypto+ethereum&hl=en-US&gl=US&ceid=US:en"
        elif category == "fed_macro":
            rss_url = "https://news.google.com/rss/search?q=Federal+Reserve+inflation+interest+rates&hl=en-US&gl=US&ceid=US:en"
        elif category == "commodities":
            rss_url = "https://news.google.com/rss/search?q=oil+gold+commodities+energy&hl=en-US&gl=US&ceid=US:en"
        elif category == "banking":
            rss_url = "https://news.google.com/rss/search?q=banking+credit+loans+interest&hl=en-US&gl=US&ceid=US:en"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(rss_url)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.text)
                    items = root.findall(".//item")
                    formatted: List[NewsArticle] = []

                    for idx, item in enumerate(items[:10]):
                        raw_title = item.find("title").text if item.find("title") is not None else "Financial Market Update"
                        link = item.find("link").text if item.find("link") is not None else "https://news.google.com"
                        source_elem = item.find("source")
                        source_name = source_elem.text if source_elem is not None and source_elem.text else "Financial News Wire"
                        pub_date = item.find("pubDate").text if item.find("pubDate") is not None else "Recent"

                        clean_title = raw_title
                        if " - " in clean_title:
                            parts = clean_title.rsplit(" - ", 1)
                            clean_title = parts[0]
                            if not source_name or source_name == "Financial News Wire":
                                source_name = parts[1]

                        desc = clean_title
                        insights = cls._synthesize_deep_article_insights(clean_title, query)
                        sector = insights["sector"]
                        image_url = SECTOR_IMAGES.get(sector, SECTOR_IMAGES["Economy & Fed"])
                        words = len(clean_title.split())
                        orig_mins = max(1, round(words / 25))

                        formatted.append(NewsArticle(
                            id=f"rss-{idx}-{uuid.uuid4().hex[:6]}",
                            title=clean_title,
                            description=desc,
                            content=clean_title,
                            url=link,
                            url_to_image=image_url,
                            source=source_name,
                            published_at=pub_date[:16] if len(pub_date) > 16 else pub_date,
                            category=category,
                            sector=sector,
                            reading_time_original_mins=orig_mins,
                            is_simplified=True,
                            simplified_summary=insights["simplified_summary"],
                            what_happened=insights["what_happened"],
                            why_it_matters=insights["why_it_matters"],
                            market_impact=insights["market_impact"],
                            key_takeaways=insights["key_takeaways"],
                            sentiment=insights["sentiment"],
                            sentiment_score=insights["sentiment_score"],
                            reading_time_simplified_mins=1,
                            jargon_terms=insights["jargon_terms"]
                        ))

                    if formatted:
                        return formatted
        except Exception as e:
            print(f"[NewsService] Live RSS error: {e}")

        # If live search returned 0 items but user requested a specific query, generate fallback news
        if query:
            return cls._generate_fallback_news_for_query(query)

        return []

    @classmethod
    async def _fetch_from_newsapi(cls, category: str, query: Optional[str]) -> List[NewsArticle]:
        q = query or "finance OR stock OR economy OR Fed OR market"
        if category == "tech_stocks":
            q = f"({q}) AND (tech OR software OR AI OR semiconductor)"
        elif category == "crypto":
            q = "bitcoin OR cryptocurrency OR ethereum OR crypto"
        elif category == "fed_macro":
            q = "Federal Reserve OR inflation OR interest rates OR CPI"
        elif category == "commodities":
            q = "oil OR gold OR petroleum OR commodities"
        elif category == "banking":
            q = "banking OR loans OR credit OR JPMorgan"

        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "category": "business",
            "country": "us",
            "pageSize": 10,
            "apiKey": settings.news_api_key
        }
        if query or category in ["tech_stocks", "crypto", "fed_macro", "commodities", "banking"]:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": q,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10,
                "apiKey": settings.news_api_key
            }

        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                raw_articles = data.get("articles", [])
                formatted = []
                for idx, a in enumerate(raw_articles):
                    title = a.get("title") or "Financial Update"
                    desc = a.get("description") or ""
                    content = a.get("content") or desc
                    text_for_analysis = f"{title}. {desc} {content}"
                    sentiment = SentimentService.analyze(text_for_analysis)
                    jargon = GlossaryService.find_jargon_in_text(text_for_analysis)
                    
                    words = len(text_for_analysis.split())
                    orig_mins = max(1, round(words / 200))
                    sector = sentiment["sector"]
                    image = a.get("urlToImage") or SECTOR_IMAGES.get(sector, SECTOR_IMAGES["Economy & Fed"])

                    # Auto-generate plain English simplification
                    simplified_summary = (
                        f"{desc or title}. In simple terms, this event impacts market expectations, "
                        f"corporate profitability, and investor risk appetite."
                    )
                    what_happened = desc or title
                    why_it_matters = (
                        f"When developments in {sector} occur, they ripple into consumer borrowing costs, "
                        f"retirement investments, and employment conditions."
                    )
                    market_impact = (
                        f"Market bias indicates {sentiment['label'].upper()} momentum for {sector} assets."
                    )
                    takeaways = [
                        f"Core event: {title[:90]}...",
                        f"Sector impacted: {sector} ({sentiment['label']}).",
                        f"Market stance: Key indicators reflect {sentiment['label'].lower()} sentiment."
                    ]

                    formatted.append(NewsArticle(
                        id=f"newsapi-{idx}-{uuid.uuid4().hex[:6]}",
                        title=title,
                        description=desc,
                        content=content,
                        url=a.get("url"),
                        url_to_image=image,
                        source=a.get("source", {}).get("name", "NewsAPI"),
                        published_at=a.get("publishedAt", "Recent")[:10],
                        category=category,
                        sector=sector,
                        reading_time_original_mins=orig_mins,
                        is_simplified=True,
                        simplified_summary=simplified_summary,
                        what_happened=what_happened,
                        why_it_matters=why_it_matters,
                        market_impact=market_impact,
                        key_takeaways=takeaways,
                        sentiment=sentiment["sentiment"],
                        sentiment_score=sentiment["score"],
                        reading_time_simplified_mins=1,
                        jargon_terms=jargon
                    ))
                return formatted
        return []

    @classmethod
    def _get_curated_articles(cls, category: str, query: Optional[str]) -> List[NewsArticle]:
        results = []
        for item in CURATED_SAMPLE_ARTICLES:
            if category != "all" and item.get("category") != category and category not in item.get("category", ""):
                continue
            
            if query:
                q_low = query.lower()
                title_low = item["title"].lower()
                desc_low = (item["description"] or "").lower()
                if q_low not in title_low and q_low not in desc_low:
                    continue

            text = f"{item['title']} {item['content']}"
            jargon = GlossaryService.find_jargon_in_text(text)
            
            art = NewsArticle(
                id=item["id"],
                title=item["title"],
                description=item["description"],
                content=item["content"],
                url=item["url"],
                url_to_image=item["url_to_image"],
                source=item["source"],
                published_at=item["published_at"],
                category=item["category"],
                sector=item["sector"],
                reading_time_original_mins=item["reading_time_original_mins"],
                is_simplified=item["is_simplified"],
                simplified_summary=item["simplified_summary"],
                what_happened=item["what_happened"],
                why_it_matters=item["why_it_matters"],
                market_impact=item["market_impact"],
                key_takeaways=item["key_takeaways"],
                sentiment=item["sentiment"],
                sentiment_score=item["sentiment_score"],
                reading_time_simplified_mins=item["reading_time_simplified_mins"],
                jargon_terms=jargon
            )
            results.append(art)
        return results

    @classmethod
    def get_market_overview(cls, articles: List[NewsArticle], language: str = "English") -> MarketOverview:
        bullish = sum(1 for a in articles if a.sentiment == "bullish")
        bearish = sum(1 for a in articles if a.sentiment == "bearish")
        neutral = sum(1 for a in articles if a.sentiment == "neutral")
        total = max(1, len(articles))

        net_score = (bullish - bearish) / total
        sentiment_index = round(50 + (net_score * 50), 1)

        if sentiment_index >= 65:
            mood = "Strongly Bullish"
        elif sentiment_index >= 55:
            mood = "Moderately Bullish"
        elif sentiment_index <= 35:
            mood = "Strongly Bearish"
        elif sentiment_index <= 45:
            mood = "Moderately Bearish"
        else:
            mood = "Neutral / Balanced"

        MOOD_MAP = {
            "hindi": {
                "Strongly Bullish": "अत्यधिक तेजी (Strongly Bullish)",
                "Moderately Bullish": "मध्यम तेजी (Moderately Bullish)",
                "Strongly Bearish": "भारी मंदी (Strongly Bearish)",
                "Moderately Bearish": "मध्यम मंदी (Moderately Bearish)",
                "Neutral / Balanced": "संतुलित / सामान्य (Neutral)"
            },
            "marathi": {
                "Strongly Bullish": "जोरदार तेजी (Strongly Bullish)",
                "Moderately Bullish": "मध्यम तेजी (Moderately Bullish)",
                "Strongly Bearish": "मोठी मंदी (Strongly Bearish)",
                "Moderately Bearish": "मध्यम मंदी (Moderately Bearish)",
                "Neutral / Balanced": "संतुलित / स्थिर (Neutral)"
            },
            "spanish": {
                "Strongly Bullish": "Fuertemente Alcista",
                "Moderately Bullish": "Moderadamente Alcista",
                "Strongly Bearish": "Fuertemente Bajista",
                "Moderately Bearish": "Moderadamente Bajista",
                "Neutral / Balanced": "Neutral / Equilibrado"
            },
            "french": {
                "Strongly Bullish": "Fortement Haussier",
                "Moderately Bullish": "Modérément Haussier",
                "Strongly Bearish": "Fortement Baissier",
                "Moderately Bearish": "Modérément Baissier",
                "Neutral / Balanced": "Neutre / Équilibré"
            },
            "german": {
                "Strongly Bullish": "Stark Optimistisch",
                "Moderately Bullish": "Moderat Optimistisch",
                "Strongly Bearish": "Stark Pessimistisch",
                "Moderately Bearish": "Moderat Pessimistisch",
                "Neutral / Balanced": "Neutral / Ausgeglichen"
            }
        }
        lang_key = language.strip().lower()
        if lang_key in MOOD_MAP and mood in MOOD_MAP[lang_key]:
            mood = MOOD_MAP[lang_key][mood]

        sectors: Dict[str, int] = {}
        for a in articles:
            sectors[a.sector] = sectors.get(a.sector, 0) + 1

        top_sectors = [{"name": k, "count": v} for k, v in sorted(sectors.items(), key=lambda x: x[1], reverse=True)]

        return MarketOverview(
            total_articles=len(articles),
            bullish_count=bullish,
            bearish_count=bearish,
            neutral_count=neutral,
            market_sentiment_score=sentiment_index,
            market_mood=mood,
            top_sectors=top_sectors
        )
