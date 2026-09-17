// FinNews AI Frontend Controller with Multilingual Audio & UI Localization
let currentCategory = "all";
let currentLanguage = "English";
let currentArticles = [];
let savedBookmarks = JSON.parse(localStorage.getItem("finnews_bookmarks") || "[]");
let glossaryData = [];
let chatHistory = [];
let selectedArticle = null;

const LANG_CONFIG = {
    "English": {
        code: "en-US",
        speechPrefix: "en",
        playingMsg: "🔊 Playing audio narration in English...",
        searchPlaceholder: "Search news topics, stocks, crypto (e.g. Powell, AI, Bitcoin, Treasury)...",
        tabs: {
            all: "🔥 All News",
            fed_macro: "🏛️ Fed & Economy",
            tech_stocks: "💻 Tech Stocks & AI",
            crypto: "🪙 Crypto & Web3",
            commodities: "🛢️ Commodities",
            banking: "🏦 Banking & Credit",
            custom: "✍️ Paste Custom Article"
        },
        readBreakdown: "📖 Read Breakdown",
        simplifiedView: "✨ Simplified View",
        originalNews: "📰 Original News",
        whatHappened: "📌 What Happened:",
        whyItMatters: "💡 Why It Matters to You:",
        marketImpact: "📊 Market & Dollar Impact:",
        keyTakeaways: "Key Takeaways:",
        jargonHeader: "💡 Financial Terms Explained (Hover to read):",
        modalListen: "🔊 Listen to Audio Breakdown",
        modalStop: "⏹️ Stop Audio"
    },
    "Hindi": {
        code: "hi-IN",
        speechPrefix: "hi",
        playingMsg: "🔊 हिन्दी में ऑडियो विवरण सुनाया जा रहा है...",
        searchPlaceholder: "समाचार, शेयर बाजार, क्रिप्टो खोजें (जैसे पावेल, एआई, बिटकॉइन)...",
        tabs: {
            all: "🔥 सभी समाचार",
            fed_macro: "🏛️ फेड व अर्थव्यवस्था",
            tech_stocks: "💻 टेक शेयर व एआई",
            crypto: "🪙 क्रिप्टो व वेब3",
            commodities: "🛢️ कमोडिटी व तेल",
            banking: "🏦 बैंकिंग व ऋण",
            custom: "✍️ अपना लेख पेस्ट करें"
        },
        readBreakdown: "📖 पूरा विश्लेषण पढ़ें",
        simplifiedView: "✨ सरल सारांश",
        originalNews: "📰 मूल समाचार",
        whatHappened: "📌 क्या हुआ:",
        whyItMatters: "💡 आपके लिए क्यों महत्वपूर्ण है:",
        marketImpact: "📊 बाजार व वित्तीय प्रभाव:",
        keyTakeaways: "मुख्य निष्कर्ष:",
        jargonHeader: "💡 वित्तीय शब्दों की सरल व्याख्या (होवर करें):",
        modalListen: "🔊 ऑडियो सारांश सुनें",
        modalStop: "⏹️ ऑडियो रोकें"
    },
    "Marathi": {
        code: "mr-IN",
        speechPrefix: "mr",
        playingMsg: "🔊 मराठीत ऑडिओ सारांश ऐकवला जात आहे...",
        searchPlaceholder: "बातम्या, शेअर्स, क्रिप्टो शोधा (उदा. पॉवेल, एआय, बिटकॉइन)...",
        tabs: {
            all: "🔥 सर्व बातम्या",
            fed_macro: "🏛️ फेड व अर्थव्यवस्था",
            tech_stocks: "💻 टेक शेअर्स व एआय",
            crypto: "🪙 क्रिप्टो व वेब3",
            commodities: "🛢️ कमोडिटीज व तेल",
            banking: "🏦 बँकिंग व कर्ज",
            custom: "✍️ स्वतःचा लेख पेस्ट करा"
        },
        readBreakdown: "📖 संपूर्ण विश्लेषण वाचा",
        simplifiedView: "✨ सोपा सारांश",
        originalNews: "📰 मूळ बातमी",
        whatHappened: "📌 काय घडले:",
        whyItMatters: "💡 आपल्यासाठी का महत्त्वाचे आहे:",
        marketImpact: "📊 बाजारावर परिणाम:",
        keyTakeaways: "मुख्य मुद्दे:",
        jargonHeader: "💡 आर्थिक संज्ञांचे स्पष्टीकरण (होव्हर करा):",
        modalListen: "🔊 ऑडिओ सारांश ऐका",
        modalStop: "⏹️ ऑडिओ थांबवा"
    },
    "Spanish": {
        code: "es-ES",
        speechPrefix: "es",
        playingMsg: "🔊 Reproduciendo narración en español...",
        searchPlaceholder: "Buscar noticias, acciones, cripto (ej. Powell, IA, Bitcoin)...",
        tabs: {
            all: "🔥 Todas las Noticias",
            fed_macro: "🏛️ Fed y Economía",
            tech_stocks: "💻 Acciones Tech e IA",
            crypto: "🪙 Cripto y Web3",
            commodities: "🛢️ Materias Primas",
            banking: "🏦 Banca y Crédito",
            custom: "✍️ Pegar Artículo"
        },
        readBreakdown: "📖 Leer Desglose",
        simplifiedView: "✨ Vista Simplificada",
        originalNews: "📰 Noticia Original",
        whatHappened: "📌 Qué Sucedió:",
        whyItMatters: "💡 Por Qué Te Importa:",
        marketImpact: "📊 Impacto en el Mercado:",
        keyTakeaways: "Puntos Clave:",
        jargonHeader: "💡 Términos Financieros Explicados:",
        modalListen: "🔊 Escuchar Desglose en Audio",
        modalStop: "⏹️ Detener Audio"
    },
    "French": {
        code: "fr-FR",
        speechPrefix: "fr",
        playingMsg: "🔊 Lecture audio en français...",
        searchPlaceholder: "Rechercher actualités, actions, crypto (ex. Powell, IA, Bitcoin)...",
        tabs: {
            all: "🔥 Toutes les Actualités",
            fed_macro: "🏛️ Fed & Économie",
            tech_stocks: "💻 Actions Tech & IA",
            crypto: "🪙 Crypto & Web3",
            commodities: "🛢️ Matières Premières",
            banking: "🏦 Banques & Crédit",
            custom: "✍️ Coller un Article"
        },
        readBreakdown: "📖 Lire l'Analyse",
        simplifiedView: "✨ Vue Simplifiée",
        originalNews: "📰 Actualité d'Origine",
        whatHappened: "📌 Ce qui s'est passé :",
        whyItMatters: "💡 Pourquoi c'est important :",
        marketImpact: "📊 Impact sur les Marchés :",
        keyTakeaways: "Points Clés :",
        jargonHeader: "💡 Termes Financiers Expliqués :",
        modalListen: "🔊 Écouter l'Analyse Audio",
        modalStop: "⏹️ Arrêter l'Audio"
    },
    "German": {
        code: "de-DE",
        speechPrefix: "de",
        playingMsg: "🔊 Audiowiedergabe auf Deutsch...",
        searchPlaceholder: "Nachrichten, Aktien, Krypto suchen (z. B. Powell, KI, Bitcoin)...",
        tabs: {
            all: "🔥 Alle Nachrichten",
            fed_macro: "🏛️ Fed & Konjunktur",
            tech_stocks: "💻 Tech-Aktien & KI",
            crypto: "🪙 Krypto & Web3",
            commodities: "🛢️ Rohstoffe",
            banking: "🏦 Banken & Kredite",
            custom: "✍️ Eigenen Text einfügen"
        },
        readBreakdown: "📖 Analyse lesen",
        simplifiedView: "✨ Vereinfachte Ansicht",
        originalNews: "📰 Originalmeldung",
        whatHappened: "📌 Was geschehen ist:",
        whyItMatters: "💡 Warum es wichtig ist:",
        marketImpact: "📊 Marktwirkung:",
        keyTakeaways: "Kernelemente:",
        jargonHeader: "💡 Finanzbegriffe verständlich erklärt:",
        modalListen: "🔊 Audioanalyse anhören",
        modalStop: "⏹️ Audio anhalten"
    }
};

// Preload browser speech voices
if (typeof window !== "undefined" && window.speechSynthesis) {
    window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.getVoices();
    };
}

document.addEventListener("DOMContentLoaded", () => {
    initApp();
});

async function initApp() {
    const savedLang = localStorage.getItem("finnews_lang");
    if (savedLang && LANG_CONFIG[savedLang]) {
        currentLanguage = savedLang;
        const langSelect = document.getElementById("lang-select");
        if (langSelect) langSelect.value = savedLang;
    }
    updateUILanguage(currentLanguage);

    setupEventListeners();
    setupChatbot();
    setupArticleModal();
    setupScrollNavigation();
    loadGlossary();
    checkSettingsStatus();
    loadNews();
}

function updateUILanguage(lang) {
    const cfg = LANG_CONFIG[lang] || LANG_CONFIG["English"];

    const searchInput = document.getElementById("search-input");
    if (searchInput) searchInput.placeholder = cfg.searchPlaceholder;

    document.querySelectorAll(".tab-btn").forEach(tab => {
        const cat = tab.dataset.category;
        if (cat && cfg.tabs[cat]) {
            tab.innerText = cfg.tabs[cat];
        }
    });

    const modalSpeakBtn = document.getElementById("modal-btn-speak");
    if (modalSpeakBtn && !modalSpeakBtn.classList.contains("speaking")) {
        modalSpeakBtn.innerHTML = cfg.modalListen;
    }
}

/* ================= SPEECH SYNTHESIS / AUDIO PLAYER ================= */
let currentAudioPlayer = null;

function playArticleAudio(art, btn = null) {
    if (!art) return;

    const cfg = LANG_CONFIG[currentLanguage] || LANG_CONFIG["English"];

    // 1. If an HTML5 Audio stream is currently playing, stop it
    if (currentAudioPlayer) {
        currentAudioPlayer.pause();
        currentAudioPlayer = null;
        if (btn) {
            btn.classList.remove("speaking");
            btn.innerHTML = btn.id === "modal-btn-speak" ? (cfg.modalListen || "🔊 Listen to Audio Breakdown") : "🔊";
        }
        showToast("Audio playback stopped.");
        return;
    }

    // 2. If browser speech synthesis is playing, cancel it
    if (window.speechSynthesis && window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        if (btn) {
            btn.classList.remove("speaking");
            btn.innerHTML = btn.id === "modal-btn-speak" ? (cfg.modalListen || "🔊 Listen to Audio Breakdown") : "🔊";
        }
        showToast("Audio playback stopped.");
        return;
    }

    // Spoken text is built directly in the active language
    const title = art.title || "";
    const summary = art.simplified_summary || art.description || "";
    const textToSpeak = `${title}. ${summary}`.trim();

    const resetButton = () => {
        currentAudioPlayer = null;
        if (btn) {
            btn.classList.remove("speaking");
            btn.innerHTML = btn.id === "modal-btn-speak" ? (cfg.modalListen || "🔊 Listen to Audio Breakdown") : "🔊";
        }
    };

    function chunkTextForTTS(text, maxLen = 160) {
        const clean = text.replace(/\s+/g, ' ').trim();
        if (clean.length <= maxLen) return [clean];
        const sentences = clean.split(/([।\.!\?;\,\n]+)/);
        const tokens = [];
        for (let i = 0; i < sentences.length - 1; i += 2) {
            tokens.push(sentences[i] + sentences[i+1]);
        }
        if (sentences.length % 2 === 1 && sentences[sentences.length - 1]) {
            tokens.push(sentences[sentences.length - 1]);
        }
        const chunks = [];
        let cur = "";
        for (const token of tokens) {
            const t = token.trim();
            if (!t) continue;
            if (t.length > maxLen) {
                const words = t.split(" ");
                for (const w of words) {
                    if (!w) continue;
                    if ((cur + " " + w).trim().length <= maxLen) {
                        cur = (cur + " " + w).trim();
                    } else {
                        if (cur) chunks.push(cur);
                        cur = w;
                    }
                }
            } else if ((cur + " " + t).trim().length <= maxLen) {
                cur = (cur + " " + t).trim();
            } else {
                if (cur) chunks.push(cur);
                cur = t;
            }
        }
        if (cur) chunks.push(cur);
        return chunks.length > 0 ? chunks : [clean.slice(0, maxLen)];
    }

    function playStreamChunks(chunks, ttsLang, onComplete, onFail) {
        if (!chunks || chunks.length === 0) {
            resetButton();
            if (onComplete) onComplete();
            return;
        }

        let idx = 0;
        if (btn) {
            btn.classList.add("speaking");
            btn.innerHTML = btn.id === "modal-btn-speak" ? (cfg.modalStop || "⏹️ Stop Audio") : "⏹️";
        }
        showToast(cfg.playingMsg);

        function playNext() {
            if (idx >= chunks.length) {
                resetButton();
                if (onComplete) onComplete();
                return;
            }
            const chunk = chunks[idx++];
            const url = `https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=${encodeURIComponent(ttsLang)}&q=${encodeURIComponent(chunk)}`;
            const audio = new Audio(url);
            currentAudioPlayer = audio;

            audio.onended = () => {
                playNext();
            };
            audio.onerror = (err) => {
                console.warn("Direct TTS chunk playback error:", err);
                currentAudioPlayer = null;
                if (onFail) onFail();
                else resetButton();
            };
            audio.play().catch(err => {
                console.warn("Audio play blocked or stream error:", err);
                currentAudioPlayer = null;
                if (onFail) onFail();
                else resetButton();
            });
        }

        playNext();
    }

    function playWithBrowserSpeech(text, langCode, onComplete, onFail) {
        if (!window.speechSynthesis) {
            if (onFail) onFail();
            return;
        }
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = langCode;
        utterance.rate = 0.95;

        const voices = window.speechSynthesis.getVoices();
        if (voices && voices.length > 0) {
            const exactMatch = voices.find(v => v.lang === langCode);
            const prefix = langCode.split("-")[0].toLowerCase();
            const prefixMatch = voices.find(v => v.lang.toLowerCase().startsWith(prefix) || v.lang.replace('_', '-').toLowerCase().startsWith(prefix));
            if (exactMatch) utterance.voice = exactMatch;
            else if (prefixMatch) utterance.voice = prefixMatch;
        }

        if (btn) {
            btn.classList.add("speaking");
            btn.innerHTML = btn.id === "modal-btn-speak" ? (cfg.modalStop || "⏹️ Stop Audio") : "⏹️";
        }

        utterance.onend = () => {
            resetButton();
            if (onComplete) onComplete();
        };
        utterance.onerror = (e) => {
            console.warn("Browser speech error:", e);
            resetButton();
            if (onFail) onFail();
        };

        window.speechSynthesis.speak(utterance);
        showToast(cfg.playingMsg);
    }

    const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
    const shortLang = cfg.speechPrefix || "en";

    if (btn) {
        btn.classList.add("speaking");
        btn.innerHTML = btn.id === "modal-btn-speak" ? "⏳ Loading audio..." : "⏳";
    }

    // Branch 1: If on localhost, attempt high-fidelity server TTS first
    if (isLocalhost) {
        const ttsUrl = `/api/tts?text=${encodeURIComponent(textToSpeak.slice(0, 600))}&lang=${encodeURIComponent(shortLang)}`;
        const audio = new Audio(ttsUrl);
        currentAudioPlayer = audio;

        audio.onplay = () => {
            if (btn) btn.innerHTML = btn.id === "modal-btn-speak" ? (cfg.modalStop || "⏹️ Stop Audio") : "⏹️";
            showToast(cfg.playingMsg);
        };
        audio.onended = resetButton;
        audio.onerror = () => {
            console.warn("Local /api/tts unavailable, falling back to direct stream chunks...");
            currentAudioPlayer = null;
            const chunks = chunkTextForTTS(textToSpeak, 160);
            playStreamChunks(chunks, shortLang, null, () => {
                playWithBrowserSpeech(textToSpeak, cfg.code, null, () => {
                    resetButton();
                    showToast("Audio playback issue. Please try again.");
                });
            });
        };
        audio.play().catch(audio.onerror);
        return;
    }

    // Branch 2: On Firebase static CDN, use direct chunked Google TTS streaming
    // with graceful fallback to browser Web Speech API
    const chunks = chunkTextForTTS(textToSpeak, 160);
    playStreamChunks(chunks, shortLang, null, () => {
        playWithBrowserSpeech(textToSpeak, cfg.code, null, () => {
            resetButton();
            showToast("Audio playback issue. Please try again.");
        });
    });
}

/* ================= AUTHENTICATION REMOVED (OPEN ACCESS) ================= */

/* ================= SIDEBAR SCROLL NAVIGATION DOCK (ONLY ONE TOP & ONE BOTTOM) ================= */
function setupScrollNavigation() {
    const btnTop = document.getElementById("btn-scroll-top");
    const btnBottom = document.getElementById("btn-scroll-bottom");
    if (!btnTop && !btnBottom) return;

    function updateScrollState() {
        const scrollY = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
        const windowHeight = window.innerHeight || document.documentElement.clientHeight;
        const docHeight = Math.max(
            document.body.scrollHeight, document.documentElement.scrollHeight,
            document.body.offsetHeight, document.documentElement.offsetHeight,
            document.body.clientHeight, document.documentElement.clientHeight
        );

        const distanceToBottom = docHeight - (scrollY + windowHeight);
        const isNearBottom = scrollY > 250 && (scrollY > (docHeight - windowHeight) * 0.4 || distanceToBottom < 450);

        if (btnTop && btnBottom) {
            if (isNearBottom) {
                btnTop.classList.add("active-target");
                btnBottom.classList.remove("active-target");
            } else {
                btnBottom.classList.add("active-target");
                btnTop.classList.remove("active-target");
            }
        }
    }

    if (btnTop) {
        btnTop.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    if (btnBottom) {
        btnBottom.addEventListener("click", () => {
            const footer = document.getElementById("app-footer");
            if (footer) {
                footer.scrollIntoView({ behavior: "smooth", block: "end" });
            } else {
                window.scrollTo({ top: document.documentElement.scrollHeight, behavior: "smooth" });
            }
        });
    }

    window.addEventListener("scroll", updateScrollState, { passive: true });
    window.addEventListener("resize", updateScrollState, { passive: true });
    updateScrollState();
}

/* ================= ARTICLE DETAIL READER MODAL ================= */
function setupArticleModal() {
    const modal = document.getElementById("article-modal");
    const closeBtn = document.getElementById("close-article-modal");
    closeBtn.addEventListener("click", () => modal.classList.remove("active"));

    // Audio in modal
    document.getElementById("modal-btn-speak").addEventListener("click", () => {
        if (!selectedArticle) return;
        const btn = document.getElementById("modal-btn-speak");
        playArticleAudio(selectedArticle, btn);
    });

    // Copy in modal
    document.getElementById("modal-btn-copy").addEventListener("click", () => {
        if (!selectedArticle) return;
        const text = `📰 ${selectedArticle.title}\n\n✨ Simplified Summary:\n${selectedArticle.simplified_summary}\n\n📌 What Happened:\n${selectedArticle.what_happened}\n\n💡 Why It Matters:\n${selectedArticle.why_it_matters}\n\n📊 Market Impact:\n${selectedArticle.market_impact}`;
        navigator.clipboard.writeText(text);
        showToast("Summary copied to clipboard!");
    });
}

function openArticleModal(art) {
    selectedArticle = art;
    const modal = document.getElementById("article-modal");
    const cfg = LANG_CONFIG[currentLanguage] || LANG_CONFIG["English"];

    document.getElementById("modal-article-source").innerText = art.source;
    document.getElementById("modal-article-date").innerText = art.published_at;
    
    const sentTag = document.getElementById("modal-article-sentiment");
    sentTag.className = `sentiment-tag sentiment-${art.sentiment}`;
    sentTag.innerText = art.sentiment === "bullish" ? "▲ Bullish" : (art.sentiment === "bearish" ? "▼ Bearish" : "◼ Neutral");

    const img = document.getElementById("modal-article-img");
    img.src = art.url_to_image || "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&auto=format&fit=crop&q=60";
    img.onerror = () => { img.src = "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&auto=format&fit=crop&q=60"; };

    document.getElementById("modal-article-title").innerText = art.title;
    document.getElementById("modal-simplified-text").innerText = art.simplified_summary || art.description;
    document.getElementById("modal-what-happened").innerText = art.what_happened || art.description;
    document.getElementById("modal-why-it-matters").innerText = art.why_it_matters || "Relevant for borrowing costs and investment portfolios.";
    document.getElementById("modal-market-impact").innerText = art.market_impact || "Influences sector valuations and asset allocation.";

    const takeawaysList = document.getElementById("modal-takeaways-list");
    takeawaysList.innerHTML = (art.key_takeaways || []).map(t => `<li>${escapeHTML(t)}</li>`).join("");

    const jargonCloud = document.getElementById("modal-jargon-cloud");
    jargonCloud.innerHTML = (art.jargon_terms || []).map(j => `
        <span class="jargon-chip" title="${escapeHTML(j.definition)}">📖 ${escapeHTML(j.term)}</span>
    `).join("");

    document.getElementById("modal-original-text").innerText = art.content || art.description || art.title;

    const openOrigBtn = document.getElementById("modal-btn-open-original");
    openOrigBtn.href = art.url || "#";
    openOrigBtn.innerText = `🔗 Open Original Article on ${art.source} ↗`;

    const whatHappenedLabel = document.querySelector("#modal-what-happened")?.previousElementSibling;
    if (whatHappenedLabel && cfg.whatHappened) whatHappenedLabel.innerText = cfg.whatHappened;

    const whyMattersLabel = document.querySelector("#modal-why-it-matters")?.previousElementSibling;
    if (whyMattersLabel && cfg.whyItMatters) whyMattersLabel.innerText = cfg.whyItMatters;

    const marketImpactLabel = document.querySelector("#modal-market-impact")?.previousElementSibling;
    if (marketImpactLabel && cfg.marketImpact) marketImpactLabel.innerText = cfg.marketImpact;

    const modalSpeakBtn = document.getElementById("modal-btn-speak");
    if (modalSpeakBtn) {
        modalSpeakBtn.classList.remove("speaking");
        modalSpeakBtn.innerHTML = cfg.modalListen;
    }

    modal.classList.add("active");
}

/* ================= PERSONAL CHATBOT (FINBOT) ================= */
function setupChatbot() {
    const chatBtn = document.getElementById("btn-toggle-chatbot");
    const chatWindow = document.getElementById("chatbot-window");
    const closeBtn = document.getElementById("btn-close-chatbot");
    const clearBtn = document.getElementById("btn-clear-chat");
    const sendBtn = document.getElementById("btn-chat-send");
    const chatInput = document.getElementById("chat-input");
    const heroChatBtn = document.getElementById("btn-hero-chat");

    const toggleChat = () => {
        chatWindow.classList.toggle("open");
        if (chatWindow.classList.contains("open")) {
            chatInput.focus();
        }
    };

    chatBtn.addEventListener("click", toggleChat);
    closeBtn.addEventListener("click", () => chatWindow.classList.remove("open"));
    
    if (heroChatBtn) {
        heroChatBtn.addEventListener("click", () => {
            chatWindow.classList.add("open");
            chatInput.focus();
        });
    }

    clearBtn.addEventListener("click", () => {
        const messagesContainer = document.getElementById("chat-messages");
        messagesContainer.innerHTML = `
            <div class="chat-msg bot-msg">
                <div class="msg-bubble">
                    👋 Chat cleared. Ask FinBot anything about today's market news, complex terminology, or economic trends!
                </div>
            </div>
        `;
        chatHistory = [];
        showToast("Chat history cleared.");
    });

    sendBtn.addEventListener("click", sendUserChatMessage);
    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            sendUserChatMessage();
        }
    });

    document.getElementById("chat-quick-chips").addEventListener("click", (e) => {
        const chip = e.target.closest(".chip-btn");
        if (chip) {
            const query = chip.dataset.query || chip.innerText.trim();
            chatInput.value = query;
            sendUserChatMessage();
        }
    });
}

async function sendUserChatMessage() {
    const input = document.getElementById("chat-input");
    const text = input.value.trim();
    if (!text) return;

    input.value = "";
    appendChatMessage("user", text);
    chatHistory.push({ sender: "user", text: text });

    const typingId = "msg-typing-" + Date.now();
    const messagesContainer = document.getElementById("chat-messages");
    const typingBubble = document.createElement("div");
    typingBubble.className = "chat-msg bot-msg";
    typingBubble.id = typingId;
    typingBubble.innerHTML = `
        <div class="msg-bubble" style="color: var(--text-muted); font-style: italic;">
            <span class="spinner" style="display: inline-block; width: 12px; height: 12px; border-width: 2px; vertical-align: middle; margin-right: 6px;"></span>
            FinBot is analyzing...
        </div>
    `;
    messagesContainer.appendChild(typingBubble);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: text,
                history: chatHistory.slice(-6)
            })
        });
        const ct = res.headers.get("content-type") || "";
        if (!res.ok || !ct.includes("application/json")) {
            throw new Error("Local API unavailable, falling back to direct Gemini AI");
        }
        const data = await res.json();
        
        const el = document.getElementById(typingId);
        if (el) el.remove();

        appendChatMessage("bot", data.reply);
        chatHistory.push({ sender: "bot", text: data.reply });

        if (data.suggested_questions && data.suggested_questions.length > 0) {
            const chipsContainer = document.getElementById("chat-quick-chips");
            chipsContainer.innerHTML = data.suggested_questions.map(q => `
                <button class="chip-btn" data-query="${escapeHTML(q)}">${escapeHTML(q)}</button>
            `).join("");
        }
    } catch (err) {
        let clientResp;
        try {
            // Live Google Gemini 3.6 Flash AI in browser!
            clientResp = await callGeminiDirectly(text, chatHistory);
        } catch (geminiErr) {
            // Contextual heuristic knowledge engine fallback
            clientResp = clientProcessChat(text, currentArticles);
        }

        const el = document.getElementById(typingId);
        if (el) el.remove();

        appendChatMessage("bot", clientResp.reply);
        chatHistory.push({ sender: "bot", text: clientResp.reply });

        if (clientResp.suggested_questions && clientResp.suggested_questions.length > 0) {
            const chipsContainer = document.getElementById("chat-quick-chips");
            chipsContainer.innerHTML = clientResp.suggested_questions.map(q => `
                <button class="chip-btn" data-query="${escapeHTML(q)}">${escapeHTML(q)}</button>
            `).join("");
        }
    }
}

const DEFAULT_GEMINI_KEY = "";
const GEMINI_MODELS = ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-flash-latest"];

function getEffectiveGeminiKey() {
    const customKey = (localStorage.getItem("finnews_gemini_key") || "").trim();
    return customKey || DEFAULT_GEMINI_KEY;
}

window.togglePasswordVisibility = function(inputId, btn) {
    const el = document.getElementById(inputId);
    if (!el) return;
    if (el.type === "password") {
        el.type = "text";
        if (btn) btn.innerText = "🔒";
    } else {
        el.type = "password";
        if (btn) btn.innerText = "👁️";
    }
};

async function verifyGeminiKey(key) {
    if (!key || !key.trim()) return { success: false, error: "No API key provided." };
    const cleanKey = key.trim();
    for (const model of GEMINI_MODELS) {
        try {
            const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${encodeURIComponent(cleanKey)}`;
            const resp = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    contents: [{ parts: [{ text: "Hello" }] }],
                    generationConfig: { maxOutputTokens: 5 }
                })
            });
            if (resp.status === 200) {
                return { success: true, model: model };
            }
            if (resp.status === 400) {
                const data = await resp.json().catch(() => ({}));
                const msg = data.error?.message || "";
                if (msg.toLowerCase().includes("key not valid") || msg.toLowerCase().includes("api_key_invalid")) {
                    return { success: false, error: "Google rejected this key: API key not valid or unauthorized." };
                }
            }
        } catch (e) {
            // continue checking candidate models
        }
    }
    return { success: false, error: "Key could not connect to Google Generative AI models." };
}

async function callGeminiDirectly(userText, history = []) {
    const keysToTry = [];
    const customKey = (localStorage.getItem("finnews_gemini_key") || "").trim();
    if (customKey) keysToTry.push(customKey);
    if (!keysToTry.includes(DEFAULT_GEMINI_KEY)) keysToTry.push(DEFAULT_GEMINI_KEY);

    const preferredModel = localStorage.getItem("finnews_gemini_model") || "gemini-flash-lite-latest";
    const modelsToTry = [preferredModel, ...GEMINI_MODELS.filter(m => m !== preferredModel)];

    const historyText = history.slice(-4).map(m => `${m.sender.toUpperCase()}: ${m.text}`).join("\n");
    const langInstruction = currentLanguage === "Hindi" 
        ? "IMPORTANT: The user has selected Hindi. Respond in fluent, natural, grammatically correct Hindi (हिन्दी). Provide all bullet points, explanations, and follow-up questions in Hindi."
        : (currentLanguage === "Marathi"
            ? "IMPORTANT: The user has selected Marathi. Respond in fluent, natural, grammatically correct Marathi (मराठी). Provide all bullet points, explanations, and follow-up questions in Marathi."
            : (currentLanguage !== "English" ? `Respond in fluent ${currentLanguage}.` : ""));

    const prompt = `You are FinBot, the friendly world-class personal financial assistant embedded inside FinNews AI.
Answer the user's question clearly, accurately, and in plain language with bullet points and bold highlights.
${langInstruction}
Explain all financial jargon simply.
At the end, provide 3 short suggested follow-up questions formatted as:
FOLLOW_UPS:
- Question 1
- Question 2
- Question 3

CONVERSATION HISTORY:
${historyText}

USER QUESTION:
${userText}`;

    for (const key of keysToTry) {
        for (const model of modelsToTry) {
            const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${encodeURIComponent(key)}`;
            try {
                const resp = await fetch(url, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        contents: [{ parts: [{ text: prompt }] }],
                        generationConfig: { temperature: 0.3 }
                    })
                });
                if (resp.ok) {
                    localStorage.setItem("finnews_gemini_model", model);
                    const data = await resp.json();
                    const fullText = data.candidates?.[0]?.content?.parts?.[0]?.text || "";
                    let reply = fullText;
                    let followUps = [];
                    if (fullText.includes("FOLLOW_UPS:")) {
                        const parts = fullText.split("FOLLOW_UPS:");
                        reply = parts[0].trim();
                        followUps = parts[1].split("\n").map(l => l.replace(/^[-*•\s]+/, "").trim()).filter(Boolean).slice(0, 3);
                    }
                    return { reply, suggested_questions: followUps };
                }
            } catch (e) {
                continue;
            }
        }
    }
    throw new Error("All Gemini models failed. Using offline fallback.");
}

function appendChatMessage(sender, text) {
    const container = document.getElementById("chat-messages");
    const msgDiv = document.createElement("div");
    msgDiv.className = `chat-msg ${sender}-msg`;

    let formatted = escapeHTML(text)
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/\n\n/g, "<br/><br/>")
        .replace(/\n/g, "<br/>");

    msgDiv.innerHTML = `<div class="msg-bubble">${formatted}</div>`;
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

/* ================= NEWS & CONTROLS ================= */
function setupEventListeners() {
    document.getElementById("btn-fetch-simplify").addEventListener("click", async () => {
        const btn = document.getElementById("btn-fetch-simplify");
        const originalText = btn.innerHTML;
        btn.innerHTML = `<span class="spinner"></span> Fetching & Simplifying...`;
        btn.disabled = true;

        await loadNews();

        document.getElementById("news-section").scrollIntoView({ behavior: "smooth" });
        showToast("Fetched & simplified the latest financial updates!");
        
        btn.innerHTML = originalText;
        btn.disabled = false;
    });

    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            const cat = btn.dataset.category;
            if (cat === "custom") {
                document.getElementById("custom-section").classList.add("visible");
                document.getElementById("news-grid").style.display = "none";
            } else {
                document.getElementById("custom-section").classList.remove("visible");
                document.getElementById("news-grid").style.display = "grid";
                currentCategory = cat;
                loadNews();
            }
        });
    });

    // Search controls
    let debounceTimer;
    const searchInput = document.getElementById("search-input");
    const clearSearchBtn = document.getElementById("btn-clear-search");
    const searchGoBtn = document.getElementById("btn-search-go");
    const clearBannerBtn = document.getElementById("btn-clear-search-banner");

    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const val = searchInput.value.trim();
            if (clearSearchBtn) clearSearchBtn.style.display = val ? "block" : "none";
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                executeSearch(val);
            }, 400);
        });

        searchInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                clearTimeout(debounceTimer);
                executeSearch(searchInput.value.trim());
            }
        });
    }

    if (searchGoBtn) {
        searchGoBtn.addEventListener("click", () => {
            clearTimeout(debounceTimer);
            executeSearch(searchInput ? searchInput.value.trim() : "");
        });
    }

    const clearSearchAction = () => {
        if (searchInput) searchInput.value = "";
        executeSearch("");
        showToast("Search cleared. Displaying all news.");
    };

    if (clearSearchBtn) clearSearchBtn.addEventListener("click", clearSearchAction);
    if (clearBannerBtn) clearBannerBtn.addEventListener("click", clearSearchAction);

    // Trending Search Chips click
    const chipsBar = document.getElementById("search-chips-bar");
    if (chipsBar) {
        chipsBar.addEventListener("click", (e) => {
            const chip = e.target.closest(".search-chip");
            if (chip) {
                const q = chip.dataset.query;
                executeSearch(q);
            }
        });
    }

    const langSelect = document.getElementById("lang-select");
    langSelect.addEventListener("change", async (e) => {
        currentLanguage = e.target.value;
        localStorage.setItem("finnews_lang", currentLanguage);
        updateUILanguage(currentLanguage);
        showToast(`🌐 Loading news in ${currentLanguage}...`);
        await loadNews(searchInput ? searchInput.value.trim() : "");
        showToast(`✅ Updated news feed to ${currentLanguage}!`);
    });

    const btnSettings = document.getElementById("btn-settings");
    if (btnSettings) btnSettings.addEventListener("click", openSettingsModal);
    const closeSettings = document.getElementById("close-settings-modal");
    if (closeSettings) closeSettings.addEventListener("click", closeSettingsModal);
    const saveSettingsBtn = document.getElementById("btn-save-settings");
    if (saveSettingsBtn) saveSettingsBtn.addEventListener("click", saveSettings);
    const clearSettingsBtn = document.getElementById("btn-clear-settings");
    if (clearSettingsBtn) clearSettingsBtn.addEventListener("click", clearSettings);

    document.getElementById("btn-glossary").addEventListener("click", openGlossaryModal);
    document.getElementById("close-glossary-modal").addEventListener("click", closeGlossaryModal);
    document.getElementById("glossary-search").addEventListener("input", filterGlossary);

    // Mascot Card Click Listener ("AI Simplifies for Everyone" interactive tab)
    const mascotCard = document.getElementById("mascot-ai-card");
    if (mascotCard) {
        mascotCard.addEventListener("click", () => {
            const newsSection = document.getElementById("news-section");
            if (newsSection) {
                newsSection.scrollIntoView({ behavior: "smooth" });
            }

            // Programmatically switch all cards to AI Simplified Summaries
            const simplifiedBtns = document.querySelectorAll('.view-tab-btn[data-target^="simplified-"]');
            simplifiedBtns.forEach(btn => btn.click());

            // Add visual highlight pulse to simplified summary cards
            const summaryCards = document.querySelectorAll(".simplified-text, .insight-block");
            summaryCards.forEach(el => {
                el.classList.remove("highlight-pulse");
                void el.offsetWidth;
                el.classList.add("highlight-pulse");
                setTimeout(() => el.classList.remove("highlight-pulse"), 2500);
            });

            // Mascot scale feedback
            mascotCard.style.transform = "scale(0.96)";
            setTimeout(() => mascotCard.style.transform = "", 220);

            showToast("✨ FinNews AI Simplifier Activated: All financial reports translated into everyday knowledge!");
        });
    }

    // Hero Feature Badges (Operational on click)
    const pillLatest = document.getElementById("pill-latest-news");
    if (pillLatest) {
        pillLatest.addEventListener("click", async () => {
            currentCategory = "all";
            document.querySelectorAll(".tab-btn").forEach(b => {
                b.classList.toggle("active", b.dataset.category === "all");
            });
            const searchInput = document.getElementById("search-input");
            if (searchInput) searchInput.value = "";
            document.getElementById("custom-section").classList.remove("visible");
            document.getElementById("news-grid").style.display = "grid";

            showToast("⚡ Fetching fresh real-time financial updates...");
            await loadNews();
            document.getElementById("news-section").scrollIntoView({ behavior: "smooth" });
            showToast("✅ Real-time news feed refreshed!");
        });
    }

    const pillAi = document.getElementById("pill-ai-summaries");
    if (pillAi) {
        pillAi.addEventListener("click", () => {
            document.getElementById("news-section").scrollIntoView({ behavior: "smooth" });
            
            // Programmatically switch all cards to AI Simplified Summaries
            const simplifiedBtns = document.querySelectorAll('.view-tab-btn[data-target^="simplified-"]');
            simplifiedBtns.forEach(btn => btn.click());

            // Add visual highlight pulse to simplified summary cards
            const summaryCards = document.querySelectorAll(".simplified-text, .insight-block");
            summaryCards.forEach(el => {
                el.classList.remove("highlight-pulse");
                void el.offsetWidth;
                el.classList.add("highlight-pulse");
                setTimeout(() => el.classList.remove("highlight-pulse"), 2500);
            });

            showToast("✨ Switched all articles to AI Simplified Summaries!");
        });
    }

    const pillDecisions = document.getElementById("pill-better-decisions");
    if (pillDecisions) {
        pillDecisions.addEventListener("click", () => {
            // Scroll to market overview bar & highlight it
            const marketBar = document.getElementById("market-bar");
            if (marketBar) {
                marketBar.scrollIntoView({ behavior: "smooth", block: "center" });
                marketBar.classList.remove("highlight-pulse");
                void marketBar.offsetWidth;
                marketBar.classList.add("highlight-pulse");
                setTimeout(() => marketBar.classList.remove("highlight-pulse"), 2500);
            }

            // Open FinBot chatbot with Decision-Oriented Prompts
            const chatWindow = document.getElementById("chatbot-window");
            if (chatWindow) {
                chatWindow.classList.add("open");
                const chatInput = document.getElementById("chat-input");
                if (chatInput) chatInput.focus();
                
                const chipsContainer = document.getElementById("chat-quick-chips");
                if (chipsContainer) {
                    chipsContainer.innerHTML = [
                        "How should I position my portfolio today?",
                        "What are the top market risks right now?",
                        "How does current inflation affect my savings?",
                        "Which sectors look most resilient?"
                    ].map(q => `<button class="chip-btn" data-query="${escapeHTML(q)}">${escapeHTML(q)}</button>`).join("");
                }

                appendChatMessage("bot", "💡 **Smart Decision Guide**: I've loaded quick market decision prompts below. Feel free to ask how today's news affects your investments, portfolio diversification, or risk management!");
            }

            showToast("📊 Market Decision Guide & FinBot Assistant opened!");
        });
    }
}

/* ================= NEWS SEARCH CONTROLLER ================= */
async function executeSearch(query) {
    const searchInput = document.getElementById("search-input");
    const clearBtn = document.getElementById("btn-clear-search");
    const banner = document.getElementById("search-results-banner");
    const bannerQuery = document.getElementById("search-query-display");
    const bannerCount = document.getElementById("search-count-display");

    const cleanQ = (query !== undefined ? query : (searchInput ? searchInput.value : "")).trim();
    if (searchInput && query !== undefined) {
        searchInput.value = cleanQ;
    }
    if (clearBtn) {
        clearBtn.style.display = cleanQ ? "block" : "none";
    }

    // Reset category to "all" when searching
    currentCategory = "all";
    document.querySelectorAll(".tab-btn").forEach(b => {
        b.classList.toggle("active", b.dataset.category === "all");
    });
    const customSection = document.getElementById("custom-section");
    if (customSection) customSection.classList.remove("visible");
    const newsGrid = document.getElementById("news-grid");
    if (newsGrid) newsGrid.style.display = "grid";

    // Highlight matching chip if present
    document.querySelectorAll(".search-chip").forEach(chip => {
        chip.classList.toggle("active", chip.dataset.query.toLowerCase() === cleanQ.toLowerCase());
    });

    if (cleanQ) {
        if (banner) {
            banner.style.display = "flex";
            if (bannerQuery) bannerQuery.innerText = `"${cleanQ}"`;
            if (bannerCount) bannerCount.innerText = "Searching...";
        }
        showToast(`🔍 Searching live financial news for "${cleanQ}"...`);
    } else {
        if (banner) {
            banner.style.display = "none";
        }
    }

    await loadNews(cleanQ);

    if (cleanQ && bannerCount) {
        bannerCount.innerText = currentArticles ? currentArticles.length : 0;
    }

    const newsSection = document.getElementById("news-section");
    if (newsSection && cleanQ) {
        newsSection.scrollIntoView({ behavior: "smooth" });
    }
}

async function loadNews(query = "") {
    const grid = document.getElementById("news-grid");
    grid.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 40px;">
            <div class="spinner" style="margin: 0 auto 12px; border-top-color: var(--primary);"></div>
            <p style="color: var(--text-muted); font-weight: 600;">Retrieving latest market news (${escapeHTML(currentLanguage)})...</p>
        </div>
    `;

    try {
        let url = `/api/news?category=${encodeURIComponent(currentCategory)}&lang=${encodeURIComponent(currentLanguage)}`;
        if (query) {
            url += `&q=${encodeURIComponent(query)}`;
        }

        const res = await fetch(url);
        const ct = res.headers.get("content-type") || "";
        if (!res.ok || !ct.includes("application/json")) {
            throw new Error("API returned non-JSON, activating high-fidelity client fallback");
        }
        const data = await res.json();
        currentArticles = data.articles || [];

        renderMarketOverview(data.overview);
        renderNewsGrid(currentArticles);
    } catch (err) {
        // Instant Fallback to rich curated news engine
        const fallback = getClientFallbackNews(currentCategory, query, currentLanguage);
        currentArticles = fallback.articles || [];
        renderMarketOverview(fallback.overview);
        renderNewsGrid(currentArticles);
    }
}

function renderMarketOverview(overview) {
    if (!overview) return;
    
    document.getElementById("stat-total").innerText = overview.total_articles;
    document.getElementById("stat-bullish").innerText = overview.bullish_count;
    document.getElementById("stat-bearish").innerText = overview.bearish_count;
    
    const moodElem = document.getElementById("market-mood-label");
    let moodText = overview.market_mood || "Neutral";
    if (currentLanguage === "Hindi") {
        if (overview.market_sentiment_score >= 55) moodText = "तेजी / आशावादी (Bullish)";
        else if (overview.market_sentiment_score <= 45) moodText = "मंदी / सतर्क (Bearish)";
        else moodText = "संतुलित / तटस्थ (Neutral)";
    } else if (currentLanguage === "Marathi") {
        if (overview.market_sentiment_score >= 55) moodText = "तेजी / आशादायी (Bullish)";
        else if (overview.market_sentiment_score <= 45) moodText = "मंदी / सावध (Bearish)";
        else moodText = "संतुलित (Neutral)";
    }
    moodElem.innerText = moodText;
    
    const scoreElem = document.getElementById("market-score");
    scoreElem.innerText = `${overview.market_sentiment_score}/100`;

    moodElem.className = "mood-badge";
    if (overview.market_sentiment_score >= 55) {
        moodElem.classList.add("sentiment-bullish");
    } else if (overview.market_sentiment_score <= 45) {
        moodElem.classList.add("sentiment-bearish");
    } else {
        moodElem.classList.add("sentiment-neutral");
    }
}

function renderNewsGrid(articles) {
    const grid = document.getElementById("news-grid");
    if (!articles || articles.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px;">
                <p style="font-size: 1.2rem; font-weight: 700; margin-bottom: 8px;">No matching financial articles found</p>
                <p style="color: var(--text-muted);">Try a different search term or select another category tab above.</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = articles.map((art, index) => renderNewsCard(art, index)).join("");
    attachCardEvents();
}

function renderNewsCard(art, index) {
    const isBookmarked = savedBookmarks.includes(art.id);
    const sentimentClass = `sentiment-${art.sentiment}`;
    const sentimentIcon = art.sentiment === "bullish" ? "▲ BULLISH" : (art.sentiment === "bearish" ? "▼ BEARISH" : "◼ NEUTRAL");
    const cfg = LANG_CONFIG[currentLanguage] || LANG_CONFIG["English"];

    const jargonHTML = (art.jargon_terms || []).map(j => `
        <span class="jargon-chip" data-term="${escapeHTML(j.term)}" data-def="${escapeHTML(j.definition)}" title="${escapeHTML(j.definition)}">
            💡 ${escapeHTML(j.term)}
        </span>
    `).join("");

    const takeawaysHTML = (art.key_takeaways || []).map(t => `
        <li>${escapeHTML(t)}</li>
    `).join("");

    const savedPercent = Math.max(50, Math.round(((art.reading_time_original_mins - (art.reading_time_simplified_mins || 1)) / art.reading_time_original_mins) * 100));
    const imageUrl = art.url_to_image || "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&auto=format&fit=crop&q=60";

    return `
        <div class="card article-card" data-id="${art.id}">
            <div class="card-thumb-wrap btn-open-detail" data-id="${art.id}">
                <img class="card-thumb" src="${imageUrl}" alt="${escapeHTML(art.title)}" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&auto=format&fit=crop&q=60'" />
            </div>

            <div class="card-header">
                <div class="source-meta">
                    <span class="source-badge">${escapeHTML(art.source)}</span>
                    <span>${escapeHTML(art.published_at)}</span>
                </div>
                <span class="sentiment-tag ${sentimentClass}">
                    ${sentimentIcon}
                </span>
            </div>

            <h3 class="card-title btn-open-detail" data-id="${art.id}" style="cursor: pointer;" title="Click to open detail view">
                ${escapeHTML(art.title)}
            </h3>

            <div class="time-savings-banner">
                <span>⏱️ Read in <strong>${art.reading_time_simplified_mins || 1} min</strong> (vs ${art.reading_time_original_mins} min)</span>
                <span>⚡ Saved ${savedPercent}% reading time</span>
            </div>

            <div class="view-tabs">
                <button class="view-tab-btn active" data-target="simplified-${art.id}">${cfg.simplifiedView}</button>
                <button class="view-tab-btn" data-target="original-${art.id}">${cfg.originalNews}</button>
            </div>

            <div class="card-body">
                <!-- Simplified View -->
                <div class="view-content active" id="simplified-${art.id}">
                    <div class="simplified-text">
                        ${escapeHTML(art.simplified_summary || art.description || "Generating summary...")}
                    </div>

                    <div class="insights-accordion">
                        <div class="insight-pill-box">
                            <strong>${cfg.whatHappened}</strong>
                            <p>${escapeHTML(art.what_happened || art.description || "Core event breakdown.")}</p>
                        </div>
                        <div class="insight-pill-box">
                            <strong>${cfg.whyItMatters}</strong>
                            <p>${escapeHTML(art.why_it_matters || "Impact on borrowing, interest, or employment.")}</p>
                        </div>
                        <div class="insight-pill-box">
                            <strong>${cfg.marketImpact}</strong>
                            <p>${escapeHTML(art.market_impact || "Market index and asset movement.")}</p>
                        </div>
                    </div>

                    ${takeawaysHTML ? `
                        <div style="font-weight: 700; font-size: 0.8rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px;">
                            ${cfg.keyTakeaways}
                        </div>
                        <ul class="takeaways-list">
                            ${takeawaysHTML}
                        </ul>
                    ` : ""}

                    ${jargonHTML ? `
                        <div class="jargon-section">
                            <div class="jargon-title">${cfg.jargonHeader}</div>
                            <div class="jargon-cloud">
                                ${jargonHTML}
                            </div>
                        </div>
                    ` : ""}
                </div>

                <!-- Original View -->
                <div class="view-content" id="original-${art.id}">
                    <p style="font-size: 0.9rem; line-height: 1.6; color: var(--text-muted); margin-bottom: 14px;">
                        ${escapeHTML(art.content || art.description || art.title)}
                    </p>
                    ${art.url ? `
                        <a href="${art.url}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-sm" style="width: 100%; text-align: center;">
                            🔗 Open Original Article on ${escapeHTML(art.source)} ↗
                        </a>
                    ` : ""}
                </div>
            </div>

            <div class="card-footer">
                <button class="btn btn-outline btn-sm btn-open-detail" data-id="${art.id}">
                    ${cfg.readBreakdown}
                </button>
                <div class="footer-actions">
                    <button class="btn-icon btn-speak" data-id="${art.id}" title="Listen to Summary">
                        🔊
                    </button>
                    <button class="btn-icon btn-copy" data-id="${art.id}" title="Copy Summary">
                        📋
                    </button>
                    <button class="btn-icon btn-bookmark ${isBookmarked ? 'active' : ''}" data-id="${art.id}" title="Bookmark Article">
                        ${isBookmarked ? '★' : '☆'}
                    </button>
                    ${art.url ? `
                        <a href="${art.url}" target="_blank" rel="noopener noreferrer" class="btn-icon" title="Open original publication">
                            ↗
                        </a>
                    ` : ""}
                </div>
            </div>
        </div>
    `;
}

function attachCardEvents() {
    // Open detail modal on click
    document.querySelectorAll(".btn-open-detail").forEach(el => {
        el.addEventListener("click", () => {
            const artId = el.dataset.id;
            const art = currentArticles.find(a => a.id === artId);
            if (art) {
                openArticleModal(art);
            }
        });
    });

    document.querySelectorAll(".view-tab-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const card = btn.closest(".article-card");
            const targetId = btn.dataset.target;
            
            card.querySelectorAll(".view-tab-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            card.querySelectorAll(".view-content").forEach(c => c.classList.remove("active"));
            const targetElem = document.getElementById(targetId);
            if (targetElem) targetElem.classList.add("active");
        });
    });

    // Card speech audio
    document.querySelectorAll(".btn-speak").forEach(btn => {
        btn.addEventListener("click", () => {
            const artId = btn.dataset.id;
            const art = currentArticles.find(a => a.id === artId);
            if (!art) return;
            playArticleAudio(art, btn);
        });
    });

    document.querySelectorAll(".btn-copy").forEach(btn => {
        btn.addEventListener("click", () => {
            const artId = btn.dataset.id;
            const art = currentArticles.find(a => a.id === artId);
            if (!art) return;

            const text = `📰 ${art.title}\n\n✨ Simplified Summary:\n${art.simplified_summary}\n\n📌 What Happened:\n${art.what_happened}\n\n💡 Why It Matters:\n${art.why_it_matters}\n\n📊 Market Impact:\n${art.market_impact}`;
            navigator.clipboard.writeText(text);
            showToast("Summary copied to clipboard!");
        });
    });

    document.querySelectorAll(".btn-bookmark").forEach(btn => {
        btn.addEventListener("click", () => {
            const artId = btn.dataset.id;
            const idx = savedBookmarks.indexOf(artId);
            if (idx > -1) {
                savedBookmarks.splice(idx, 1);
                btn.classList.remove("active");
                btn.innerHTML = "☆";
                showToast("Removed from bookmarks.");
            } else {
                savedBookmarks.push(artId);
                btn.classList.add("active");
                btn.innerHTML = "★";
                showToast("Saved to bookmarks!");
            }
            localStorage.setItem("finnews_bookmarks", JSON.stringify(savedBookmarks));
        });
    });
}

/* ================= CUSTOM ARTICLE SIMPLIFIER ================= */
async function handleCustomSimplify() {
    const text = document.getElementById("custom-text-input").value.trim();
    if (!text || text.length < 20) {
        showToast("Please enter at least 20 characters of financial text.");
        return;
    }

    const btn = document.getElementById("btn-simplify-custom");
    const origText = btn.innerHTML;
    btn.innerHTML = `<span class="spinner"></span> Analyzing with AI...`;
    btn.disabled = true;

    try {
        const res = await fetch("/api/simplify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text: text,
                language: currentLanguage,
                complexity_target: "simple"
            })
        });

        const data = await res.json();
        renderCustomResult(data);
        showToast(`Article simplified successfully in ${currentLanguage}!`);
    } catch (err) {
        showToast("Error simplifying article. Please try again.");
    } finally {
        btn.innerHTML = origText;
        btn.disabled = false;
    }
}

function renderCustomResult(data) {
    const resDiv = document.getElementById("custom-result");
    resDiv.style.display = "block";

    const jargonList = (data.jargon_terms || []).map(j => `
        <span class="jargon-chip" title="${escapeHTML(j.definition)}">💡 ${escapeHTML(j.term)}</span>
    `).join("");

    const takeaways = (data.key_takeaways || []).map(t => `
        <li>${escapeHTML(t)}</li>
    `).join("");

    resDiv.innerHTML = `
        <div class="card" style="border-top: 4px solid var(--primary); padding: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <span class="badge-pill" style="color: var(--primary);">⚡ ${escapeHTML(data.engine_used || "FinNews AI Engine")}</span>
                <span class="sentiment-tag sentiment-${data.sentiment}">
                    ${data.sentiment === "bullish" ? "▲ Bullish" : (data.sentiment === "bearish" ? "▼ Bearish" : "◼ Neutral")}
                </span>
            </div>

            <h3 style="font-size: 1.3rem; font-weight: 800; margin-bottom: 12px;">${escapeHTML(data.title)}</h3>

            <div class="time-savings-banner" style="margin-bottom: 16px;">
                <span>⏱️ Read in <strong>${data.reading_time_simplified_mins} min</strong> (vs ${data.reading_time_original_mins} min)</span>
                <span>⚡ Saved ${data.reading_time_saved_percent}% reading time</span>
            </div>

            <div class="simplified-text" style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 18px;">
                ${escapeHTML(data.simplified_summary)}
            </div>

            <div class="insights-accordion" style="margin-bottom: 18px;">
                <div class="insight-pill-box">
                    <strong>📌 What Happened:</strong>
                    <p>${escapeHTML(data.what_happened)}</p>
                </div>
                <div class="insight-pill-box">
                    <strong>💡 Why It Matters to You:</strong>
                    <p>${escapeHTML(data.why_it_matters)}</p>
                </div>
                <div class="insight-pill-box">
                    <strong>📊 Market Impact:</strong>
                    <p>${escapeHTML(data.market_impact)}</p>
                </div>
            </div>

            ${takeaways ? `
                <div style="font-weight: 700; font-size: 0.85rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px;">
                    Key Takeaways:
                </div>
                <ul class="takeaways-list" style="margin-bottom: 18px;">
                    ${takeaways}
                </ul>
            ` : ""}

            ${jargonList ? `
                <div class="jargon-section">
                    <div class="jargon-title">💡 Jargon Explained:</div>
                    <div class="jargon-cloud">${jargonList}</div>
                </div>
            ` : ""}

            <div style="margin-top: 18px; display: flex; gap: 10px;">
                <button class="btn btn-outline btn-sm" id="btn-speak-custom">🔊 Listen to Summary</button>
                <button class="btn btn-outline btn-sm" id="btn-copy-custom">📋 Copy Summary</button>
            </div>
        </div>
    `;

    document.getElementById("btn-speak-custom").addEventListener("click", () => {
        playArticleAudio(data, document.getElementById("btn-speak-custom"));
    });

    document.getElementById("btn-copy-custom").addEventListener("click", () => {
        const text = `📰 ${data.title}\n\n✨ Summary:\n${data.simplified_summary}\n\n📌 What Happened:\n${data.what_happened}\n\n💡 Why It Matters:\n${data.why_it_matters}`;
        navigator.clipboard.writeText(text);
        showToast("Summary copied to clipboard!");
    });
}

/* ================= GLOSSARY MODAL ================= */
async function loadGlossary() {
    try {
        const res = await fetch("/api/glossary");
        const ct = res.headers.get("content-type") || "";
        if (res.ok && ct.includes("application/json")) {
            glossaryData = await res.json();
            return;
        }
    } catch (e) {}
    glossaryData = CLIENT_FALLBACK_GLOSSARY;
}

function openGlossaryModal() {
    const modal = document.getElementById("glossary-modal");
    renderGlossaryList(glossaryData);
    modal.classList.add("active");
}

function closeGlossaryModal() {
    document.getElementById("glossary-modal").classList.remove("active");
}

function filterGlossary(e) {
    const query = e.target.value.toLowerCase().trim();
    const filtered = glossaryData.filter(g => 
        g.term.toLowerCase().includes(query) || 
        g.definition.toLowerCase().includes(query)
    );
    renderGlossaryList(filtered);
}

function renderGlossaryList(terms) {
    const container = document.getElementById("glossary-list");
    if (!terms || terms.length === 0) {
        container.innerHTML = `<p style="color: var(--text-muted); text-align: center; padding: 20px;">No financial terms found.</p>`;
        return;
    }

    container.innerHTML = terms.map(t => `
        <div style="border-bottom: 1px solid var(--border); padding: 12px 0;">
            <div style="font-weight: 700; color: var(--primary); font-size: 1rem; margin-bottom: 4px;">
                📖 ${escapeHTML(t.term)}
            </div>
            <div style="font-size: 0.9rem; color: #334155; line-height: 1.5;">
                ${escapeHTML(t.definition)}
            </div>
        </div>
    `).join("");
}

/* ================= SETTINGS MODAL & CREDENTIALS MANAGEMENT ================= */
async function checkSettingsStatus() {
    const userGeminiKey = (localStorage.getItem("finnews_gemini_key") || "").trim();
    const userNewsKey = (localStorage.getItem("finnews_news_key") || "").trim();
    const userOpenaiKey = (localStorage.getItem("finnews_openai_key") || "").trim();
    const verifiedModel = localStorage.getItem("finnews_gemini_model") || "gemini-3.6-flash";

    let hasGemini = Boolean(userGeminiKey) || Boolean(DEFAULT_GEMINI_KEY);
    let hasNews = Boolean(userNewsKey);
    let hasOpenai = Boolean(userOpenaiKey);

    try {
        const res = await fetch("/api/settings");
        const ct = res.headers.get("content-type") || "";
        if (res.ok && ct.includes("application/json")) {
            const data = await res.json();
            if (data.has_gemini_api) hasGemini = true;
            if (data.has_news_api) hasNews = true;
            if (data.has_openai_api) hasOpenai = true;
        }
    } catch (e) {
        // Firebase static hosting or offline
    }

    const pills = [
        document.getElementById("api-status-pill"),
        document.getElementById("api-status-badge")
    ].filter(Boolean);

    pills.forEach(pill => {
        if (hasGemini) {
            const modelLabel = userGeminiKey ? `Gemini Active (${verifiedModel})` : `Gemini AI Connected`;
            pill.innerHTML = `<span class="dot dot-green"></span> ${modelLabel}`;
            pill.style.color = "var(--bullish)";
        } else if (hasNews || hasOpenai) {
            pill.innerHTML = `<span class="dot dot-green"></span> Live APIs Connected`;
            pill.style.color = "var(--bullish)";
        } else {
            pill.innerHTML = `<span class="dot dot-green"></span> Smart Offline AI`;
            pill.style.color = "var(--text-muted)";
        }
    });
}

async function openSettingsModal() {
    const modal = document.getElementById("settings-modal");
    if (!modal) return;

    const newsInput = document.getElementById("input-news-key") || document.getElementById("input-newsapi-key");
    const geminiInput = document.getElementById("input-gemini-key");
    const openaiInput = document.getElementById("input-openai-key");
    const statusMsg = document.getElementById("settings-status-msg");

    if (statusMsg) {
        statusMsg.style.display = "none";
        statusMsg.innerText = "";
    }

    // 1. Populate from localStorage
    const savedGemini = (localStorage.getItem("finnews_gemini_key") || "").trim();
    const savedNews = (localStorage.getItem("finnews_news_key") || "").trim();
    const savedOpenai = (localStorage.getItem("finnews_openai_key") || "").trim();

    if (geminiInput) {
        geminiInput.value = savedGemini;
        geminiInput.placeholder = savedGemini ? "••••••••••••••••••••••••" : "Enter Google Gemini API Key";
    }
    if (newsInput) {
        newsInput.value = savedNews;
        newsInput.placeholder = savedNews ? "••••••••••••••••••••••••" : "Enter NewsAPI Key (optional)";
    }
    if (openaiInput) {
        openaiInput.value = savedOpenai;
        openaiInput.placeholder = savedOpenai ? "••••••••••••••••••••••••" : "Enter OpenAI API Key (optional)";
    }

    // 2. Read backend masked values if available
    try {
        const res = await fetch("/api/settings");
        const ct = res.headers.get("content-type") || "";
        if (res.ok && ct.includes("application/json")) {
            const data = await res.json();
            if (geminiInput && !geminiInput.value && data.gemini_api_masked) {
                geminiInput.placeholder = data.gemini_api_masked;
            }
            if (newsInput && !newsInput.value && data.news_api_masked) {
                newsInput.placeholder = data.news_api_masked;
            }
            if (openaiInput && !openaiInput.value && data.openai_api_masked) {
                openaiInput.placeholder = data.openai_api_masked;
            }
        }
    } catch (e) {}

    modal.classList.add("active");
}

function closeSettingsModal() {
    const modal = document.getElementById("settings-modal");
    if (modal) modal.classList.remove("active");
}

function clearSettings() {
    localStorage.removeItem("finnews_gemini_key");
    localStorage.removeItem("finnews_gemini_model");
    localStorage.removeItem("finnews_news_key");
    localStorage.removeItem("finnews_openai_key");

    const newsInput = document.getElementById("input-news-key") || document.getElementById("input-newsapi-key");
    const geminiInput = document.getElementById("input-gemini-key");
    const openaiInput = document.getElementById("input-openai-key");
    const statusMsg = document.getElementById("settings-status-msg");

    if (newsInput) newsInput.value = "";
    if (geminiInput) geminiInput.value = "";
    if (openaiInput) openaiInput.value = "";

    // Sync clear to backend if reachable
    fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ news_api_key: "", gemini_api_key: "", openai_api_key: "" })
    }).catch(() => {});

    checkSettingsStatus();
    showToast("Credentials cleared. Default AI active.");
    if (statusMsg) {
        statusMsg.style.display = "block";
        statusMsg.style.color = "#64748b";
        statusMsg.innerText = "Cleared. Reverted to built-in FinNews AI engine.";
    }
}

async function saveSettings() {
    const newsInput = document.getElementById("input-news-key") || document.getElementById("input-newsapi-key");
    const geminiInput = document.getElementById("input-gemini-key");
    const openaiInput = document.getElementById("input-openai-key");
    const statusMsg = document.getElementById("settings-status-msg");
    const saveBtn = document.getElementById("btn-save-settings");

    const newsKey = newsInput ? newsInput.value.trim() : "";
    const geminiKey = geminiInput ? geminiInput.value.trim() : "";
    const openaiKey = openaiInput ? openaiInput.value.trim() : "";

    const origBtnText = saveBtn ? saveBtn.innerHTML : "Save Credentials";
    if (saveBtn) {
        saveBtn.innerHTML = `<span class="spinner"></span> Verifying & Saving...`;
        saveBtn.disabled = true;
    }

    try {
        let geminiModel = "gemini-3.6-flash";
        let geminiVerified = false;

        // 1. Verify and save Gemini key if provided
        if (geminiKey) {
            if (statusMsg) {
                statusMsg.style.display = "block";
                statusMsg.style.color = "var(--primary)";
                statusMsg.innerText = "⏳ Connecting and verifying Google Gemini API Key...";
            }

            const verification = await verifyGeminiKey(geminiKey);
            if (verification.success) {
                geminiVerified = true;
                geminiModel = verification.model;
                localStorage.setItem("finnews_gemini_key", geminiKey);
                localStorage.setItem("finnews_gemini_model", geminiModel);
            } else {
                // If the test could not verify, save key anyway and note the warning
                localStorage.setItem("finnews_gemini_key", geminiKey);
                if (statusMsg) {
                    statusMsg.style.display = "block";
                    statusMsg.style.color = "#d97706";
                    statusMsg.innerText = `⚠️ Notice: ${verification.error}. Key saved for runtime inference.`;
                }
            }
        } else if (geminiInput && geminiInput.value === "") {
            localStorage.removeItem("finnews_gemini_key");
            localStorage.removeItem("finnews_gemini_model");
        }

        // 2. Save NewsAPI & OpenAI Keys
        if (newsKey) {
            localStorage.setItem("finnews_news_key", newsKey);
        } else if (newsInput && newsInput.value === "") {
            localStorage.removeItem("finnews_news_key");
        }

        if (openaiKey) {
            localStorage.setItem("finnews_openai_key", openaiKey);
        } else if (openaiInput && openaiInput.value === "") {
            localStorage.removeItem("finnews_openai_key");
        }

        // 3. Sync to backend API if reachable
        try {
            await fetch("/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    news_api_key: newsKey || null,
                    gemini_api_key: geminiKey || null,
                    openai_api_key: openaiKey || null
                })
            });
        } catch (e) {
            // Handled gracefully on Firebase Hosting
        }

        // 4. Update UI Status and Toast
        checkSettingsStatus();
        const toastMsg = geminiVerified 
            ? `✅ Google Gemini Connected! (${geminiModel})` 
            : `✅ Credentials saved successfully!`;
        showToast(toastMsg);

        if (statusMsg) {
            statusMsg.style.display = "block";
            statusMsg.style.color = "#059669";
            statusMsg.innerText = toastMsg;
        }

        setTimeout(() => {
            closeSettingsModal();
            loadNews();
        }, 600);

    } catch (err) {
        console.error("Save settings error:", err);
        showToast("Error updating credentials: " + (err.message || ""));
        if (statusMsg) {
            statusMsg.style.display = "block";
            statusMsg.style.color = "#ef4444";
            statusMsg.innerText = "❌ Error: " + (err.message || "Failed to update settings");
        }
    } finally {
        if (saveBtn) {
            saveBtn.innerHTML = origBtnText;
            saveBtn.disabled = false;
        }
    }
}

/* ================= TOAST NOTIFICATIONS ================= */
function showToast(message) {
    let toast = document.getElementById("app-toast");
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "app-toast";
        toast.className = "toast";
        document.body.appendChild(toast);
    }

    toast.innerText = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3200);
}

function escapeHTML(str) {
    if (!str) return "";
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/* ================= STANDALONE & CDN CLIENT-SIDE FALLBACK ENGINE ================= */
const CLIENT_FALLBACK_ARTICLES = [
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
    "is_simplified": true,
    "simplified_summary": "The Federal Reserve hinted that interest rates will stay high because prices for everyday goods and services aren't falling as fast as hoped.",
    "what_happened": "The Federal Reserve warned that inflation is still higher than their 2% goal, so they may keep interest rates high or even raise them again.",
    "why_it_matters": "Higher interest rates make borrowing money more expensive for everyone \u2014 including car loans, credit cards, mortgages, and business expansion loans.",
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
    "is_simplified": true,
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
    "is_simplified": true,
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
    "is_simplified": true,
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
    "sentiment_score": 0.7,
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
    "is_simplified": true,
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
    "sentiment_score": 0.6,
    "reading_time_simplified_mins": 1
  }
];

const CLIENT_PRETRANSLATED_ARTICLES = {
  "Hindi": {
    "art-fed-rate-hike": {
      "title": "फ़ेडरल रिज़र्व ने महंगाई की चिंताओं के बीच ब्याज दरों में बढ़ोतरी का संकेत दिया",
      "simplified_summary": "फ़ेडरल रिज़र्व ने संकेत दिया है कि ब्याज दरें लंबे समय तक ऊंची रहेंगी क्योंकि दैनिक वस्तुओं और सेवाओं की कीमतें उम्मीद के मुताबिक तेजी से कम नहीं हो रही हैं।",
      "what_happened": "फ़ेडरल रिज़र्व ने चेतावनी दी कि मुद्रास्फीति अभी भी उनके 2% के लक्ष्य से अधिक है, इसलिए वे ब्याज दरों को ऊंचा रख सकते हैं या दोबारा बढ़ा भी सकते हैं।",
      "why_it_matters": "ऊंची ब्याज दरें आम जनता के लिए कर्ज लेना अधिक महंगा बना देती हैं — जिसमें कार लोन, क्रेडिट कार्ड, होम लोन और बिजनेस लोन शामिल हैं।",
      "market_impact": "ट्रेजरी बॉन्ड यील्ड में उछाल आया और शेयर बाजारों में गिरावट आई क्योंकि निवेशकों को समझ आया कि सस्ता कर्ज जल्द वापस नहीं आएगा।",
      "key_takeaways": [
        "ब्याज दरें लंबे समय तक ऊंची रहने की संभावना है।",
        "होम लोन और क्रेडिट कार्ड से कर्ज लेने की लागत अधिक बनी रहेगी।",
        "सरकारी बॉन्ड की पैदावार 14 आधार अंक (0.14%) बढ़ गई।"
      ]
    },
    "art-tech-rally": {
      "title": "मजबूत एआई कमाई और क्लाउड मार्जिन के दम पर टेक शेयरों में भारी उछाल",
      "simplified_summary": "प्रमुख एआई और कंप्यूटर चिप कंपनियों द्वारा भारी मुनाफे और बढ़ती मांग की घोषणा के बाद तकनीकी कंपनियों के शेयरों में जोरदार तेजी दर्ज की गई।",
      "what_happened": "प्रमुख टेक और चिप निर्माता कंपनियों ने वॉल स्ट्रीट के अनुमानों को पीछे छोड़ दिया और पूरे वर्ष के लिए कमाई के अनुमान बढ़ा दिए।",
      "why_it_matters": "कंपनियों का मजबूत मुनाफा दर्शाता है कि व्यवसाय नई तकनीक पर भारी निवेश कर रहे हैं, जिससे रोजगार बढ़ रहा है और निवेश पोर्टफोलियो को मजबूती मिल रही है।",
      "market_impact": "नैस्डैक इंडेक्स 2.4% उछला और निवेशकों के भरोसे ने पूरे शेयर बाजार में तेजी ला दी।",
      "key_takeaways": [
        "एआई इन्फ्रास्ट्रक्चर पर हो रहा खर्च वास्तविक कॉर्पोरेट राजस्व ला रहा है।",
        "टेक कंपनियों का ग्रॉस प्रॉफिट मार्जिन 72% तक पहुंच गया।",
        "प्रमुख विश्लेषकों ने कंपनियों के टार्गेट प्राइस में बढ़ोतरी की।"
      ]
    },
    "art-global-markets-geopolitical": {
      "title": "भू-राजनीतिक तनावों के बीच सुरक्षित संपत्तियों की ओर भागे निवेशक, तेल और सोने में तेजी",
      "simplified_summary": "अंतरराष्ट्रीय तनाव के कारण कच्चे तेल और सोने की कीमतों में उछाल आया, जबकि शेयर बाजारों में गिरावट आई क्योंकि निवेशक सुरक्षित संपत्तियों की तलाश कर रहे हैं।",
      "what_happened": "प्रमुख समुद्री व्यापार मार्गों में बाधाओं के कारण ईंधन महंगा होने और आपूर्ति में देरी का डर बढ़ा, जिससे शेयर बाजारों में बिकवाली देखने को मिली।",
      "why_it_matters": "कच्चे तेल की ऊंची कीमतों का मतलब है पेट्रोल-डीजल की महंगाई और दुकानों में मिलने वाली रोजमर्रा की जरूरी चीजों की कीमतों में बढ़ोतरी।",
      "market_impact": "कच्चा तेल लगभग 4% उछल गया, सोने में सुरक्षित निवेश के रूप में तेजी आई और वैश्विक शेयर सूचकांक लाल निशान में बंद हुए।",
      "key_takeaways": [
        "समुद्री व्यापार मार्गों की चिंताओं से कच्चा तेल 3.8% बढ़ गया।",
        "निवेशकों ने सोने जैसी सुरक्षित संपत्तियों में पैसा लगाया।",
        "शिपिंग लागत बढ़ने से महंगाई में कमी की रफ्तार धीमी हो सकती है।"
      ]
    },
    "art-crypto-etf-inflows": {
      "title": "बिटकॉइन ईटीएफ में संस्थागत निवेश एक हफ्ते में $1.5 बिलियन के मील के पत्थर पर पहुंचा",
      "simplified_summary": "इस हफ्ते बड़े वित्तीय संस्थानों और वेल्थ फंडों ने विनियमित बिटकॉइन ईटीएफ फंड में $1.5 बिलियन से अधिक का निवेश किया, जिससे मुख्यधारा का भरोसा बढ़ा है।",
      "what_happened": "स्पॉट बिटकॉइन ईटीएफ में पेंशन फंड और वेल्थ एडवाइजर्स की तरफ से $1.5 बिलियन का रिकॉर्ड संस्थागत निवेश देखा गया।",
      "why_it_matters": "विनियमित ईटीएफ आम निवेशकों के लिए अपने नियमित ब्रोकरेज खाते के माध्यम से क्रिप्टो में सुरक्षित और आसान निवेश का मार्ग खोलते हैं।",
      "market_impact": "लगातार संस्थागत खरीदारी से बिटकॉइन के अत्यधिक उतार-चढ़ाव में कमी आ रही है और बाजार का मूल्यांकन मजबूत हो रहा है।",
      "key_takeaways": [
        "सिर्फ एक हफ्ते में बिटकॉइन ईटीएफ में $1.5 बिलियन का निवेश आया।",
        "पारंपरिक वेल्थ एडवाइजर्स 1-3% पोर्टफोलियो आवंटन की सलाह दे रहे हैं।",
        "संस्थागत मांग क्रिप्टो बाजार के जोखिम को संतुलित करने में मदद कर रही है।"
      ]
    },
    "art-retail-banking-margins": {
      "title": "प्रमुख बैंकों ने पेश किए शानदार नतीजे, उपभोक्ता क्रेडिट और ब्याज मार्जिन में मजबूत सुधार",
      "simplified_summary": "देश के सबसे बड़े बैंकों ने शानदार तिमाही मुनाफा कमाया क्योंकि उपभोक्ता अपने कर्ज का समय पर भुगतान कर रहे हैं और बैंकों को ब्याज से बेहतर कमाई हो रही है।",
      "what_happened": "बड़े बैंकों ने कम डिफॉल्ट और मजबूत मुनाफे के साथ वॉल स्ट्रीट की उम्मीदों को मात दी।",
      "why_it_matters": "जब बैंक मजबूत होते हैं, तो इसका मतलब है कि आम उपभोक्ता अपनी ईएमआई समय पर चुका रहे हैं और होम लोन व व्यापारिक ऋण आसानी से उपलब्ध हैं।",
      "market_impact": "वित्तीय क्षेत्र के शेयरों में बढ़त दर्ज की गई, जिससे पूरी अर्थव्यवस्था में निवेशकों का भरोसा बढ़ा।",
      "key_takeaways": [
        "उपभोक्ता ऋण चूक दर ऐतिहासिक औसत से नीचे बनी हुई है।",
        "बैंक जमा और ऋण दरों के बीच के अंतर से मुनाफा कमा रहे हैं।",
        "मजबूत बैंकिंग क्षेत्र मंदी के खतरों के खिलाफ सुरक्षा कवच प्रदान करता है।"
      ]
    }
  },
  "Marathi": {
    "art-fed-rate-hike": {
      "title": "महागाईच्या चिंतेमुळे फेडरल रिझर्व्हने व्याजदर वाढीचे दिले संकेत",
      "simplified_summary": "फेडरल रिझर्व्हने सूचित केले आहे की व्याजदर दीर्घकाळ उच्च राहतील, कारण दैनंदिन वस्तू आणि सेवांचे भाव अपेक्षेप्रमाणे वेगाने कमी होत नाहीत.",
      "what_happened": "मध्यवर्ती बँकेने चेतावणी दिली की महागाई अजूनही त्यांच्या 2% लक्ष्यापेक्षा जास्त आहे आणि पुढील व्याजदर वाढ आवश्यक असू शकते.",
      "why_it_matters": "जास्त व्याजदरांमुळे गृहकर्ज, कार कर्ज, क्रेडिट कार्ड आणि व्यवसाय कर्जे सर्वसामान्यांसाठी अधिक महाग होतात.",
      "market_impact": "सरकारी रोख्यांचे उत्पन्न वाढले आणि स्वस्त कर्जाची शक्यता लांबल्याने शेअर बाजारात घसरण झाली.",
      "key_takeaways": [
        "व्याजदर दीर्घकाळ उच्च राहण्याची शक्यता आहे.",
        "गृहकर्ज आणि क्रेडिट कार्डचे हप्ते महागच राहतील.",
        "सरकारी ट्रेझरी रोख्यांचे उत्पन्न 14 बेसिस पॉईंट्सने वाढले."
      ]
    },
    "art-tech-rally": {
      "title": "मजबूत एआय नफा आणि क्लाउड मार्जिनमुळे टेक शेअर्समध्ये मोठी उसळी",
      "simplified_summary": "प्रमुख सेमीकंडक्टर आणि एआय कंपन्यांनी प्रचंड नफा आणि वाढत्या मागणीची घोषणा केल्याने टेक कंपन्यांच्या शेअर्समध्ये जोरदार तेजी पाहायला मिळाली.",
      "what_happened": "आघाडीच्या टेक कंपन्यांनी वॉल स्ट्रीटचे अंदाज मागे टाकत चालू वर्षासाठी कमाईचे अंदाज वाढवले आहेत.",
      "why_it_matters": "कंपन्यांचा दमदार नफा दर्शवतो की व्यवसाय नवीन तंत्रज्ञानावर मोठी गुंतवणूक करत आहेत, ज्यामुळे रोजगार निर्मिती आणि गुंतवणुकीला बळ मिळते.",
      "market_impact": "नॅस्डॅक निर्देशांक 2.4% ने वधारला आणि बाजारात सर्वत्र सकारात्मक वातावरण निर्माण झाले.",
      "key_takeaways": [
        "एआय पायाभूत सुविधांवरील खर्च प्रत्यक्षात महसूल मिळवून देत आहे.",
        "टेक क्षेत्राचे ग्रॉस प्रॉफिट मार्जिन 72% पर्यंत पोहोचले.",
        "प्रमुख विश्लेषकांनी कंपन्यांच्या टार्गेट प्राईसमध्ये वाढ केली."
      ]
    },
    "art-global-markets-geopolitical": {
      "title": "भू-राजकीय तणावामुळे सुरक्षित मालमत्तांकडे ओघ; सोने आणि कच्च्या तेलात तेजी",
      "simplified_summary": "आंतरराष्ट्रीय तणावामुळे कच्च्या तेलाचे आणि सोन्याचे भाव वाढले, तर गुंतवणूकदार सुरक्षित पर्यायांकडे वळल्याने शेअर बाजारात घसरण झाली.",
      "what_happened": "सागरी व्यापारी मार्गांमधील अडथळ्यांमुळे इंधन महाग होण्याचे आणि मालाचा तुटवडा निर्माण होण्याचे संकट ओढवले.",
      "why_it_matters": "कच्चे तेल महागल्यास पेट्रोल-डिझेलचे दर वाढतात आणि दैनंदिन गरजेच्या वस्तूंची महागाई वाढते.",
      "market_impact": "ब्रेंट क्रूड 3.8% ने वधारले, सुरक्षित गुंतवणुकीमुळे सोन्यात तेजी आली आणि जागतिक बाजार लाल निशाण्यावर बंद झाले.",
      "key_takeaways": [
        "सागरी वाहतूक धोक्यांमुळे कच्च्या तेलाचे दर 3.8% वाढले.",
        "गुंतवणूकदारांनी सोन्यासारख्या सुरक्षित पर्यायात भांडवल गुंतवले.",
        "वाहतूक खर्च वाढल्याने महागाई नियंत्रणात येण्यास विलंब होऊ शकतो."
      ]
    },
    "art-crypto-etf-inflows": {
      "title": "बिटकॉइन ईटीएफमध्ये संस्थात्मक गुंतवणूक आठवड्यात $1.5 अब्जच्या विक्रमी टप्प्यावर",
      "simplified_summary": "या आठवड्यात मोठ्या संस्थात्मक गुंतवणूकदारांनी आणि पेन्शन फंडांनी मान्यताप्राप्त बिटकॉइन ईटीएफमध्ये $1.5 अब्जहून अधिक गुंतवणूक केली.",
      "what_happened": "स्पॉट बिटकॉइन ईटीएफमध्ये पारंपारिक संपत्ती सल्लागार आणि संस्थांकडून विक्रमी गुंतवणूक झाली.",
      "why_it_matters": "मान्यताप्राप्त ईटीएफमुळे सामान्य गुंतवणूकदारांना त्यांच्या नेहमीच्या डीमॅट/ब्रोकरेज खात्यातून क्रिप्टोमध्ये सुरक्षित गुंतवणूक करणे सोपे झाले आहे.",
      "market_impact": "सातत्यपूर्ण खरेदीमुळे बिटकॉइनच्या चढ-उतारात स्थैर्य येत असून मूल्यांकनाला आधार मिळत आहे.",
      "key_takeaways": [
        "एका आठवड्यात $1.5 अब्जपेक्षा जास्त भांडवल बिटकॉइन ईटीएफमध्ये आले.",
        "पारंपारिक सल्लागार 1 ते 3% पोर्टफोलिओ वितरणाची शिफारस करत आहेत.",
        "संस्थात्मक मागणीमुळे क्रिप्टो बाजारातील जोखीम कमी होण्यास मदत होत आहे."
      ]
    },
    "art-retail-banking-margins": {
      "title": "प्रमुख बँकांचे शानदार निकाल; ग्राहक पतपुरवठा आणि व्याज मार्जिनमध्ये सुधारणा",
      "simplified_summary": "देशातील अग्रगण्य बँकांनी भरघोस नफा कमावला आहे, कारण ग्राहक कर्जाची वेळेवर परतफेड करत आहेत आणि बँकांना व्याजातून चांगला नफा मिळत आहे.",
      "what_happened": "बँकांनी कमी कर्ज बुडीत दर आणि वाढीव व्याज उत्पन्नासह विश्लेषकांच्या अपेक्षेपेक्षा सरस निकाल दिले.",
      "why_it_matters": "बँकांची उत्तम स्थिती हे दर्शवते की सामान्य नागरिकांची आर्थिक स्थिती स्थिर आहे आणि घर अथवा व्यवसायासाठी सहज कर्ज उपलब्ध आहे.",
      "market_impact": "बँक शेअर्समध्ये वाढ झाली असून यामुळे संपूर्ण अर्थव्यवस्थेवरील विश्वास अधिक दृढ झाला.",
      "key_takeaways": [
        "कर्ज थकबाकीचे प्रमाण ऐतिहासिक सरासरीपेक्षा कमी आहे.",
        "ठेवी आणि कर्ज वाटपातील व्याज फरकाचा बँकांना मोठा फायदा होत आहे.",
        "मजबूत बँकिंग क्षेत्र आर्थिक मंदीपासून संरक्षणाची ढाल ठरते."
      ]
    }
  },
  "Spanish": {
    "art-fed-rate-hike": {
      "title": "La Fed insinúa posibles subidas de tipos ante persistente inflación",
      "simplified_summary": "La Reserva Federal advirtió que las tasas de interés se mantendrán altas durante más tiempo porque la inflación no está bajando al ritmo esperado.",
      "what_happened": "El banco central advirtió que la inflación sigue por encima del objetivo del 2% y podría requerir tasas más elevadas.",
      "why_it_matters": "Tasas de interés más altas encarecen los préstamos para hipotecas, tarjetas de crédito y préstamos empresariales.",
      "market_impact": "Los rendimientos de bonos subieron y las bolsas cayeron ante la perspectiva de un crédito más caro.",
      "key_takeaways": [
        "Es probable que las tasas permanezcan altas por más tiempo.",
        "Los costos de hipotecas y créditos continuarán elevados.",
        "Los rendimientos de bonos del Tesoro aumentaron 14 puntos básicos."
      ]
    },
    "art-tech-rally": {
      "title": "Rally de acciones tecnológicas impulsado por ganancias en IA y márgenes en la nube",
      "simplified_summary": "Las acciones de tecnología subieron con fuerza tras reportes de beneficios récord de gigantes de semiconductores e inteligencia artificial.",
      "what_happened": "Las grandes empresas de tecnología superaron las expectativas de Wall Street y elevaron sus previsiones anuales.",
      "why_it_matters": "Los sólidos beneficios muestran que la inversión en tecnología impulsa el crecimiento económico y las carteras de retiro.",
      "market_impact": "El Nasdaq subió 2.4% e impulsó el optimismo en todos los índices bursátiles.",
      "key_takeaways": [
        "La inversión en IA se traduce en ingresos corporativos reales.",
        "Los márgenes brutos alcanzaron un notable 72%.",
        "Analistas de Wall Street mejoraron sus precios objetivos."
      ]
    },
    "art-global-markets-geopolitical": {
      "title": "Mercados reaccionan a tensiones geopolíticas con refugio en oro y petróleo",
      "simplified_summary": "Las tensiones marítimas internacionales impulsaron los precios del petróleo y del oro, mientras los mercados bursátiles retrocedieron.",
      "what_happened": "Las interrupciones en rutas marítimas generaron temores sobre costos de transporte e inflación energética.",
      "why_it_matters": "Petróleo más caro se traduce en combustible más costoso y aumento de precios en bienes esenciales.",
      "market_impact": "El crudo subió casi 4%, el oro ganó atractivo refugio y las bolsas cerraron con pérdidas moderadas.",
      "key_takeaways": [
        "El crudo Brent subió 3.8% por riesgos en rutas de navegación.",
        "Inversores trasladaron liquidez a activos seguros como el oro.",
        "Mayores costos de envío podrían retrasar el alivio inflacionario."
      ]
    },
    "art-crypto-etf-inflows": {
      "title": "Entradas institucionales a ETFs de Bitcoin alcanzan $1.5 mil millones semanales",
      "simplified_summary": "Fondos de pensiones y asesores de patrimonio destinaron más de $1.5 mil millones a ETFs de Bitcoin regulados esta semana.",
      "what_happened": "Los ETFs spot de Bitcoin experimentaron flujos récord de capital institucional regulado.",
      "why_it_matters": "Los fondos regulados facilitan a inversores comunes acceder a criptoactivos desde sus cuentas tradicionales de inversión.",
      "market_impact": "Las compras institucionales constantes absorben ventas y estabilizan la volatilidad del mercado.",
      "key_takeaways": [
        "Más de $1.5 mil millones ingresaron a ETFs de Bitcoin en una semana.",
        "Asesores tradicionales recomiendan asignaciones del 1% al 3%.",
        "La demanda institucional respalda valoraciones más sólidas."
      ]
    },
    "art-retail-banking-margins": {
      "title": "Grandes bancos reportan sólida solvencia crediticia y márgenes en expansión",
      "simplified_summary": "Los mayores bancos obtuvieron fuertes beneficios gracias a que los consumidores pagan a tiempo y los préstamos rinden mayores márgenes.",
      "what_happened": "Los bancos superaron expectativas con bajas tasas de impago e ingresos por intereses en alza.",
      "why_it_matters": "Bancos saludables indican que la economía del consumidor resiste y el crédito para comprar casas o emprender sigue disponible.",
      "market_impact": "Las acciones bancarias subieron, reforzando la confianza en la estabilidad del sistema financiero.",
      "key_takeaways": [
        "Las tasas de morosidad continúan por debajo de los promedios históricos.",
        "Los bancos aprovechan el diferencial entre tasas de depósitos y préstamos.",
        "El sector bancario ofrece un sólido soporte frente a riesgos recesivos."
      ]
    }
  },
  "French": {
    "art-fed-rate-hike": {
      "title": "La Fed signale de potentielles hausses de taux face à l'inflation tenace",
      "simplified_summary": "La Réserve fédérale a indiqué que les taux d'intérêt resteront élevés car les prix ne baissent pas aussi vite que prévu.",
      "what_happened": "La banque centrale a averti que l'inflation dépasse toujours son objectif de 2% et justifie le maintien de taux élevés.",
      "why_it_matters": "Des taux plus élevés rendent le crédit plus cher pour l'immobilier, les cartes de crédit et les prêts aux entreprises.",
      "market_impact": "Les rendements obligataires ont grimpé et les bourses ont reculé face au coût accru du crédit.",
      "key_takeaways": [
        "Les taux d'intérêt devraient rester élevés plus longtemps.",
        "Le coût des prêts immobiliers et à la consommation restera soutenu.",
        "Les rendements des bons du Trésor ont augmenté de 14 points de base."
      ]
    },
    "art-tech-rally": {
      "title": "Les valeurs technologiques bondissent grâce aux résultats solides dans l'IA",
      "simplified_summary": "Les cours des actions technologiques ont grimpé après des bénéfices records dans les semi-conducteurs et l'infrastructure IA.",
      "what_happened": "Les leaders de la tech ont dépassé les prévisions de Wall Street et rehaussé leurs perspectives annuelles.",
      "why_it_matters": "Des bénéfices robustes prouvent que l'adoption de l'IA génère une vraie croissance économique et soutient l'épargne.",
      "market_impact": "Le Nasdaq a progressé de 2,4% et a entraîné l'ensemble des marchés boursiers à la hausse.",
      "key_takeaways": [
        "Les investissements dans l'IA génèrent des flux de trésorerie concrets.",
        "Les marges brutes de la tech atteignent 72%.",
        "Les analystes financiers ont relevé leurs objectifs de cours."
      ]
    },
    "art-global-markets-geopolitical": {
      "title": "Les marchés réagissent aux tensions géopolitiques avec un repli vers l'or et le pétrole",
      "simplified_summary": "Les tensions maritimes internationales ont fait grimper le pétrole et l'or, tandis que les actions ont fléchi.",
      "what_happened": "Les perturbations du fret maritime ont fait craindre une hausse du carburant et des retards d'approvisionnement.",
      "why_it_matters": "Un pétrole plus cher renchérit l'essence à la pompe et le prix des biens de consommation en magasin.",
      "market_impact": "Le baril de brut a gagné 3,8%, l'or a joué son rôle de valeur refuge et les actions ont baissé.",
      "key_takeaways": [
        "Le pétrole Brent a progressé de 3,8% en raison des risques de transit.",
        "Les investisseurs ont privilégié les actifs refuges comme l'or.",
        "Les frais de transport accrus pourraient freiner la désinflation."
      ]
    },
    "art-crypto-etf-inflows": {
      "title": "Les entrées institutionnelles dans les ETF Bitcoin atteignent 1,5 milliard de dollars",
      "simplified_summary": "De grands fonds d'investissement ont injecté 1,5 milliard de dollars dans les ETF Bitcoin cette semaine, confirmant l'adoption institutionnelle.",
      "what_happened": "Les ETF Bitcoin au comptant ont enregistré une vague d'investissements de la part de gestionnaires de patrimoine.",
      "why_it_matters": "Ces fonds régulés permettent aux épargnants d'investir facilement dans les actifs numériques depuis un compte de courtage classique.",
      "market_impact": "La demande institutionnelle régulière stabilise les cours et absorbe la volatilité des cryptomonnaies.",
      "key_takeaways": [
        "1,5 milliard de dollars alloués aux ETF Bitcoin en une seule semaine.",
        "Les conseillers financiers recommandent des pondérations de 1 à 3%.",
        "L'intérêt institutionnel structure durablement le marché."
      ]
    },
    "art-retail-banking-margins": {
      "title": "Les grandes banques affichent un crédit résilient et des marges d'intérêt en hausse",
      "simplified_summary": "Les grandes banques ont enregistré de solides bénéfices grâce au remboursement ponctuel des emprunts par les ménages.",
      "what_happened": "Les banques ont battu le consensus avec des défauts de crédit historiquement bas et des revenus d'intérêt croissants.",
      "why_it_matters": "La solidité bancaire prouve que les ménages gèrent bien leur budget et que le crédit reste accessible pour l'économie.",
      "market_impact": "Les valeurs bancaires ont progressé, renforçant la confiance dans la stabilité macroéconomique.",
      "key_takeaways": [
        "Le taux de défaut des emprunteurs reste inférieur aux moyennes historiques.",
        "Les banques tirent parti de l'écart entre taux de dépôt et taux de prêt.",
        "Le secteur bancaire offre un rempart efficace contre la récession."
      ]
    }
  },
  "German": {
    "art-fed-rate-hike": {
      "title": "Fed signalisiert mögliche Zinserhöhung wegen anhaltender Inflationssorgen",
      "simplified_summary": "Die US-Notenbank Federal Reserve deutete an, dass die Zinssätze länger hoch bleiben, da die Inflation langsamer sinkt als erwartet.",
      "what_happened": "Die Notenbank warnte, dass die Teuerungsrate über dem 2%-Ziel verharrt und weitere Straffungen nötig sein könnten.",
      "why_it_matters": "Höhere Zinsen verteuern Kredite für Immobilien, Konsum und Unternehmensinvestitionen spürbar.",
      "market_impact": "Die Renditen von Staatsanleihen kletterten und die Aktienmärkte gaben angesichts teurerer Kredite nach.",
      "key_takeaways": [
        "Zinssätze bleiben voraussichtlich über längere Zeit erhöht.",
        "Baufinanzierungen und Kreditkartenkosten bleiben teuer.",
        "Die Rendite 10-jähriger US-Staatsanleihen stieg um 14 Basispunkte."
      ]
    },
    "art-tech-rally": {
      "title": "Tech-Aktien legen dank starker KI-Gewinne und Cloud-Margen deutlich zu",
      "simplified_summary": "Die Kurse großer Technologiekonzerne stiegen kräftig, nachdem Halbleiter- und KI-Unternehmen Rekordergebnisse meldeten.",
      "what_happened": "Große Tech-Unternehmen übertrafen die Schätzungen der Wall Street und hoben ihre Jahresprognosen an.",
      "why_it_matters": "Robuste Unternehmensgewinne belegen, dass Investitionen in KI reales Wirtschaftswachstum und Arbeitsplätze schaffen.",
      "market_impact": "Der Nasdaq stieg um 2,4% und zog die weltweiten Leitindizes mit nach oben.",
      "key_takeaways": [
        "Ausgaben für KI-Infrastruktur generieren reale Unternehmensumsätze.",
        "Die Bruttomargen der Tech-Riesen erreichten beachtliche 72%.",
        "Führende Analysten erhöhten ihre Kursziele."
      ]
    },
    "art-global-markets-geopolitical": {
      "title": "Märkte reagieren auf geopolitische Spannungen mit Flucht in Öl und Gold",
      "simplified_summary": "Internationale Spannungen führten zu steigenden Öl- und Goldpreisen, während die Aktienmärkte nachgaben.",
      "what_happened": "Störungen in maritimen Schifffahrtsrouten schürten Sorgen vor Lieferengpässen und Energiepreissteigerungen.",
      "why_it_matters": "Höhere Rohölpreise bedeuten teurere Treibstoffkosten und steigende Preise für Alltagswaren im Handel.",
      "market_impact": "Rohöl verteuerte sich um 3,8%, Gold war als sicherer Hafen gefragt und Aktienindizes gaben leicht nach.",
      "key_takeaways": [
        "Brent-Öl stieg wegen Schifffahrtsrisiken um 3,8%.",
        "Investoren schichteten Kapital in sichere Sachwerte wie Gold um.",
        "Erhöhte Frachtraten könnten den Inflationsrückgang verlangsamen."
      ]
    },
    "art-crypto-etf-inflows": {
      "title": "Institutionelle Zuflüsse in Bitcoin-ETFs erreichen wöchentlichen Meilenstein von 1,5 Mrd. Dollar",
      "simplified_summary": "Große Vermögensverwalter und Fonds investierten diese Woche über 1,5 Milliarden Dollar in regulierte Bitcoin-ETFs.",
      "what_happened": "Spot-Bitcoin-ETFs verzeichneten Rekordzuflüsse von Pensionskassen und institutionellen Investoren.",
      "why_it_matters": "Regulierte Fonds erleichtern es auch Privatanlegern, Kryptoanlagen sicher über ihr normales Bankdepot beizumischen.",
      "market_impact": "Kontinuierliche institutionelle Nachfrage absorbiert Verkaufsdruck und dämpft Kursschwankungen.",
      "key_takeaways": [
        "1,5 Milliarden US-Dollar flossen in nur einer Woche in Bitcoin-ETFs.",
        "Vermögensberater empfehlen eine defensive Portfolio-Beimischung von 1 bis 3%.",
        "Institutionelle Nachfrage stabilisiert die Gesamtmarktbewertung."
      ]
    },
    "art-retail-banking-margins": {
      "title": "Großbanken melden solide Konsumentenkredite und wachsende Zinsmargen",
      "simplified_summary": "Die führenden Banken erzielten hohe Gewinne, da Kunden ihre Kredite verlässlich bedienen und Zinserträge steigen.",
      "what_happened": "Banken übertrafen die Erwartungen mit geringen Kreditausfällen und steigenden Nettozinserträgen.",
      "why_it_matters": "Ein stabiler Bankensektor signalisiert eine gesunde Konsumentenbasis und sichert die Kreditversorgung der Wirtschaft.",
      "market_impact": "Bankaktien legten zu und stärkten das Vertrauen in die Stabilität des Finanzsystems.",
      "key_takeaways": [
        "Kreditausfallraten liegen weiterhin unter dem historischen Durchschnitt.",
        "Banken profitieren von der Spanne zwischen Einlagen- und Kreditzinsen.",
        "Der Bankensektor bietet ein verlässliches Fundament gegen Rezessionsrisiken."
      ]
    }
  }
};

const CLIENT_FALLBACK_GLOSSARY = [
  {
    "term": "Inflation",
    "definition": "The rate at which general prices for goods and services increase over time, eroding the purchasing power of money.",
    "category": "Macroeconomics",
    "example": "When inflation is 6%, a grocery basket that cost $100 last year now costs $106.",
    "why_it_matters": "High inflation reduces the real value of cash savings, forcing investors into assets that outpace rising prices."
  },
  {
    "term": "Deflation",
    "definition": "A persistent decrease in the general price level of goods and services, often accompanied by slowing economic activity.",
    "category": "Macroeconomics",
    "example": "Deflation can cause consumers to delay purchases, leading businesses to cut production and lay off workers.",
    "why_it_matters": "While cheaper prices sound good, prolonged deflation can spark economic recessions and debt distress."
  },
  {
    "term": "Stagflation",
    "definition": "A toxic economic condition characterized by slow economic growth, high unemployment, and high inflation occurring simultaneously.",
    "category": "Macroeconomics",
    "example": "The 1970s oil shocks triggered severe stagflation across major developed economies.",
    "why_it_matters": "It is central banks' worst nightmare because raising rates to fight inflation worsens unemployment."
  },
  {
    "term": "Hyperinflation",
    "definition": "Rapid, excessive, and out-of-control price increases in an economy, typically exceeding 50% per month.",
    "category": "Macroeconomics",
    "example": "During hyperinflation in Zimbabwe, prices doubled every few days, rendering local currency worthless.",
    "why_it_matters": "Completely destroys trust in fiat currency and causes citizens to flee to gold, foreign currency, or barter."
  },
  {
    "term": "Gdp",
    "definition": "Gross Domestic Product: the total monetary value of all finished goods and services produced within a country during a specific period.",
    "category": "Macroeconomics",
    "example": "US real GDP expanded at a 2.8% annualized rate last quarter, signaling economic resilience.",
    "why_it_matters": "It is the scorecard of a country's economic health; sustained GDP growth typically supports corporate revenue."
  },
  {
    "term": "Cpi",
    "definition": "Consumer Price Index: a benchmark monthly metric tracking the average change over time in prices paid by urban consumers for a market basket of goods.",
    "category": "Macroeconomics",
    "example": "The Core CPI report excluded volatile food and energy components to measure baseline inflation trends.",
    "why_it_matters": "Central banks closely watch CPI data when determining whether to hike, cut, or hold benchmark interest rates."
  },
  {
    "term": "Ppi",
    "definition": "Producer Price Index: a measure of the average change over time in the selling prices received by domestic producers for their output (wholesale inflation).",
    "category": "Macroeconomics",
    "example": "A higher-than-expected PPI often precedes rising consumer prices as manufacturers pass higher costs to retail buyers.",
    "why_it_matters": "Acts as an early leading indicator for future consumer inflation."
  },
  {
    "term": "Pce",
    "definition": "Personal Consumption Expenditures Price Index: the primary metric preferred by the Federal Reserve to gauge inflation and consumer spending behavior.",
    "category": "Macroeconomics",
    "example": "The Fed targets a 2% Core PCE inflation rate over the longer term.",
    "why_it_matters": "Because it adjusts for changes in consumer substitution habits, the Fed treats PCE as its gold standard."
  },
  {
    "term": "Interest Rates",
    "definition": "The cost of borrowing money or the reward for saving it, set as a percentage of the total borrowed or invested amount.",
    "category": "Interest Rates",
    "example": "When interest rates climb, auto loans and 30-year home mortgages become significantly more expensive.",
    "why_it_matters": "Interest rates dictate the cost of capital across the entire global financial ecosystem."
  },
  {
    "term": "Repo Rate",
    "definition": "The rate at which a country's central bank lends short-term money to commercial banks against government securities.",
    "category": "Monetary Policy",
    "example": "The Reserve Bank of India (RBI) kept the repo rate unchanged at 6.50% to maintain price stability.",
    "why_it_matters": "When repo rates go up, commercial banks raise their loan interest rates (home loans, auto loans, business credit)."
  },
  {
    "term": "Reverse Repo Rate",
    "definition": "The interest rate at which the central bank borrows money from commercial banks within the country.",
    "category": "Monetary Policy",
    "example": "Banks park excess overnight liquidity with the central bank via the reverse repo window.",
    "why_it_matters": "Absorbs excess liquidity from the banking system to manage currency strength and inflation."
  },
  {
    "term": "Federal Funds Rate",
    "definition": "The target interest rate set by the FOMC at which US commercial banks borrow and lend their excess reserves to each other overnight.",
    "category": "Monetary Policy",
    "example": "The Federal Reserve held the federal funds rate in the 5.25%\u20135.50% corridor.",
    "why_it_matters": "Serves as the benchmark for US prime rates, mortgages, corporate loans, and Treasury yields."
  },
  {
    "term": "Basis Points",
    "definition": "A standard unit of measure for interest rates and financial percentages. 1 basis point equals 0.01% (or 1/100th of 1%).",
    "category": "Interest Rates",
    "example": "A 50 basis point hike means the rate rose by 0.50% (e.g. from 4.00% to 4.50%).",
    "why_it_matters": "Provides unambiguous clarity when discussing tiny interest rate or bond yield movements."
  },
  {
    "term": "Bps",
    "definition": "Short for basis points. 100 bps = 1.00% interest rate shift.",
    "category": "Interest Rates",
    "example": "Yields surged 15 bps following the unexpected employment surge.",
    "why_it_matters": "Industry shorthand widely used across trading floors and central bank briefings."
  },
  {
    "term": "Fomc",
    "definition": "Federal Open Market Committee: the 12-member committee of the Federal Reserve responsible for setting national monetary policy and interest rates.",
    "category": "Monetary Policy",
    "example": "Markets rallied as the FOMC statement hinted at upcoming rate cuts.",
    "why_it_matters": "Every FOMC meeting and press conference has the power to shift billions of dollars in global markets."
  },
  {
    "term": "Hawkish",
    "definition": "An economic stance favoring higher interest rates and monetary tightening to combat inflation, even if it slows economic growth.",
    "category": "Monetary Policy",
    "example": "The Fed chairman gave a hawkish speech warning that interest rates must stay higher for longer.",
    "why_it_matters": "Hawkish stances usually support currency strength while putting downward pressure on high-growth stock valuations."
  },
  {
    "term": "Dovish",
    "definition": "An economic stance favoring lower interest rates, cheap borrowing, and monetary easing to stimulate employment and economic expansion.",
    "category": "Monetary Policy",
    "example": "Dovish remarks from central bankers sent tech stocks rallying as borrowing costs were expected to drop.",
    "why_it_matters": "Dovish policy tends to boost equities, real estate, and risk assets by expanding liquidity."
  },
  {
    "term": "Quantitative Easing",
    "definition": "An unconventional monetary policy where a central bank creates new reserves to buy long-term government bonds, injecting liquidity directly into the economy.",
    "category": "Monetary Policy",
    "example": "Quantitative easing was heavily deployed in 2008 and 2020 to lower long-term yields and encourage lending.",
    "why_it_matters": "Expands central bank balance sheets and pumps huge liquidity into capital markets."
  },
  {
    "term": "Quantitative Tightening",
    "definition": "The reversal of QE, where a central bank shrinks its balance sheet by allowing mature bonds to roll off without reinvestment, pulling cash out of the banking system.",
    "category": "Monetary Policy",
    "example": "Quantitative tightening drains bank reserves and can raise borrowing costs for corporations.",
    "why_it_matters": "Tightens liquidity conditions and removes the artificial floor under asset prices."
  },
  {
    "term": "Recession",
    "definition": "A significant, widespread, and prolonged downturn in economic activity, conventionally marked by two consecutive quarters of negative GDP growth.",
    "category": "Macroeconomics",
    "example": "Consumer confidence plunged and corporate hiring slowed, fueling fears of an impending recession.",
    "why_it_matters": "Recessions bring higher unemployment, reduced corporate earnings, and defensive investor rotation."
  },
  {
    "term": "Soft Landing",
    "definition": "A rare economic feat where a central bank successfully brings down high inflation by hiking rates without triggering a recession or massive job losses.",
    "category": "Macroeconomics",
    "example": "Optimists believe resilient consumer spending could allow the economy to achieve a soft landing.",
    "why_it_matters": "Preserves jobs and allows stock markets to thrive without enduring the pain of an economic slump."
  },
  {
    "term": "Fiscal Policy",
    "definition": "Government decisions regarding taxation, public spending, and borrowing to influence aggregate economic performance.",
    "category": "Macroeconomics",
    "example": "Large fiscal stimulus packages during downturns boost public infrastructure and consumer subsidies.",
    "why_it_matters": "Works alongside monetary policy to shape national debt, consumer demand, and sector growth."
  },
  {
    "term": "Monetary Policy",
    "definition": "The actions taken by a nation's central bank to control the overall money supply and achieve economic goals like price stability and maximum employment.",
    "category": "Monetary Policy",
    "example": "The central bank adopted a restrictive monetary policy stance to curb wage-price spirals.",
    "why_it_matters": "Directly controls base interest rates, reserve ratios, and currency circulation."
  },
  {
    "term": "Bull Market",
    "definition": "A market condition characterized by sustained rising prices, strong corporate earnings, investor optimism, and economic expansion.",
    "category": "Stock Market",
    "example": "The S&P 500 bull market has gained over 40% from its cyclical low.",
    "why_it_matters": "In a bull market, investor sentiment is positive and broad market indices generate attractive returns."
  },
  {
    "term": "Bear Market",
    "definition": "A prolonged period of declining asset prices, traditionally defined as a drop of 20% or more from recent peak highs across major indices.",
    "category": "Stock Market",
    "example": "Tech equities entered a bear market as rising discount rates compressed valuation multiples.",
    "why_it_matters": "Presents severe volatility and emotional panic, but historically offers superior long-term entry points for patient investors."
  },
  {
    "term": "Market Correction",
    "definition": "A short-term decline of between 10% and 20% in the price of a stock, bond, commodity, or market index from its recent peak.",
    "category": "Stock Market",
    "example": "After a relentless five-month rally, the benchmark index suffered a healthy 11% market correction.",
    "why_it_matters": "Corrections relieve speculative froth in asset valuations and occur on average every 12 to 18 months."
  },
  {
    "term": "Market Crash",
    "definition": "A sudden, dramatic, and steep collapse in stock or asset prices across a major cross-section of the market, often occurring over a few days.",
    "category": "Stock Market",
    "example": "The Black Monday crash of 1987 saw the Dow Jones drop over 22% in a single trading session.",
    "why_it_matters": "Often driven by panic, automated selling algorithms, margin calls, or sudden systemic shocks."
  },
  {
    "term": "Market Cap",
    "definition": "Market Capitalization: the total aggregate market dollar value of a publicly traded company's outstanding shares (Share Price \u00d7 Total Shares).",
    "category": "Stock Market",
    "example": "Microsoft and Apple boast market caps exceeding $3 trillion, categorizing them as mega-cap titans.",
    "why_it_matters": "Used by institutional investors and indices to classify company size, liquidity, and risk profile."
  },
  {
    "term": "Large Cap",
    "definition": "Companies with a market capitalization typically of $10 billion or more, known for established market leadership and stability.",
    "category": "Stock Market",
    "example": "Blue-chip stocks like Johnson & Johnson and Berkshire Hathaway are quintessential large-cap companies.",
    "why_it_matters": "Forms the defensive core of most diversified equity portfolios."
  },
  {
    "term": "Mid Cap",
    "definition": "Companies with a market capitalization generally between $2 billion and $10 billion, offering a balance between growth potential and corporate stability.",
    "category": "Stock Market",
    "example": "Mid-cap companies often outperform large caps during early-to-mid economic expansions.",
    "why_it_matters": "Provides higher growth potential than mature giants with less volatility than micro caps."
  },
  {
    "term": "Small Cap",
    "definition": "Companies with a market capitalization usually between $300 million and $2 billion, often featuring high growth potential alongside higher business volatility.",
    "category": "Stock Market",
    "example": "Small-cap stocks in the Russell 2000 index are more sensitive to domestic borrowing costs.",
    "why_it_matters": "Can generate explosive multi-bagger returns, but carries elevated risk of bankruptcy during economic downturns."
  },
  {
    "term": "P/E Ratio",
    "definition": "Price-to-Earnings Ratio: a fundamental valuation metric calculated by dividing a company's current stock price by its earnings per share (EPS).",
    "category": "Valuation",
    "example": "If a stock trades at $100 and its annual EPS is $5, its P/E ratio is 20x.",
    "why_it_matters": "Tells you how many dollars investors are willing to pay for every dollar of annual company profit."
  },
  {
    "term": "Price-To-Earnings",
    "definition": "Alternative name for the P/E ratio, comparing market price per share to corporate profit per share.",
    "category": "Valuation",
    "example": "Value investors seek companies trading at low price-to-earnings ratios compared to historical peers.",
    "why_it_matters": "Helps distinguish between overvalued high-expectation stocks and potentially undervalued bargain investments."
  },
  {
    "term": "Peg Ratio",
    "definition": "Price/Earnings-to-Growth Ratio: calculates P/E ratio divided by the projected annual earnings growth rate of the company.",
    "category": "Valuation",
    "example": "A stock with a P/E of 20 and 20% annual earnings growth has an attractive PEG ratio of 1.0.",
    "why_it_matters": "Helps determine whether a high P/E ratio is genuinely justified by rapid underlying corporate expansion."
  },
  {
    "term": "Eps",
    "definition": "Earnings Per Share: a company's net profit divided by the total number of common shares outstanding.",
    "category": "Valuation",
    "example": "A company with $100 million in profit and 50 million shares has an EPS of $2.00.",
    "why_it_matters": "The ultimate bottom-line measure of corporate profitability available to individual equity shareholders."
  },
  {
    "term": "Dividend",
    "definition": "A distribution of a portion of a company's net earnings paid directly to shareholders, commonly distributed in cash on a quarterly basis.",
    "category": "Investing",
    "example": "The oil giant declared a quarterly cash dividend of $0.95 per common share.",
    "why_it_matters": "Provides tangible passive income and reflects stable, mature corporate cash generation."
  },
  {
    "term": "Dividend Yield",
    "definition": "The annual dividend payment per share divided by the current stock price, expressed as a percentage.",
    "category": "Investing",
    "example": "A $4 annual dividend on a $100 stock gives an attractive dividend yield of 4.0%.",
    "why_it_matters": "Allows investors to compare cash yields between dividend stocks and fixed deposits or bonds."
  },
  {
    "term": "Ipo",
    "definition": "Initial Public Offering: the first sale of stock by a private company to institutional and retail public investors on a stock exchange.",
    "category": "Stock Market",
    "example": "The cloud software startup raised $1.2 billion through its high-profile Nasdaq IPO.",
    "why_it_matters": "Allows founders and early venture capital backers to monetize equity and raises capital for future growth."
  },
  {
    "term": "Stock Split",
    "definition": "A corporate action where a company increases its number of outstanding shares while lowering the price per share proportionally.",
    "category": "Corporate Finance",
    "example": "In a 10-for-1 split, a $1,000 share becomes 10 shares priced at $100 each; overall investor wealth remains unchanged.",
    "why_it_matters": "Enhances liquidity and makes single share prices psychologically more affordable for retail investors."
  },
  {
    "term": "Share Buyback",
    "definition": "When a corporation uses its cash reserves to buy back its own shares from the open market, reducing total outstanding shares.",
    "category": "Corporate Finance",
    "example": "Apple announced an unprecedented $110 billion share repurchase authorization.",
    "why_it_matters": "Reduces share count, boosting EPS and signaling management's confidence in the company's valuation."
  },
  {
    "term": "Short Selling",
    "definition": "Borrowing shares from a broker to sell them immediately on the market, aiming to repurchase them at a lower price later and pocket the difference.",
    "category": "Trading",
    "example": "Short sellers who bet against EV stocks suffered heavy losses during the unexpected earnings surge.",
    "why_it_matters": "Enables profiting from asset declines, but carries theoretically infinite upside loss potential."
  },
  {
    "term": "Short Squeeze",
    "definition": "A rapid surge in a stock's price caused by short sellers scrambling to buy back shares to close out losing positions, forcing the price even higher.",
    "category": "Trading",
    "example": "The dramatic retail short squeeze in GameStop caused hedge funds billions in trading losses.",
    "why_it_matters": "Generates violent upward spikes that catch contrarian short traders off guard."
  },
  {
    "term": "Volatility",
    "definition": "A statistical measure of the dispersion of returns for a given asset or market index, representing the magnitude and speed of price fluctuations.",
    "category": "Trading",
    "example": "High implied volatility before earnings announcements causes options contract premiums to expand.",
    "why_it_matters": "Reflects market uncertainty; higher volatility implies greater risk and potential reward."
  },
  {
    "term": "Vix",
    "definition": "The CBOE Volatility Index: a real-time market index representing the market's expectations for 30-day forward-looking volatility in the S&P 500 (the 'Fear Gauge').",
    "category": "Trading",
    "example": "When the VIX spikes above 30, it indicates extreme investor fear and market distress.",
    "why_it_matters": "Useful contrarian indicator; Warren Buffett's 'be greedy when others are fearful' often correlates with elevated VIX readings."
  },
  {
    "term": "Beta",
    "definition": "A measure of a stock's volatility and systematic risk in comparison to the broader market (where market beta is 1.0).",
    "category": "Valuation",
    "example": "A high-growth tech stock with a beta of 1.5 tends to move 15% when the overall market moves 10%.",
    "why_it_matters": "Helps investors evaluate how aggressively a stock will fluctuate relative to index benchmarks."
  },
  {
    "term": "Liquidity",
    "definition": "The ease and speed with which an asset can be converted into cash without triggering a significant impact on its market price.",
    "category": "Markets",
    "example": "Large-cap equities and US Treasuries possess exceptional liquidity, while physical real estate is relatively illiquid.",
    "why_it_matters": "Illiquid assets can trap capital or force deep discounts when an investor needs fast liquidity."
  },
  {
    "term": "Circuit Breaker",
    "definition": "An automatic regulatory mechanism that halts trading across stock exchanges for a specified duration when benchmark indices drop past preset thresholds.",
    "category": "Stock Market",
    "example": "Trading was halted for 15 minutes after the index plunged 7% at market open.",
    "why_it_matters": "Prevents catastrophic market stampedes by giving market participants a cooling-off period to digest breaking news."
  },
  {
    "term": "Bond",
    "definition": "A fixed-income debt instrument where an investor loans money to a government or corporation that borrows the funds for a defined period at a fixed or variable interest rate.",
    "category": "Bonds",
    "example": "Municipalities issue municipal bonds to build highways, hospitals, and water systems.",
    "why_it_matters": "Provides predictable income, capital preservation, and portfolio ballast against equity crashes."
  },
  {
    "term": "Treasury Yield",
    "definition": "The effective annual return earned by an investor on sovereign debt obligations issued by the US government.",
    "category": "Bonds",
    "example": "The 10-year Treasury yield rose to 4.30%, raising corporate borrowing costs across the economy.",
    "why_it_matters": "Regarded as the 'risk-free rate of return', setting the hurdle rate against which all risky investments are judged."
  },
  {
    "term": "Treasury Bills",
    "definition": "Short-term US government debt securities with maturities ranging from a few days to 52 weeks (commonly called T-Bills).",
    "category": "Bonds",
    "example": "Retail investors parked cash in 3-month T-Bills yielding 5.2% annualized.",
    "why_it_matters": "Considered the safest cash-equivalent asset backed by the full faith and credit of the government."
  },
  {
    "term": "Yield Curve",
    "definition": "A graphical line that plots interest rates (yields) of bonds with equal credit quality across differing maturity horizons (e.g. 1 month to 30 years).",
    "category": "Bonds",
    "example": "A normal yield curve slopes upwards because investors demand higher yields for locking up money longer.",
    "why_it_matters": "The shape of the yield curve reveals market expectations for future economic growth and inflation."
  },
  {
    "term": "Yield Curve Inversion",
    "definition": "An unusual financial phenomenon where short-term bond yields exceed long-term yields, historically the most reliable warning signal of a looming recession.",
    "category": "Bonds",
    "example": "When the 2-year Treasury yielded more than the 10-year Treasury, macro analysts flagged recession danger.",
    "why_it_matters": "Has preceded nearly every major US economic recession over the past 60 years."
  },
  {
    "term": "Coupon Rate",
    "definition": "The fixed annual interest rate paid by a bond issuer to the bondholder, expressed as a percentage of the bond's par or face value.",
    "category": "Bonds",
    "example": "A bond with a $1,000 face value and a 5% coupon rate pays $50 in annual interest.",
    "why_it_matters": "Determines the cash flow yield an investor receives throughout the bond's life."
  },
  {
    "term": "Etf",
    "definition": "Exchange-Traded Fund: an investment fund traded on stock exchanges that holds a diversified basket of assets (stocks, bonds, or commodities).",
    "category": "Investing",
    "example": "The SPY ETF tracks the S&P 500 index and trades intraday just like individual stocks.",
    "why_it_matters": "Offers instant broad diversification, high liquidity, and ultra-low annual expense ratios."
  },
  {
    "term": "Index Fund",
    "definition": "A mutual fund or ETF designed to passively replicate the performance of a specific financial market benchmark (e.g. S&P 500, Nifty 50).",
    "category": "Investing",
    "example": "Legendary investor Warren Buffett recommends low-cost index funds for all non-professional investors.",
    "why_it_matters": "Consistently beats 85%+ of actively managed, high-fee funds over a 15-to-20 year investment horizon."
  },
  {
    "term": "Mutual Fund",
    "definition": "A financial vehicle that pools money from many retail and institutional investors to purchase a managed portfolio of stocks, bonds, or other securities.",
    "category": "Investing",
    "example": "Active mutual funds employ portfolio managers who attempt to outperform market benchmarks.",
    "why_it_matters": "Allows individuals with small amounts of capital to access professional diversification."
  },
  {
    "term": "Sip",
    "definition": "Systematic Investment Plan: an investment strategy where an investor commits to investing a predetermined fixed sum of money at regular intervals (monthly/weekly).",
    "category": "Investing",
    "example": "Setting up a $250 monthly SIP into an index fund automates long-term wealth building.",
    "why_it_matters": "Eliminates emotional market timing and harnesses dollar-cost averaging effortlessly."
  },
  {
    "term": "Dollar Cost Averaging",
    "definition": "The practice of investing a fixed dollar amount into a security on a regular schedule, regardless of share price.",
    "category": "Investing",
    "example": "By practicing DCA, you automatically buy more shares when prices are depressed and fewer when prices are elevated.",
    "why_it_matters": "Lowers your average cost per share over time and removes the anxiety of timing market peaks."
  },
  {
    "term": "Dca",
    "definition": "Short acronym for Dollar Cost Averaging, a proven disciplined wealth accumulation method.",
    "category": "Investing",
    "example": "DCA is widely recommended for crypto and stock accumulation to navigate volatility.",
    "why_it_matters": "Disciplines investors to buy consistently through bear markets."
  },
  {
    "term": "Compounding",
    "definition": "The process where the earnings generated by an investment are reinvested to generate their own earnings over time (earning interest on interest).",
    "category": "Investing",
    "example": "Albert Einstein famously called compound interest the eighth wonder of the world.",
    "why_it_matters": "Enables modest monthly savings to multiply into substantial fortunes over several decades."
  },
  {
    "term": "Rule Of 72",
    "definition": "A quick mathematical shortcut to estimate the number of years required to double your investment: divide 72 by the annual rate of return.",
    "category": "Investing",
    "example": "At an 8% annual return, your money doubles in approximately 9 years (72 / 8 = 9).",
    "why_it_matters": "Allows instant mental math for evaluating investment opportunities and compounding horizons."
  },
  {
    "term": "Asset Allocation",
    "definition": "An investment strategy aimed at balancing risk and reward by dividing a portfolio's capital among major asset classes (equities, bonds, real estate, cash).",
    "category": "Investing",
    "example": "A traditional balanced portfolio often uses a 60% equities and 40% fixed income asset allocation.",
    "why_it_matters": "Determines over 90% of a portfolio's return variability and downside protection."
  },
  {
    "term": "Portfolio Diversification",
    "definition": "The risk management technique that mixes a wide variety of investments within a portfolio to limit exposure to any single asset or sector.",
    "category": "Investing",
    "example": "'Don't put all your eggs in one basket' is the founding principle of diversification.",
    "why_it_matters": "Reduces unsystematic risk without sacrificing long-term expected returns."
  },
  {
    "term": "Emergency Fund",
    "definition": "A cash reserve specifically set aside to cover unexpected life emergencies, such as job loss, medical bills, or major car repairs.",
    "category": "Personal Finance",
    "example": "Financial experts advise keeping 3 to 6 months of baseline living expenses in a liquid high-yield savings account.",
    "why_it_matters": "Prevents you from having to liquidate investments at a steep loss during sudden market downturns."
  },
  {
    "term": "Reit",
    "definition": "Real Estate Investment Trust: a company that owns, operates, or finances income-producing real estate and trades on public stock exchanges.",
    "category": "Investing",
    "example": "By law, US REITs must distribute at least 90% of their taxable income to shareholders as dividends.",
    "why_it_matters": "Allows retail investors to profit from commercial real estate with small sums and daily liquidity."
  },
  {
    "term": "Ebitda",
    "definition": "Earnings Before Interest, Taxes, Depreciation, and Amortization: a metric used to evaluate a company's raw operational performance without financing decisions or accounting methods.",
    "category": "Corporate Finance",
    "example": "The cloud enterprise firm generated an adjusted EBITDA margin of 32%.",
    "why_it_matters": "Provides a clean proxy for core operating cash generation, widely used in acquisitions."
  },
  {
    "term": "Balance Sheet",
    "definition": "A core financial statement summarizing a company's assets, liabilities, and shareholders' equity at a specific point in time (Assets = Liabilities + Equity).",
    "category": "Corporate Finance",
    "example": "A strong balance sheet with substantial cash and minimal short-term debt shields companies during recessions.",
    "why_it_matters": "Shows financial solvency, working capital health, and debt obligations."
  },
  {
    "term": "Free Cash Flow",
    "definition": "The cash a company produces through its operations minus its capital expenditures (investments in physical assets like equipment or factories).",
    "category": "Corporate Finance",
    "example": "High free cash flow allows firms to pay dividends, repurchase shares, and fund R&D without borrowing.",
    "why_it_matters": "The purest indicator of actual discretionary cash generation available to shareholders."
  },
  {
    "term": "Fcf",
    "definition": "Short for Free Cash Flow.",
    "category": "Corporate Finance",
    "example": "With $10B in annual FCF, the tech leader easily financed its AI infrastructure expansion.",
    "why_it_matters": "Discounted Free Cash Flow (DCF) forms the foundation of intrinsic valuation models."
  },
  {
    "term": "Roe",
    "definition": "Return on Equity: a measure of financial performance calculated by dividing net income by shareholders' equity.",
    "category": "Corporate Finance",
    "example": "A consistent ROE above 15% signifies that management is effectively allocating shareholders' capital.",
    "why_it_matters": "Measures corporate profitability efficiency from the perspective of an equity investor."
  },
  {
    "term": "Apr",
    "definition": "Annual Percentage Rate: the annual cost of borrowing money, including interest and fees charged by lenders.",
    "category": "Banking",
    "example": "Credit cards frequently charge an APR of 22% or higher on unpaid monthly balances.",
    "why_it_matters": "Standardizes the true cost of consumer loans, auto financing, and revolving credit."
  },
  {
    "term": "Apy",
    "definition": "Annual Percentage Yield: the real rate of return earned on a deposit over one year, taking into account the effect of compounding interest.",
    "category": "Banking",
    "example": "A high-yield savings account offering 5.0% APY compounded daily yields more than 5.0% simple interest.",
    "why_it_matters": "Crucial for comparing savings accounts, certificates of deposit, and money market funds."
  },
  {
    "term": "Credit Score",
    "definition": "A numerical expression (typically 300 to 850) based on an analysis of a person's credit files, representing creditworthiness.",
    "category": "Banking",
    "example": "Maintaining a credit score above 750 qualifies borrowers for the lowest interest rates on home mortgages.",
    "why_it_matters": "Dictates your eligibility and pricing for mortgages, car loans, rental apartments, and insurance."
  },
  {
    "term": "Cibil Score",
    "definition": "India's premier 3-digit credit score (ranging between 300 and 900) calculated by TransUnion CIBIL based on repayment history.",
    "category": "Banking",
    "example": "Indian banks typically look for a CIBIL score of 750 or higher when approving unsecured personal loans.",
    "why_it_matters": "Critical metric in Indian banking for loan approvals and credit card issuances."
  },
  {
    "term": "Fixed Deposit",
    "definition": "A financial instrument provided by banks that provides investors a higher rate of interest than regular savings accounts until a fixed maturity date.",
    "category": "Banking",
    "example": "Senior citizens often lock in 1-year bank Fixed Deposits (FDs) for guaranteed quarterly interest.",
    "why_it_matters": "Offers guaranteed, risk-free capital preservation with predictable income."
  },
  {
    "term": "Fd",
    "definition": "Short for Fixed Deposit.",
    "category": "Banking",
    "example": "Many conservative investors prefer bank FDs to avoid stock market volatility.",
    "why_it_matters": "Popular savings tool in India and emerging markets."
  },
  {
    "term": "Options",
    "definition": "Financial derivatives that give the buyer the right, but not the obligation, to buy (Call) or sell (Put) an underlying asset at an agreed price within a specific timeframe.",
    "category": "Derivatives",
    "example": "Traders use options contracts to hedge their stock portfolios against sudden price crashes.",
    "why_it_matters": "Provides tremendous leverage and risk hedging capabilities, but can expire completely worthless."
  },
  {
    "term": "Call Option",
    "definition": "A contract that gives the holder the right to buy an underlying asset at a specified strike price prior to expiration.",
    "category": "Derivatives",
    "example": "Buying a call option is a bullish bet that the stock price will rise above the strike price.",
    "why_it_matters": "Allows upside equity participation with limited upfront capital."
  },
  {
    "term": "Put Option",
    "definition": "A contract that gives the holder the right to sell an underlying asset at a specified strike price prior to expiration.",
    "category": "Derivatives",
    "example": "Portfolio managers purchase put options as insurance against a market downturn.",
    "why_it_matters": "Acts as portfolio disaster insurance or an instrument to profit from falling prices."
  },
  {
    "term": "Leverage",
    "definition": "The use of borrowed capital or financial derivatives to increase the potential return of an investment.",
    "category": "Trading",
    "example": "Trading with 10x leverage magnifies both your percentage gains and your percentage losses ten-fold.",
    "why_it_matters": "A double-edged sword that can wipe out an entire trading account in a matter of seconds."
  },
  {
    "term": "Cryptocurrency",
    "definition": "A digital or virtual currency that is secured by cryptography, operating on decentralized peer-to-peer networks.",
    "category": "Cryptocurrency",
    "example": "Bitcoin and Ethereum are the two largest cryptocurrencies by market capitalization.",
    "why_it_matters": "Enables borderless, censorship-resistant transfers of value without central intermediaries."
  },
  {
    "term": "Bitcoin",
    "definition": "The first decentralized peer-to-peer digital currency created in 2009 by pseudonymous creator Satoshi Nakamoto, with a capped supply of 21 million coins.",
    "category": "Cryptocurrency",
    "example": "Spot Bitcoin ETFs have brought hundreds of millions in institutional inflows.",
    "why_it_matters": "Often viewed as 'Digital Gold' due to its strict mathematical scarcity and decentralization."
  },
  {
    "term": "Ethereum",
    "definition": "A decentralized open-source blockchain network featuring smart contract functionality, powered by its native cryptocurrency Ether (ETH).",
    "category": "Cryptocurrency",
    "example": "Ethereum serves as the foundational operating layer for decentralized finance (DeFi) and NFTs.",
    "why_it_matters": "Pioneered programmable money and decentralized internet applications."
  },
  {
    "term": "Blockchain",
    "definition": "A distributed, immutable digital ledger of transactions maintained by a consensus of computers across a network.",
    "category": "Cryptocurrency",
    "example": "Transactions recorded on a blockchain cannot be modified or deleted retroactively.",
    "why_it_matters": "Eliminates the need for trusted third-party verification in digital transactions."
  },
  {
    "term": "Bitcoin Halving",
    "definition": "An event occurring every 210,000 blocks (roughly every 4 years) where the reward paid to Bitcoin miners for verifying transactions is cut by 50%.",
    "category": "Cryptocurrency",
    "example": "The 2024 halving reduced the block reward from 6.25 BTC to 3.125 BTC.",
    "why_it_matters": "Constrains new supply issuance, historically serving as a major multi-month catalyst for bull cycles."
  },
  {
    "term": "Gold",
    "definition": "A precious metal and monetary commodity that has served as a universal store of value and safe-haven asset for over 5,000 years.",
    "category": "Commodities",
    "example": "Gold hit fresh record highs as investors sought refuge from inflation and geopolitical conflicts.",
    "why_it_matters": "Non-yielding asset that cannot be printed by governments, offering protection against currency debasement."
  },
  {
    "term": "Crude Oil",
    "definition": "A naturally occurring unrefined petroleum product, refined into gasoline, diesel, and petrochemicals; the lifeblood of global industrial transit.",
    "category": "Commodities",
    "example": "Rising crude oil prices directly increase logistics costs, feeding into headline consumer inflation.",
    "why_it_matters": "Global energy costs directly dictate manufacturing and transport inflation worldwide."
  },
  {
    "term": "Brent Crude",
    "definition": "A major trading classification and international benchmark for sweet light crude oil extracted from the North Sea.",
    "category": "Commodities",
    "example": "Brent crude oil traded near $80 per barrel amid shipping disruptions in the Red Sea.",
    "why_it_matters": "Used to price more than two-thirds of the world's internationally traded crude oil supplies."
  },
  {
    "term": "Wti",
    "definition": "West Texas Intermediate: a high-quality, sweet, light crude oil that serves as the benchmark for US petroleum pricing.",
    "category": "Commodities",
    "example": "WTI crude futures settle daily on the New York Mercantile Exchange (NYMEX).",
    "why_it_matters": "Primary pricing standard for American energy production and refining margins."
  },
  {
    "term": "Nifty 50",
    "definition": "The flagship benchmark stock index of the National Stock Exchange of India (NSE), tracking the 50 largest and most liquid Indian blue-chip companies.",
    "category": "Indian Markets",
    "example": "The Nifty 50 scaled past 25,000 points powered by banking and automobile heavyweights.",
    "why_it_matters": "Represents the pulse of India's formal corporate economy and is the world's most traded index derivative."
  },
  {
    "term": "Sensex",
    "definition": "The benchmark index of the Bombay Stock Exchange (BSE), tracking 30 well-established, financially sound companies across key sectors.",
    "category": "Indian Markets",
    "example": "The BSE Sensex is India's oldest stock index, established in 1986.",
    "why_it_matters": "The most widely quoted barometer of Indian stock market wealth and sentiment."
  },
  {
    "term": "Sebi",
    "definition": "Securities and Exchange Board of India: the statutory regulatory body governing securities and commodity markets in India.",
    "category": "Indian Markets",
    "example": "SEBI issued new disclosure guidelines to protect retail investors in futures and options trading.",
    "why_it_matters": "Protects investor interests, promotes fair market development, and regulates brokers, mutual funds, and exchanges."
  },
  {
    "term": "Rbi",
    "definition": "Reserve Bank of India: India's central banking institution that controls the monetary policy of the Indian rupee.",
    "category": "Indian Markets",
    "example": "The RBI Monetary Policy Committee maintained an accommodative-to-neutral monetary stance.",
    "why_it_matters": "Controls inflation, manages forex reserves, regulates commercial banking, and oversees India's digital payment rails (UPI)."
  },
  {
    "term": "Demat Account",
    "definition": "Dematerialized Account: an electronic account used in India to hold shares and securities in electronic format instead of physical paper certificates.",
    "category": "Indian Markets",
    "example": "To trade Indian equities, an investor needs a Demat account linked to their trading and bank accounts.",
    "why_it_matters": "Provides safe, seamless, paperless settlement of equity ownership maintained by NSDL and CDSL."
  }
];

function getClientFallbackNews(category = "all", query = "", language = "English") {
    const langDict = (typeof CLIENT_PRETRANSLATED_ARTICLES !== "undefined" && CLIENT_PRETRANSLATED_ARTICLES[language]) || {};
    let list = CLIENT_FALLBACK_ARTICLES.map(art => {
        if (langDict[art.id]) {
            const pre = langDict[art.id];
            return {
                ...art,
                title: pre.title || art.title,
                simplified_summary: pre.simplified_summary || art.simplified_summary,
                what_happened: pre.what_happened || art.what_happened,
                why_it_matters: pre.why_it_matters || art.why_it_matters,
                market_impact: pre.market_impact || art.market_impact,
                key_takeaways: pre.key_takeaways || art.key_takeaways
            };
        }
        return { ...art };
    });
    if (category && category !== "all") {
        list = list.filter(a => a.category === category);
    }
    if (query) {
        const q = query.toLowerCase().trim();
        list = list.filter(a => 
            (a.title && a.title.toLowerCase().includes(q)) ||
            (a.description && a.description.toLowerCase().includes(q)) ||
            (a.simplified_summary && a.simplified_summary.toLowerCase().includes(q)) ||
            (a.what_happened && a.what_happened.toLowerCase().includes(q)) ||
            (a.sector && a.sector.toLowerCase().includes(q))
        );
        if (list.length === 0) {
            list = [{
                id: "art-dynamic-" + Date.now(),
                title: `Market Analysis & Outlook for "${query}"`,
                description: `Comprehensive intelligence breakdown and sector implications regarding ${query}.`,
                content: `Global financial markets and analyst desks are actively evaluating recent trends surrounding ${query}. Institutional and retail investors are assessing risk-adjusted returns, macro catalysts, and price action impact.`,
                url: "https://finance.yahoo.com",
                url_to_image: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&auto=format&fit=crop&q=60",
                source: "FinNews Live Intelligence",
                published_at: "Just Now",
                category: category === "all" ? "tech_stocks" : category,
                sector: "Markets & Macro",
                reading_time_original_mins: 4,
                is_simplified: true,
                simplified_summary: `Financial reports highlight key movements in ${query}. Analysts note this trend influences investor sentiment, sector valuations, and capital allocation.`,
                what_happened: `Active trading and macroeconomic reports brought heightened focus to ${query}.`,
                why_it_matters: `Changes in this sector directly impact borrowing conditions, corporate profit margins, and personal investment portfolios.`,
                market_impact: `Traders and asset managers are repositioning risk exposure with active trading volume.`,
                key_takeaways: [
                    `Key focus on ${query} and broader financial market sentiment.`,
                    "Capital allocation is adjusting across institutional desks.",
                    "Investors are reviewing forward guidance and risk metrics."
                ],
                jargon_terms: [
                    { term: "Volatility", definition: "A measure of how much and how quickly stock or asset prices swing over a given time." },
                    { term: "Liquidity", definition: "How easily an asset or security can be converted into ready cash without affecting its market price." }
                ],
                sentiment: "bullish",
                sentiment_score: 0.65,
                reading_time_simplified_mins: 1
            }];
        }
    }

    const bullishCount = list.filter(a => a.sentiment === "bullish").length;
    const bearishCount = list.filter(a => a.sentiment === "bearish").length;
    const total = list.length;
    let score = 50;
    if (total > 0) {
        score = Math.round(50 + ((bullishCount - bearishCount) / total) * 35);
        score = Math.max(15, Math.min(95, score));
    }
    let mood = "Neutral Balance";
    if (score >= 60) mood = "Bullish Greed";
    else if (score <= 40) mood = "Bearish Fear";

    return {
        articles: list,
        overview: {
            total_articles: total,
            bullish_count: bullishCount,
            bearish_count: bearishCount,
            market_mood: mood,
            market_sentiment_score: score
        }
    };
}

function clientProcessChat(query, articles = []) {
    const low = query.toLowerCase().trim();
    if (!low) {
        return {
            reply: "Hello! I am FinBot, your personal financial assistant. Ask me anything about today's market news, complex terminology, or economic trends!",
            suggested_questions: ["What is today's market sentiment?", "Explain Fed rate hikes simply", "What is EBITDA?"]
        };
    }

    // 1. Date, Time & Market Hours
    if (/(today'?s date|current date|what day is it|what is today|tell me the date)/.test(low)) {
        const now = new Date();
        const dateStr = now.toLocaleDateString("en-US", { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
        const timeStr = now.toLocaleTimeString("en-US", { hour: '2-digit', minute: '2-digit' });
        const isWeekday = now.getDay() >= 1 && now.getDay() <= 5;
        return {
            reply: `### 📅 **Today's Date & Financial Market Status**\n\n` +
                   `• **Today's Date**: **${dateStr}**\n` +
                   `• **Current Local Time**: **${timeStr}**\n\n` +
                   `#### 🏛️ **Global Financial Trading Sessions**:\n` +
                   `- 🇺🇸 **US Markets (NYSE / NASDAQ)**: 9:30 AM – 4:00 PM ET (Mon–Fri) [${isWeekday ? 'Active Trading Day' : 'Weekend - Closed'}]\n` +
                   `- 🇮🇳 **Indian Markets (NSE / BSE)**: 9:15 AM – 3:30 PM IST (Mon–Fri) [${isWeekday ? 'Active Trading Day' : 'Weekend - Closed'}]\n` +
                   `- 🪙 **Crypto Markets (Bitcoin / Ethereum)**: **Open 24/7/365** (Always Active)`,
            suggested_questions: ["What is today's market sentiment?", "Show today's top financial headlines", "Explain stocks vs bonds"]
        };
    }

    // 2. Greetings
    if (/^(hi|hello|hey|help|good morning|good afternoon|good evening|who are you|what can you do)/.test(low) || low === "hi finbot") {
        return {
            reply: `### 🤖 **Hello! I am FinBot, your Personal Financial AI**\n\n` +
                   `I am here to make complex financial concepts, market news, and investing jargon simple and actionable.\n\n` +
                   `Ask me anything about:\n` +
                   `• 📰 **Market News**: Summaries of Fed rates, tech earnings, crypto, or oil.\n` +
                   `• 💡 **Financial Jargon**: Plain English definitions for 90+ terms (EBITDA, P/E Ratio, Repo Rate, CPI, etc.).\n` +
                   `• ⚖️ **Comparisons**: Stocks vs Bonds, ETFs vs Mutual Funds, Bitcoin vs Gold.\n` +
                   `• 🧮 **Formulas**: The Rule of 72, compound interest math, or 50/30/20 budgeting.`,
            suggested_questions: ["What is today's market sentiment?", "Explain the difference between stocks and bonds", "How does compound interest work?"]
        };
    }

    // 3. Comparisons
    if (low.includes(" vs ") || low.includes(" versus ") || low.includes("difference between") || low.includes("compare")) {
        if (low.includes("stock") && low.includes("bond")) {
            return {
                reply: `### ⚖️ **Stocks vs. Bonds: Key Differences**\n\n` +
                       `| Feature | Stocks (Equities) | Bonds (Fixed Income) |\n` +
                       `| :--- | :--- | :--- |\n` +
                       `| **What you are** | Part-owner of the company | Lender to the company/government |\n` +
                       `| **Return Source** | Stock price growth + Dividends | Regular coupon interest payments |\n` +
                       `| **Risk Profile** | Higher (prices fluctuate daily) | Lower (fixed return if held to maturity) |\n` +
                       `| **Bankruptcy Order** | Last in line | Paid before equity shareholders |\n` +
                       `| **Primary Goal** | Long-term capital growth | Capital preservation & steady income |\n\n` +
                       `**Rule of Thumb**: Younger investors usually hold more stocks for long-term growth, while retirees hold more bonds for predictable income.`,
                suggested_questions: ["What is Treasury yield?", "What is an Index Fund?", "What is Dollar-Cost Averaging?"]
            };
        }
        if (low.includes("etf") && (low.includes("mutual fund") || low.includes("fund"))) {
            return {
                reply: `### ⚖️ **ETFs vs. Mutual Funds**\n\n` +
                       `| Feature | ETF (Exchange-Traded Fund) | Mutual Fund |\n` +
                       `| :--- | :--- | :--- |\n` +
                       `| **Trading** | Trades intraday on the stock exchange | Trades once daily after market close (NAV) |\n` +
                       `| **Expense Ratio** | Ultra-low (often 0.03% – 0.20%) | Often higher (0.50% – 1.50%+) |\n` +
                       `| **Minimum Investment** | Price of 1 single share | Often has minimum initial deposit (e.g. $500+) |\n\n` +
                       `**Smart Takeaway**: For most retail investors, low-cost broad index ETFs offer an optimal, tax-efficient way to build long-term wealth.`,
                suggested_questions: ["What is Dollar-Cost Averaging?", "What is the S&P 500 ETF?", "How to start investing?"]
            };
        }
        if ((low.includes("bitcoin") || low.includes("btc") || low.includes("crypto")) && low.includes("gold")) {
            return {
                reply: `### ⚖️ **Bitcoin vs. Physical Gold**\n\n` +
                       `| Feature | Bitcoin ('Digital Gold') | Physical Gold |\n` +
                       `| :--- | :--- | :--- |\n` +
                       `| **Track Record** | 15+ years (since 2009) | 5,000+ years of monetary history |\n` +
                       `| **Supply Limit** | Hard cap at 21,000,000 BTC | Increases ~1.5% annually via mining |\n` +
                       `| **Portability** | Transferred globally in minutes | Heavy and costly to store safely |\n` +
                       `| **Volatility** | High (frequent 20-30% swings) | Low-to-moderate (steady safe-haven) |\n\n` +
                       `**Summary**: Gold remains the established global store of value; Bitcoin offers asymmetric digital scarcity with higher volatility.`,
                suggested_questions: ["What is Bitcoin Halving?", "Why do central banks buy gold?", "What is inflation?"]
            };
        }
        if (low.includes("bull") && low.includes("bear")) {
            return {
                reply: `### ⚖️ **Bull Market vs. Bear Market**\n\n` +
                       `• **Bull Market (📈)**: Prices are rising, the economy is expanding, and investor confidence is strong. (Named after the bull charging upwards with its horns).\n` +
                       `• **Bear Market (📉)**: Prices decline by 20% or more from recent peaks, accompanied by widespread caution or economic slowdown. (Named after the bear swiping downward with its paws).\n\n` +
                       `**Smart Insight**: Bear markets feel scary, but historically they have been the greatest wealth-building opportunities for patient, long-term investors.`,
                suggested_questions: ["What is today's market sentiment?", "What is compound interest?", "How does SIP work?"]
            };
        }
    }

    // 4. Rule of 72
    if (low.includes("rule of 72")) {
        const match = low.match(/(\d+(?:\.\d+)?)\s*%/);
        const rate = match ? parseFloat(match[1]) : 8.0;
        const years = (72 / rate).toFixed(1);
        return {
            reply: `### 🧮 **The Rule of 72 Explained**\n\n` +
                   `The **Rule of 72** is a mental math formula to estimate how many years it will take your investment to double at a given annual return rate.\n\n` +
                   `📌 **Formula**: \\( \\text{Years to Double} = \\frac{72}{\\text{Annual Rate}} \\)\n\n` +
                   `**Calculation for ${rate}% Annual Return**:\n` +
                   `- \\( 72 / ${rate} = \\mathbf{${years}\\text{ years}} \\)\n` +
                   `- An investment of $10,000 will grow to **$20,000** in approx **${years} years**!\n\n` +
                   `• At **6%**: Doubles in **12 years**\n` +
                   `• At **8%**: Doubles in **9 years**\n` +
                   `• At **10%**: Doubles in **7.2 years**\n` +
                   `• At **12%**: Doubles in **6 years**`,
            suggested_questions: ["How does compound interest work?", "What is Dollar-Cost Averaging?", "What is an Index Fund?"]
        };
    }

    // 5. Compound Interest
    if (low.includes("compound interest") || low.includes("compounding")) {
        return {
            reply: `### 📈 **The Power of Compound Interest**\n\n` +
                   `**Compounding** is when you earn interest not only on your original deposit, but also on the interest that accumulated in prior years.\n\n` +
                   `📌 **Formula**: \\( A = P (1 + r/n)^{nt} \\)\n` +
                   `• If you invest **$10,000** at an **8% annual return** for **25 years** without adding any more money:\n` +
                   `• Your account grows into **$68,485**! (Over $58,000 in pure compounding growth).`,
            suggested_questions: ["What is the Rule of 72?", "What is SIP investing?", "What is Inflation?"]
        };
    }

    // 6. Market Sentiment / Overview
    if (low.includes("sentiment") || low.includes("market mood") || low.includes("how is the market")) {
        return {
            reply: `### 📊 **Current Market Sentiment Overview**\n\n` +
                   `• **Overall Tone**: **Bullish Greed / Moderate Optimism** (Score: 68/100)\n` +
                   `• **Tech & AI**: Strong upward momentum supported by high chip and cloud infrastructure earnings.\n` +
                   `• **Central Banks & Fed**: Officials maintain interest rate discipline while monitoring services inflation.\n` +
                   `• **Crypto**: Institutional inflows remain robust across regulated exchange-traded products.`,
            suggested_questions: ["Show today's top financial headlines", "Explain Fed rate hikes simply", "What is EBITDA?"]
        };
    }

    // 7. Search Glossary Terms
    for (const item of CLIENT_FALLBACK_GLOSSARY) {
        const tLower = item.term.toLowerCase();
        if (low === tLower || low === `what is ${tLower}` || low === `what is ${tLower}?` || low.includes(`what is ${tLower}`) || low.includes(`explain ${tLower}`) || low.includes(`meaning of ${tLower}`)) {
            return {
                reply: `### 💡 **${item.term}** Explained Simply\n\n` +
                       `📌 **Definition**: ${item.definition}\n\n` +
                       `📊 **Example**: *"${item.example}"*\n\n` +
                       `⚖️ **Why It Matters to Your Money**: ${item.why_it_matters || "Helps investors gauge market conditions and protect capital."}\n\n` +
                       `🏷️ **Category**: \`${item.category}\``,
                suggested_questions: [`How does ${item.term} affect stock markets?`, "What is today's market sentiment?", "Explain stocks vs bonds"]
            };
        }
    }

    // Generic friendly answer
    return {
        reply: `### 💡 **FinBot Insight**\n\n` +
               `Regarding **"${query}"**:\n\n` +
               `In financial markets, this concept relates to how capital, interest rates, and investor sentiment interact to determine prices and returns.\n\n` +
               `• **Practical Takeaway**: Always evaluate whether this trend impacts your long-term goals or short-term volatility.\n` +
               `• **Risk Awareness**: Keep your portfolio diversified across asset classes (equities, fixed income, cash equivalents) rather than concentrating on a single factor.`,
        suggested_questions: ["Explain stocks vs bonds", "What is today's market sentiment?", "What is compound interest?"]
    };
}
