import os
import json
import asyncio
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import httpx

from app.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CACHE_FILE = BASE_DIR / "data" / "translations_cache.json"

LANG_MAP = {
    "english": "en",
    "hindi": "hi",
    "marathi": "mr",
    "spanish": "es",
    "french": "fr",
    "german": "de"
}

# Pre-translated dictionary for curated sample articles across languages
PRETRANSLATED_ARTICLES = {
    "hindi": {
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
    "marathi": {
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
    "spanish": {
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
    "french": {
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
    "german": {
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
}

class TranslationService:
    _cache: Dict[str, str] = {}
    _loaded: bool = False

    @classmethod
    def _init_cache(cls):
        if cls._loaded:
            return
        cls._loaded = True
        try:
            if CACHE_FILE.exists():
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cls._cache = json.load(f)
        except Exception:
            cls._cache = {}

    @classmethod
    def _save_cache(cls):
        try:
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cls._cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    @classmethod
    async def translate_text(cls, text: str, target_lang: str) -> str:
        if not text or not text.strip():
            return text
        
        target_norm = target_lang.strip().lower()
        if target_norm in ("english", "en"):
            return text

        lang_code = LANG_MAP.get(target_norm, "en")
        if lang_code == "en":
            return text

        cls._init_cache()
        cache_key = f"{lang_code}:{text.strip()}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        # 1. Try Gemini if configured
        if settings.has_gemini_api:
            try:
                translated = await cls._translate_with_gemini(text, target_lang)
                if translated:
                    cls._cache[cache_key] = translated
                    cls._save_cache()
                    return translated
            except Exception:
                pass

        # 2. Try MyMemory Translation API
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get("https://api.mymemory.translated.net/get", params={
                    "q": text[:450],
                    "langpair": f"en|{lang_code}"
                })
                if res.status_code == 200:
                    data = res.json()
                    trans = data.get("responseData", {}).get("translatedText")
                    if trans and "MYMEMORY WARNING" not in trans.upper():
                        cls._cache[cache_key] = trans
                        cls._save_cache()
                        return trans
        except Exception:
            pass

        # Fallback: Return text
        return text

    @classmethod
    async def _translate_with_gemini(cls, text: str, target_lang: str) -> Optional[str]:
        prompt = f"Translate the following financial news text directly into natural, fluent {target_lang}. Return ONLY the translated text:\n\n{text}"
        candidate_models = ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-1.5-flash"]
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 200}
        }
        async with httpx.AsyncClient(timeout=4.0) as client:
            for model in candidate_models:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.gemini_api_key}"
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        trans = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                        if trans:
                            return trans
                except Exception:
                    continue
        return None

    @classmethod
    async def translate_article_data(cls, art_dict: Dict[str, Any], target_lang: str) -> Dict[str, Any]:
        target_norm = target_lang.strip().lower()
        if target_norm in ("english", "en"):
            return art_dict

        art_id = art_dict.get("id", "")
        lang_catalog = PRETRANSLATED_ARTICLES.get(target_norm, {})

        # Check pre-translated high-quality catalog first (instantaneous 0ms latency)
        if art_id in lang_catalog:
            pre = lang_catalog[art_id]
            updated = dict(art_dict)
            updated["title"] = pre.get("title", updated.get("title"))
            updated["simplified_summary"] = pre.get("simplified_summary", updated.get("simplified_summary"))
            updated["what_happened"] = pre.get("what_happened", updated.get("what_happened"))
            updated["why_it_matters"] = pre.get("why_it_matters", updated.get("why_it_matters"))
            updated["market_impact"] = pre.get("market_impact", updated.get("market_impact"))
            updated["key_takeaways"] = pre.get("key_takeaways", updated.get("key_takeaways", []))
            return updated

        # Dynamic translation for live RSS or custom articles
        updated = dict(art_dict)
        try:
            trans_title, trans_sum = await asyncio.gather(
                cls.translate_text(updated.get("title", ""), target_lang),
                cls.translate_text(updated.get("simplified_summary", "") or updated.get("description", ""), target_lang),
                return_exceptions=True
            )
            if not isinstance(trans_title, Exception) and trans_title:
                updated["title"] = trans_title
            if not isinstance(trans_sum, Exception) and trans_sum:
                updated["simplified_summary"] = trans_sum
                updated["what_happened"] = trans_sum

            TEMPLATES = {
                "hindi": {
                    "why_it_matters": "यह विकास व्यक्तिगत वित्त, लोन की ब्याज दरों और निवेश पोर्टफोलियो पर सीधा प्रभाव डालता है।",
                    "market_impact_bullish": "बाजार में सकारात्मक रुख है और निवेशक चुनिंदा क्षेत्रों में खरीदारी बढ़ा रहे हैं।",
                    "market_impact_bearish": "बाजार में सतर्कता और बिकवाली का माहौल है, निवेशक जोखिम घटा रहे हैं।",
                    "market_impact_neutral": "बाजार स्थिर बना हुआ है और आगे के आर्थिक आंकड़ों का इंतजार किया जा रहा है।"
                },
                "marathi": {
                    "why_it_matters": "या घडामोडीचा थेट परिणाम वैयक्तिक वित्त, कर्जाचे व्याजदर आणि गुंतवणूक पोर्टफोलिओवर होतो.",
                    "market_impact_bullish": "बाजारात सकारात्मक कल असून गुंतवणूकदार विशिष्ट क्षेत्रांमध्ये खरेदी वाढवत आहेत.",
                    "market_impact_bearish": "बाजारात सावधगिरीचे वातावरण असून गुंतवणूकदार जोखीम कमी करत आहेत.",
                    "market_impact_neutral": "बाजार स्थिर असून पुढील आर्थिक आकडेवारीची प्रतीक्षा केली जात आहे."
                },
                "spanish": {
                    "why_it_matters": "Este acontecimiento influye directamente en las finanzas personales, tasas de interés e inversiones.",
                    "market_impact_bullish": "El mercado muestra optimismo y los inversores aumentan posiciones.",
                    "market_impact_bearish": "El mercado muestra cautela y toma de beneficios.",
                    "market_impact_neutral": "El mercado se mantiene equilibrado a la espera de nuevos datos."
                },
                "french": {
                    "why_it_matters": "Cette évolution influe directement sur le pouvoir d'achat, les taux d'emprunt et l'épargne.",
                    "market_impact_bullish": "Les marchés affichent un net regain d'optimisme.",
                    "market_impact_bearish": "Prudence et repli sur les marchés financiers.",
                    "market_impact_neutral": "Marché équilibré en attendant les prochaines publications économiques."
                },
                "german": {
                    "why_it_matters": "Diese Entwicklung hat direkten Einfluss auf Kreditzinsen, Sparanlagen und persönliche Finanzen.",
                    "market_impact_bullish": "Die Stimmung an den Märkten ist optimistisch mit verstärkten Zuflüssen.",
                    "market_impact_bearish": "Verhaltener Handel und Risikoreduzierung an den Börsen.",
                    "market_impact_neutral": "Ausgeglichener Markt im Vorfeld weiterer Wirtschaftsdaten."
                }
            }
            tmpl = TEMPLATES.get(target_norm, {})
            if tmpl:
                updated["why_it_matters"] = tmpl.get("why_it_matters", updated.get("why_it_matters"))
                sent = updated.get("sentiment", "neutral")
                updated["market_impact"] = tmpl.get(f"market_impact_{sent}", tmpl.get("market_impact_neutral", updated.get("market_impact")))
                updated["key_takeaways"] = [
                    f"{updated['title'][:90]}...",
                    updated["why_it_matters"],
                    updated["market_impact"]
                ]
        except Exception as e:
            print(f"[TranslationService] dynamic translation error: {e}")

        return updated
