import re
from typing import List, Dict, Any
from app.models.schemas import JargonItem, GlossaryTerm

GLOSSARY_DATABASE: Dict[str, Dict[str, str]] = {
    # =========================================================================
    # 1. MONETARY POLICY & MACROECONOMICS
    # =========================================================================
    "inflation": {
        "definition": "The rate at which general prices for goods and services increase over time, eroding the purchasing power of money.",
        "example": "When inflation is 6%, a grocery basket that cost $100 last year now costs $106.",
        "category": "Macroeconomics",
        "why_it_matters": "High inflation reduces the real value of cash savings, forcing investors into assets that outpace rising prices."
    },
    "deflation": {
        "definition": "A persistent decrease in the general price level of goods and services, often accompanied by slowing economic activity.",
        "example": "Deflation can cause consumers to delay purchases, leading businesses to cut production and lay off workers.",
        "category": "Macroeconomics",
        "why_it_matters": "While cheaper prices sound good, prolonged deflation can spark economic recessions and debt distress."
    },
    "stagflation": {
        "definition": "A toxic economic condition characterized by slow economic growth, high unemployment, and high inflation occurring simultaneously.",
        "example": "The 1970s oil shocks triggered severe stagflation across major developed economies.",
        "category": "Macroeconomics",
        "why_it_matters": "It is central banks' worst nightmare because raising rates to fight inflation worsens unemployment."
    },
    "hyperinflation": {
        "definition": "Rapid, excessive, and out-of-control price increases in an economy, typically exceeding 50% per month.",
        "example": "During hyperinflation in Zimbabwe, prices doubled every few days, rendering local currency worthless.",
        "category": "Macroeconomics",
        "why_it_matters": "Completely destroys trust in fiat currency and causes citizens to flee to gold, foreign currency, or barter."
    },
    "gdp": {
        "definition": "Gross Domestic Product: the total monetary value of all finished goods and services produced within a country during a specific period.",
        "example": "US real GDP expanded at a 2.8% annualized rate last quarter, signaling economic resilience.",
        "category": "Macroeconomics",
        "why_it_matters": "It is the scorecard of a country's economic health; sustained GDP growth typically supports corporate revenue."
    },
    "cpi": {
        "definition": "Consumer Price Index: a benchmark monthly metric tracking the average change over time in prices paid by urban consumers for a market basket of goods.",
        "example": "The Core CPI report excluded volatile food and energy components to measure baseline inflation trends.",
        "category": "Macroeconomics",
        "why_it_matters": "Central banks closely watch CPI data when determining whether to hike, cut, or hold benchmark interest rates."
    },
    "ppi": {
        "definition": "Producer Price Index: a measure of the average change over time in the selling prices received by domestic producers for their output (wholesale inflation).",
        "example": "A higher-than-expected PPI often precedes rising consumer prices as manufacturers pass higher costs to retail buyers.",
        "category": "Macroeconomics",
        "why_it_matters": "Acts as an early leading indicator for future consumer inflation."
    },
    "pce": {
        "definition": "Personal Consumption Expenditures Price Index: the primary metric preferred by the Federal Reserve to gauge inflation and consumer spending behavior.",
        "example": "The Fed targets a 2% Core PCE inflation rate over the longer term.",
        "category": "Macroeconomics",
        "why_it_matters": "Because it adjusts for changes in consumer substitution habits, the Fed treats PCE as its gold standard."
    },
    "interest rates": {
        "definition": "The cost of borrowing money or the reward for saving it, set as a percentage of the total borrowed or invested amount.",
        "example": "When interest rates climb, auto loans and 30-year home mortgages become significantly more expensive.",
        "category": "Interest Rates",
        "why_it_matters": "Interest rates dictate the cost of capital across the entire global financial ecosystem."
    },
    "repo rate": {
        "definition": "The rate at which a country's central bank lends short-term money to commercial banks against government securities.",
        "example": "The Reserve Bank of India (RBI) kept the repo rate unchanged at 6.50% to maintain price stability.",
        "category": "Monetary Policy",
        "why_it_matters": "When repo rates go up, commercial banks raise their loan interest rates (home loans, auto loans, business credit)."
    },
    "reverse repo rate": {
        "definition": "The interest rate at which the central bank borrows money from commercial banks within the country.",
        "example": "Banks park excess overnight liquidity with the central bank via the reverse repo window.",
        "category": "Monetary Policy",
        "why_it_matters": "Absorbs excess liquidity from the banking system to manage currency strength and inflation."
    },
    "federal funds rate": {
        "definition": "The target interest rate set by the FOMC at which US commercial banks borrow and lend their excess reserves to each other overnight.",
        "example": "The Federal Reserve held the federal funds rate in the 5.25%–5.50% corridor.",
        "category": "Monetary Policy",
        "why_it_matters": "Serves as the benchmark for US prime rates, mortgages, corporate loans, and Treasury yields."
    },
    "basis points": {
        "definition": "A standard unit of measure for interest rates and financial percentages. 1 basis point equals 0.01% (or 1/100th of 1%).",
        "example": "A 50 basis point hike means the rate rose by 0.50% (e.g. from 4.00% to 4.50%).",
        "category": "Interest Rates",
        "why_it_matters": "Provides unambiguous clarity when discussing tiny interest rate or bond yield movements."
    },
    "bps": {
        "definition": "Short for basis points. 100 bps = 1.00% interest rate shift.",
        "example": "Yields surged 15 bps following the unexpected employment surge.",
        "category": "Interest Rates",
        "why_it_matters": "Industry shorthand widely used across trading floors and central bank briefings."
    },
    "fomc": {
        "definition": "Federal Open Market Committee: the 12-member committee of the Federal Reserve responsible for setting national monetary policy and interest rates.",
        "example": "Markets rallied as the FOMC statement hinted at upcoming rate cuts.",
        "category": "Monetary Policy",
        "why_it_matters": "Every FOMC meeting and press conference has the power to shift billions of dollars in global markets."
    },
    "hawkish": {
        "definition": "An economic stance favoring higher interest rates and monetary tightening to combat inflation, even if it slows economic growth.",
        "example": "The Fed chairman gave a hawkish speech warning that interest rates must stay higher for longer.",
        "category": "Monetary Policy",
        "why_it_matters": "Hawkish stances usually support currency strength while putting downward pressure on high-growth stock valuations."
    },
    "dovish": {
        "definition": "An economic stance favoring lower interest rates, cheap borrowing, and monetary easing to stimulate employment and economic expansion.",
        "example": "Dovish remarks from central bankers sent tech stocks rallying as borrowing costs were expected to drop.",
        "category": "Monetary Policy",
        "why_it_matters": "Dovish policy tends to boost equities, real estate, and risk assets by expanding liquidity."
    },
    "quantitative easing": {
        "definition": "An unconventional monetary policy where a central bank creates new reserves to buy long-term government bonds, injecting liquidity directly into the economy.",
        "example": "Quantitative easing was heavily deployed in 2008 and 2020 to lower long-term yields and encourage lending.",
        "category": "Monetary Policy",
        "why_it_matters": "Expands central bank balance sheets and pumps huge liquidity into capital markets."
    },
    "quantitative tightening": {
        "definition": "The reversal of QE, where a central bank shrinks its balance sheet by allowing mature bonds to roll off without reinvestment, pulling cash out of the banking system.",
        "example": "Quantitative tightening drains bank reserves and can raise borrowing costs for corporations.",
        "category": "Monetary Policy",
        "why_it_matters": "Tightens liquidity conditions and removes the artificial floor under asset prices."
    },
    "recession": {
        "definition": "A significant, widespread, and prolonged downturn in economic activity, conventionally marked by two consecutive quarters of negative GDP growth.",
        "example": "Consumer confidence plunged and corporate hiring slowed, fueling fears of an impending recession.",
        "category": "Macroeconomics",
        "why_it_matters": "Recessions bring higher unemployment, reduced corporate earnings, and defensive investor rotation."
    },
    "soft landing": {
        "definition": "A rare economic feat where a central bank successfully brings down high inflation by hiking rates without triggering a recession or massive job losses.",
        "example": "Optimists believe resilient consumer spending could allow the economy to achieve a soft landing.",
        "category": "Macroeconomics",
        "why_it_matters": "Preserves jobs and allows stock markets to thrive without enduring the pain of an economic slump."
    },
    "fiscal policy": {
        "definition": "Government decisions regarding taxation, public spending, and borrowing to influence aggregate economic performance.",
        "example": "Large fiscal stimulus packages during downturns boost public infrastructure and consumer subsidies.",
        "category": "Macroeconomics",
        "why_it_matters": "Works alongside monetary policy to shape national debt, consumer demand, and sector growth."
    },
    "monetary policy": {
        "definition": "The actions taken by a nation's central bank to control the overall money supply and achieve economic goals like price stability and maximum employment.",
        "example": "The central bank adopted a restrictive monetary policy stance to curb wage-price spirals.",
        "category": "Monetary Policy",
        "why_it_matters": "Directly controls base interest rates, reserve ratios, and currency circulation."
    },

    # =========================================================================
    # 2. STOCK MARKET, EQUITIES & VALUATION
    # =========================================================================
    "bull market": {
        "definition": "A market condition characterized by sustained rising prices, strong corporate earnings, investor optimism, and economic expansion.",
        "example": "The S&P 500 bull market has gained over 40% from its cyclical low.",
        "category": "Stock Market",
        "why_it_matters": "In a bull market, investor sentiment is positive and broad market indices generate attractive returns."
    },
    "bear market": {
        "definition": "A prolonged period of declining asset prices, traditionally defined as a drop of 20% or more from recent peak highs across major indices.",
        "example": "Tech equities entered a bear market as rising discount rates compressed valuation multiples.",
        "category": "Stock Market",
        "why_it_matters": "Presents severe volatility and emotional panic, but historically offers superior long-term entry points for patient investors."
    },
    "market correction": {
        "definition": "A short-term decline of between 10% and 20% in the price of a stock, bond, commodity, or market index from its recent peak.",
        "example": "After a relentless five-month rally, the benchmark index suffered a healthy 11% market correction.",
        "category": "Stock Market",
        "why_it_matters": "Corrections relieve speculative froth in asset valuations and occur on average every 12 to 18 months."
    },
    "market crash": {
        "definition": "A sudden, dramatic, and steep collapse in stock or asset prices across a major cross-section of the market, often occurring over a few days.",
        "example": "The Black Monday crash of 1987 saw the Dow Jones drop over 22% in a single trading session.",
        "category": "Stock Market",
        "why_it_matters": "Often driven by panic, automated selling algorithms, margin calls, or sudden systemic shocks."
    },
    "market cap": {
        "definition": "Market Capitalization: the total aggregate market dollar value of a publicly traded company's outstanding shares (Share Price × Total Shares).",
        "example": "Microsoft and Apple boast market caps exceeding $3 trillion, categorizing them as mega-cap titans.",
        "category": "Stock Market",
        "why_it_matters": "Used by institutional investors and indices to classify company size, liquidity, and risk profile."
    },
    "large cap": {
        "definition": "Companies with a market capitalization typically of $10 billion or more, known for established market leadership and stability.",
        "example": "Blue-chip stocks like Johnson & Johnson and Berkshire Hathaway are quintessential large-cap companies.",
        "category": "Stock Market",
        "why_it_matters": "Forms the defensive core of most diversified equity portfolios."
    },
    "mid cap": {
        "definition": "Companies with a market capitalization generally between $2 billion and $10 billion, offering a balance between growth potential and corporate stability.",
        "example": "Mid-cap companies often outperform large caps during early-to-mid economic expansions.",
        "category": "Stock Market",
        "why_it_matters": "Provides higher growth potential than mature giants with less volatility than micro caps."
    },
    "small cap": {
        "definition": "Companies with a market capitalization usually between $300 million and $2 billion, often featuring high growth potential alongside higher business volatility.",
        "example": "Small-cap stocks in the Russell 2000 index are more sensitive to domestic borrowing costs.",
        "category": "Stock Market",
        "why_it_matters": "Can generate explosive multi-bagger returns, but carries elevated risk of bankruptcy during economic downturns."
    },
    "p/e ratio": {
        "definition": "Price-to-Earnings Ratio: a fundamental valuation metric calculated by dividing a company's current stock price by its earnings per share (EPS).",
        "example": "If a stock trades at $100 and its annual EPS is $5, its P/E ratio is 20x.",
        "category": "Valuation",
        "why_it_matters": "Tells you how many dollars investors are willing to pay for every dollar of annual company profit."
    },
    "price-to-earnings": {
        "definition": "Alternative name for the P/E ratio, comparing market price per share to corporate profit per share.",
        "example": "Value investors seek companies trading at low price-to-earnings ratios compared to historical peers.",
        "category": "Valuation",
        "why_it_matters": "Helps distinguish between overvalued high-expectation stocks and potentially undervalued bargain investments."
    },
    "peg ratio": {
        "definition": "Price/Earnings-to-Growth Ratio: calculates P/E ratio divided by the projected annual earnings growth rate of the company.",
        "example": "A stock with a P/E of 20 and 20% annual earnings growth has an attractive PEG ratio of 1.0.",
        "category": "Valuation",
        "why_it_matters": "Helps determine whether a high P/E ratio is genuinely justified by rapid underlying corporate expansion."
    },
    "eps": {
        "definition": "Earnings Per Share: a company's net profit divided by the total number of common shares outstanding.",
        "example": "A company with $100 million in profit and 50 million shares has an EPS of $2.00.",
        "category": "Valuation",
        "why_it_matters": "The ultimate bottom-line measure of corporate profitability available to individual equity shareholders."
    },
    "dividend": {
        "definition": "A distribution of a portion of a company's net earnings paid directly to shareholders, commonly distributed in cash on a quarterly basis.",
        "example": "The oil giant declared a quarterly cash dividend of $0.95 per common share.",
        "category": "Investing",
        "why_it_matters": "Provides tangible passive income and reflects stable, mature corporate cash generation."
    },
    "dividend yield": {
        "definition": "The annual dividend payment per share divided by the current stock price, expressed as a percentage.",
        "example": "A $4 annual dividend on a $100 stock gives an attractive dividend yield of 4.0%.",
        "category": "Investing",
        "why_it_matters": "Allows investors to compare cash yields between dividend stocks and fixed deposits or bonds."
    },
    "ipo": {
        "definition": "Initial Public Offering: the first sale of stock by a private company to institutional and retail public investors on a stock exchange.",
        "example": "The cloud software startup raised $1.2 billion through its high-profile Nasdaq IPO.",
        "category": "Stock Market",
        "why_it_matters": "Allows founders and early venture capital backers to monetize equity and raises capital for future growth."
    },
    "stock split": {
        "definition": "A corporate action where a company increases its number of outstanding shares while lowering the price per share proportionally.",
        "example": "In a 10-for-1 split, a $1,000 share becomes 10 shares priced at $100 each; overall investor wealth remains unchanged.",
        "category": "Corporate Finance",
        "why_it_matters": "Enhances liquidity and makes single share prices psychologically more affordable for retail investors."
    },
    "share buyback": {
        "definition": "When a corporation uses its cash reserves to buy back its own shares from the open market, reducing total outstanding shares.",
        "example": "Apple announced an unprecedented $110 billion share repurchase authorization.",
        "category": "Corporate Finance",
        "why_it_matters": "Reduces share count, boosting EPS and signaling management's confidence in the company's valuation."
    },
    "short selling": {
        "definition": "Borrowing shares from a broker to sell them immediately on the market, aiming to repurchase them at a lower price later and pocket the difference.",
        "example": "Short sellers who bet against EV stocks suffered heavy losses during the unexpected earnings surge.",
        "category": "Trading",
        "why_it_matters": "Enables profiting from asset declines, but carries theoretically infinite upside loss potential."
    },
    "short squeeze": {
        "definition": "A rapid surge in a stock's price caused by short sellers scrambling to buy back shares to close out losing positions, forcing the price even higher.",
        "example": "The dramatic retail short squeeze in GameStop caused hedge funds billions in trading losses.",
        "category": "Trading",
        "why_it_matters": "Generates violent upward spikes that catch contrarian short traders off guard."
    },
    "volatility": {
        "definition": "A statistical measure of the dispersion of returns for a given asset or market index, representing the magnitude and speed of price fluctuations.",
        "example": "High implied volatility before earnings announcements causes options contract premiums to expand.",
        "category": "Trading",
        "why_it_matters": "Reflects market uncertainty; higher volatility implies greater risk and potential reward."
    },
    "vix": {
        "definition": "The CBOE Volatility Index: a real-time market index representing the market's expectations for 30-day forward-looking volatility in the S&P 500 (the 'Fear Gauge').",
        "example": "When the VIX spikes above 30, it indicates extreme investor fear and market distress.",
        "category": "Trading",
        "why_it_matters": "Useful contrarian indicator; Warren Buffett's 'be greedy when others are fearful' often correlates with elevated VIX readings."
    },
    "beta": {
        "definition": "A measure of a stock's volatility and systematic risk in comparison to the broader market (where market beta is 1.0).",
        "example": "A high-growth tech stock with a beta of 1.5 tends to move 15% when the overall market moves 10%.",
        "category": "Valuation",
        "why_it_matters": "Helps investors evaluate how aggressively a stock will fluctuate relative to index benchmarks."
    },
    "liquidity": {
        "definition": "The ease and speed with which an asset can be converted into cash without triggering a significant impact on its market price.",
        "example": "Large-cap equities and US Treasuries possess exceptional liquidity, while physical real estate is relatively illiquid.",
        "category": "Markets",
        "why_it_matters": "Illiquid assets can trap capital or force deep discounts when an investor needs fast liquidity."
    },
    "circuit breaker": {
        "definition": "An automatic regulatory mechanism that halts trading across stock exchanges for a specified duration when benchmark indices drop past preset thresholds.",
        "example": "Trading was halted for 15 minutes after the index plunged 7% at market open.",
        "category": "Stock Market",
        "why_it_matters": "Prevents catastrophic market stampedes by giving market participants a cooling-off period to digest breaking news."
    },

    # =========================================================================
    # 3. BONDS & FIXED INCOME
    # =========================================================================
    "bond": {
        "definition": "A fixed-income debt instrument where an investor loans money to a government or corporation that borrows the funds for a defined period at a fixed or variable interest rate.",
        "example": "Municipalities issue municipal bonds to build highways, hospitals, and water systems.",
        "category": "Bonds",
        "why_it_matters": "Provides predictable income, capital preservation, and portfolio ballast against equity crashes."
    },
    "treasury yield": {
        "definition": "The effective annual return earned by an investor on sovereign debt obligations issued by the US government.",
        "example": "The 10-year Treasury yield rose to 4.30%, raising corporate borrowing costs across the economy.",
        "category": "Bonds",
        "why_it_matters": "Regarded as the 'risk-free rate of return', setting the hurdle rate against which all risky investments are judged."
    },
    "treasury bills": {
        "definition": "Short-term US government debt securities with maturities ranging from a few days to 52 weeks (commonly called T-Bills).",
        "example": "Retail investors parked cash in 3-month T-Bills yielding 5.2% annualized.",
        "category": "Bonds",
        "why_it_matters": "Considered the safest cash-equivalent asset backed by the full faith and credit of the government."
    },
    "yield curve": {
        "definition": "A graphical line that plots interest rates (yields) of bonds with equal credit quality across differing maturity horizons (e.g. 1 month to 30 years).",
        "example": "A normal yield curve slopes upwards because investors demand higher yields for locking up money longer.",
        "category": "Bonds",
        "why_it_matters": "The shape of the yield curve reveals market expectations for future economic growth and inflation."
    },
    "yield curve inversion": {
        "definition": "An unusual financial phenomenon where short-term bond yields exceed long-term yields, historically the most reliable warning signal of a looming recession.",
        "example": "When the 2-year Treasury yielded more than the 10-year Treasury, macro analysts flagged recession danger.",
        "category": "Bonds",
        "why_it_matters": "Has preceded nearly every major US economic recession over the past 60 years."
    },
    "coupon rate": {
        "definition": "The fixed annual interest rate paid by a bond issuer to the bondholder, expressed as a percentage of the bond's par or face value.",
        "example": "A bond with a $1,000 face value and a 5% coupon rate pays $50 in annual interest.",
        "category": "Bonds",
        "why_it_matters": "Determines the cash flow yield an investor receives throughout the bond's life."
    },

    # =========================================================================
    # 4. INVESTMENT VEHICLES & STRATEGIES
    # =========================================================================
    "etf": {
        "definition": "Exchange-Traded Fund: an investment fund traded on stock exchanges that holds a diversified basket of assets (stocks, bonds, or commodities).",
        "example": "The SPY ETF tracks the S&P 500 index and trades intraday just like individual stocks.",
        "category": "Investing",
        "why_it_matters": "Offers instant broad diversification, high liquidity, and ultra-low annual expense ratios."
    },
    "index fund": {
        "definition": "A mutual fund or ETF designed to passively replicate the performance of a specific financial market benchmark (e.g. S&P 500, Nifty 50).",
        "example": "Legendary investor Warren Buffett recommends low-cost index funds for all non-professional investors.",
        "category": "Investing",
        "why_it_matters": "Consistently beats 85%+ of actively managed, high-fee funds over a 15-to-20 year investment horizon."
    },
    "mutual fund": {
        "definition": "A financial vehicle that pools money from many retail and institutional investors to purchase a managed portfolio of stocks, bonds, or other securities.",
        "example": "Active mutual funds employ portfolio managers who attempt to outperform market benchmarks.",
        "category": "Investing",
        "why_it_matters": "Allows individuals with small amounts of capital to access professional diversification."
    },
    "sip": {
        "definition": "Systematic Investment Plan: an investment strategy where an investor commits to investing a predetermined fixed sum of money at regular intervals (monthly/weekly).",
        "example": "Setting up a $250 monthly SIP into an index fund automates long-term wealth building.",
        "category": "Investing",
        "why_it_matters": "Eliminates emotional market timing and harnesses dollar-cost averaging effortlessly."
    },
    "dollar cost averaging": {
        "definition": "The practice of investing a fixed dollar amount into a security on a regular schedule, regardless of share price.",
        "example": "By practicing DCA, you automatically buy more shares when prices are depressed and fewer when prices are elevated.",
        "category": "Investing",
        "why_it_matters": "Lowers your average cost per share over time and removes the anxiety of timing market peaks."
    },
    "dca": {
        "definition": "Short acronym for Dollar Cost Averaging, a proven disciplined wealth accumulation method.",
        "example": "DCA is widely recommended for crypto and stock accumulation to navigate volatility.",
        "category": "Investing",
        "why_it_matters": "Disciplines investors to buy consistently through bear markets."
    },
    "compounding": {
        "definition": "The process where the earnings generated by an investment are reinvested to generate their own earnings over time (earning interest on interest).",
        "example": "Albert Einstein famously called compound interest the eighth wonder of the world.",
        "category": "Investing",
        "why_it_matters": "Enables modest monthly savings to multiply into substantial fortunes over several decades."
    },
    "rule of 72": {
        "definition": "A quick mathematical shortcut to estimate the number of years required to double your investment: divide 72 by the annual rate of return.",
        "example": "At an 8% annual return, your money doubles in approximately 9 years (72 / 8 = 9).",
        "category": "Investing",
        "why_it_matters": "Allows instant mental math for evaluating investment opportunities and compounding horizons."
    },
    "asset allocation": {
        "definition": "An investment strategy aimed at balancing risk and reward by dividing a portfolio's capital among major asset classes (equities, bonds, real estate, cash).",
        "example": "A traditional balanced portfolio often uses a 60% equities and 40% fixed income asset allocation.",
        "category": "Investing",
        "why_it_matters": "Determines over 90% of a portfolio's return variability and downside protection."
    },
    "portfolio diversification": {
        "definition": "The risk management technique that mixes a wide variety of investments within a portfolio to limit exposure to any single asset or sector.",
        "example": "'Don't put all your eggs in one basket' is the founding principle of diversification.",
        "category": "Investing",
        "why_it_matters": "Reduces unsystematic risk without sacrificing long-term expected returns."
    },
    "emergency fund": {
        "definition": "A cash reserve specifically set aside to cover unexpected life emergencies, such as job loss, medical bills, or major car repairs.",
        "example": "Financial experts advise keeping 3 to 6 months of baseline living expenses in a liquid high-yield savings account.",
        "category": "Personal Finance",
        "why_it_matters": "Prevents you from having to liquidate investments at a steep loss during sudden market downturns."
    },
    "reit": {
        "definition": "Real Estate Investment Trust: a company that owns, operates, or finances income-producing real estate and trades on public stock exchanges.",
        "example": "By law, US REITs must distribute at least 90% of their taxable income to shareholders as dividends.",
        "category": "Investing",
        "why_it_matters": "Allows retail investors to profit from commercial real estate with small sums and daily liquidity."
    },

    # =========================================================================
    # 5. CORPORATE FINANCE & ACCOUNTING
    # =========================================================================
    "ebitda": {
        "definition": "Earnings Before Interest, Taxes, Depreciation, and Amortization: a metric used to evaluate a company's raw operational performance without financing decisions or accounting methods.",
        "example": "The cloud enterprise firm generated an adjusted EBITDA margin of 32%.",
        "category": "Corporate Finance",
        "why_it_matters": "Provides a clean proxy for core operating cash generation, widely used in acquisitions."
    },
    "balance sheet": {
        "definition": "A core financial statement summarizing a company's assets, liabilities, and shareholders' equity at a specific point in time (Assets = Liabilities + Equity).",
        "example": "A strong balance sheet with substantial cash and minimal short-term debt shields companies during recessions.",
        "category": "Corporate Finance",
        "why_it_matters": "Shows financial solvency, working capital health, and debt obligations."
    },
    "free cash flow": {
        "definition": "The cash a company produces through its operations minus its capital expenditures (investments in physical assets like equipment or factories).",
        "example": "High free cash flow allows firms to pay dividends, repurchase shares, and fund R&D without borrowing.",
        "category": "Corporate Finance",
        "why_it_matters": "The purest indicator of actual discretionary cash generation available to shareholders."
    },
    "fcf": {
        "definition": "Short for Free Cash Flow.",
        "example": "With $10B in annual FCF, the tech leader easily financed its AI infrastructure expansion.",
        "category": "Corporate Finance",
        "why_it_matters": "Discounted Free Cash Flow (DCF) forms the foundation of intrinsic valuation models."
    },
    "roe": {
        "definition": "Return on Equity: a measure of financial performance calculated by dividing net income by shareholders' equity.",
        "example": "A consistent ROE above 15% signifies that management is effectively allocating shareholders' capital.",
        "category": "Corporate Finance",
        "why_it_matters": "Measures corporate profitability efficiency from the perspective of an equity investor."
    },

    # =========================================================================
    # 6. BANKING, PERSONAL FINANCE & CREDIT
    # =========================================================================
    "apr": {
        "definition": "Annual Percentage Rate: the annual cost of borrowing money, including interest and fees charged by lenders.",
        "example": "Credit cards frequently charge an APR of 22% or higher on unpaid monthly balances.",
        "category": "Banking",
        "why_it_matters": "Standardizes the true cost of consumer loans, auto financing, and revolving credit."
    },
    "apy": {
        "definition": "Annual Percentage Yield: the real rate of return earned on a deposit over one year, taking into account the effect of compounding interest.",
        "example": "A high-yield savings account offering 5.0% APY compounded daily yields more than 5.0% simple interest.",
        "category": "Banking",
        "why_it_matters": "Crucial for comparing savings accounts, certificates of deposit, and money market funds."
    },
    "credit score": {
        "definition": "A numerical expression (typically 300 to 850) based on an analysis of a person's credit files, representing creditworthiness.",
        "example": "Maintaining a credit score above 750 qualifies borrowers for the lowest interest rates on home mortgages.",
        "category": "Banking",
        "why_it_matters": "Dictates your eligibility and pricing for mortgages, car loans, rental apartments, and insurance."
    },
    "cibil score": {
        "definition": "India's premier 3-digit credit score (ranging between 300 and 900) calculated by TransUnion CIBIL based on repayment history.",
        "example": "Indian banks typically look for a CIBIL score of 750 or higher when approving unsecured personal loans.",
        "category": "Banking",
        "why_it_matters": "Critical metric in Indian banking for loan approvals and credit card issuances."
    },
    "fixed deposit": {
        "definition": "A financial instrument provided by banks that provides investors a higher rate of interest than regular savings accounts until a fixed maturity date.",
        "example": "Senior citizens often lock in 1-year bank Fixed Deposits (FDs) for guaranteed quarterly interest.",
        "category": "Banking",
        "why_it_matters": "Offers guaranteed, risk-free capital preservation with predictable income."
    },
    "fd": {
        "definition": "Short for Fixed Deposit.",
        "example": "Many conservative investors prefer bank FDs to avoid stock market volatility.",
        "category": "Banking",
        "why_it_matters": "Popular savings tool in India and emerging markets."
    },

    # =========================================================================
    # 7. DERIVATIVES & TRADING
    # =========================================================================
    "options": {
        "definition": "Financial derivatives that give the buyer the right, but not the obligation, to buy (Call) or sell (Put) an underlying asset at an agreed price within a specific timeframe.",
        "example": "Traders use options contracts to hedge their stock portfolios against sudden price crashes.",
        "category": "Derivatives",
        "why_it_matters": "Provides tremendous leverage and risk hedging capabilities, but can expire completely worthless."
    },
    "call option": {
        "definition": "A contract that gives the holder the right to buy an underlying asset at a specified strike price prior to expiration.",
        "example": "Buying a call option is a bullish bet that the stock price will rise above the strike price.",
        "category": "Derivatives",
        "why_it_matters": "Allows upside equity participation with limited upfront capital."
    },
    "put option": {
        "definition": "A contract that gives the holder the right to sell an underlying asset at a specified strike price prior to expiration.",
        "example": "Portfolio managers purchase put options as insurance against a market downturn.",
        "category": "Derivatives",
        "why_it_matters": "Acts as portfolio disaster insurance or an instrument to profit from falling prices."
    },
    "leverage": {
        "definition": "The use of borrowed capital or financial derivatives to increase the potential return of an investment.",
        "example": "Trading with 10x leverage magnifies both your percentage gains and your percentage losses ten-fold.",
        "category": "Trading",
        "why_it_matters": "A double-edged sword that can wipe out an entire trading account in a matter of seconds."
    },

    # =========================================================================
    # 8. CRYPTOCURRENCY & DIGITAL ASSETS
    # =========================================================================
    "cryptocurrency": {
        "definition": "A digital or virtual currency that is secured by cryptography, operating on decentralized peer-to-peer networks.",
        "example": "Bitcoin and Ethereum are the two largest cryptocurrencies by market capitalization.",
        "category": "Cryptocurrency",
        "why_it_matters": "Enables borderless, censorship-resistant transfers of value without central intermediaries."
    },
    "bitcoin": {
        "definition": "The first decentralized peer-to-peer digital currency created in 2009 by pseudonymous creator Satoshi Nakamoto, with a capped supply of 21 million coins.",
        "example": "Spot Bitcoin ETFs have brought hundreds of millions in institutional inflows.",
        "category": "Cryptocurrency",
        "why_it_matters": "Often viewed as 'Digital Gold' due to its strict mathematical scarcity and decentralization."
    },
    "ethereum": {
        "definition": "A decentralized open-source blockchain network featuring smart contract functionality, powered by its native cryptocurrency Ether (ETH).",
        "example": "Ethereum serves as the foundational operating layer for decentralized finance (DeFi) and NFTs.",
        "category": "Cryptocurrency",
        "why_it_matters": "Pioneered programmable money and decentralized internet applications."
    },
    "blockchain": {
        "definition": "A distributed, immutable digital ledger of transactions maintained by a consensus of computers across a network.",
        "example": "Transactions recorded on a blockchain cannot be modified or deleted retroactively.",
        "category": "Cryptocurrency",
        "why_it_matters": "Eliminates the need for trusted third-party verification in digital transactions."
    },
    "bitcoin halving": {
        "definition": "An event occurring every 210,000 blocks (roughly every 4 years) where the reward paid to Bitcoin miners for verifying transactions is cut by 50%.",
        "example": "The 2024 halving reduced the block reward from 6.25 BTC to 3.125 BTC.",
        "category": "Cryptocurrency",
        "why_it_matters": "Constrains new supply issuance, historically serving as a major multi-month catalyst for bull cycles."
    },

    # =========================================================================
    # 9. COMMODITIES & CURRENCIES
    # =========================================================================
    "gold": {
        "definition": "A precious metal and monetary commodity that has served as a universal store of value and safe-haven asset for over 5,000 years.",
        "example": "Gold hit fresh record highs as investors sought refuge from inflation and geopolitical conflicts.",
        "category": "Commodities",
        "why_it_matters": "Non-yielding asset that cannot be printed by governments, offering protection against currency debasement."
    },
    "crude oil": {
        "definition": "A naturally occurring unrefined petroleum product, refined into gasoline, diesel, and petrochemicals; the lifeblood of global industrial transit.",
        "example": "Rising crude oil prices directly increase logistics costs, feeding into headline consumer inflation.",
        "category": "Commodities",
        "why_it_matters": "Global energy costs directly dictate manufacturing and transport inflation worldwide."
    },
    "brent crude": {
        "definition": "A major trading classification and international benchmark for sweet light crude oil extracted from the North Sea.",
        "example": "Brent crude oil traded near $80 per barrel amid shipping disruptions in the Red Sea.",
        "category": "Commodities",
        "why_it_matters": "Used to price more than two-thirds of the world's internationally traded crude oil supplies."
    },
    "wti": {
        "definition": "West Texas Intermediate: a high-quality, sweet, light crude oil that serves as the benchmark for US petroleum pricing.",
        "example": "WTI crude futures settle daily on the New York Mercantile Exchange (NYMEX).",
        "category": "Commodities",
        "why_it_matters": "Primary pricing standard for American energy production and refining margins."
    },

    # =========================================================================
    # 10. INDIAN FINANCIAL MARKETS
    # =========================================================================
    "nifty 50": {
        "definition": "The flagship benchmark stock index of the National Stock Exchange of India (NSE), tracking the 50 largest and most liquid Indian blue-chip companies.",
        "example": "The Nifty 50 scaled past 25,000 points powered by banking and automobile heavyweights.",
        "category": "Indian Markets",
        "why_it_matters": "Represents the pulse of India's formal corporate economy and is the world's most traded index derivative."
    },
    "sensex": {
        "definition": "The benchmark index of the Bombay Stock Exchange (BSE), tracking 30 well-established, financially sound companies across key sectors.",
        "example": "The BSE Sensex is India's oldest stock index, established in 1986.",
        "category": "Indian Markets",
        "why_it_matters": "The most widely quoted barometer of Indian stock market wealth and sentiment."
    },
    "sebi": {
        "definition": "Securities and Exchange Board of India: the statutory regulatory body governing securities and commodity markets in India.",
        "example": "SEBI issued new disclosure guidelines to protect retail investors in futures and options trading.",
        "category": "Indian Markets",
        "why_it_matters": "Protects investor interests, promotes fair market development, and regulates brokers, mutual funds, and exchanges."
    },
    "rbi": {
        "definition": "Reserve Bank of India: India's central banking institution that controls the monetary policy of the Indian rupee.",
        "example": "The RBI Monetary Policy Committee maintained an accommodative-to-neutral monetary stance.",
        "category": "Indian Markets",
        "why_it_matters": "Controls inflation, manages forex reserves, regulates commercial banking, and oversees India's digital payment rails (UPI)."
    },
    "demat account": {
        "definition": "Dematerialized Account: an electronic account used in India to hold shares and securities in electronic format instead of physical paper certificates.",
        "example": "To trade Indian equities, an investor needs a Demat account linked to their trading and bank accounts.",
        "category": "Indian Markets",
        "why_it_matters": "Provides safe, seamless, paperless settlement of equity ownership maintained by NSDL and CDSL."
    }
}

class GlossaryService:
    @staticmethod
    def get_all_terms() -> List[GlossaryTerm]:
        results = []
        for term, data in GLOSSARY_DATABASE.items():
            results.append(GlossaryTerm(
                term=term.title(),
                definition=data["definition"],
                example=data["example"],
                category=data["category"]
            ))
        return sorted(results, key=lambda x: x.term)

    @staticmethod
    def find_jargon_in_text(text: str) -> List[JargonItem]:
        if not text:
            return []
        
        found = []
        lower_text = text.lower()
        
        # Sort keys by length descending to match longer terms first (e.g., "quantitative easing" before "easing")
        sorted_keys = sorted(GLOSSARY_DATABASE.keys(), key=len, reverse=True)
        seen = set()

        for term in sorted_keys:
            # Word boundary regex search
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, lower_text):
                if term not in seen:
                    data = GLOSSARY_DATABASE[term]
                    found.append(JargonItem(
                        term=term.title(),
                        definition=data["definition"],
                        in_text=f"Appears in text: '{term}'"
                    ))
                    seen.add(term)

        return found[:8] # return top detected terms
