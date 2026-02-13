import streamlit as st
import random
import requests
import re
import json
from urllib.parse import quote_plus

# --- Theme Data ---
STYLES = [
    # Pays
    "Française", "Italienne", "Espagnole", "Américaine", "Japonaise",
    "Coréenne", "Chinoise", "Marocaine", "Brésilienne", "Mexicaine",
    "Allemande", "Britannique", "Grecque", "Turque", "Indienne",
    "Thaïlandaise", "Suédoise", "Norvégienne", "Canadienne", "Australienne",

    # Vibes sociales / culturelles
    "Nouveau Riche", "Bourgeoise", "Catho Traditionnelle", "Punk",
    "Bobo Écolo", "Hipster", "Racaille Chic", "Influenceuse Instagram",
    "Start-up Nation", "Artiste Bohème", "Famille Nombreuse",
    "Geek / Gamer", "Retraités Riches", "Vieille Fortune",
    "Étudiante Fauchée", "Fitness / Gym Bro", "Luxury Minimaliste",
]

STYLES_EN = [
    # Countries
    "French", "Italian", "Spanish", "American", "Japanese",
    "Korean", "Chinese", "Moroccan", "Brazilian", "Mexican",
    "German", "British", "Greek", "Turkish", "Indian",
    "Thai", "Swedish", "Norwegian", "Canadian", "Australian",

    # Social / cultural vibes
    "Nouveau Riche", "Bourgeois", "Traditional Catholic", "Punk",
    "Eco Bobo", "Hipster", "Street Chic", "Instagram Influencer",
    "Startup Founder", "Bohemian Artist", "Large Family",
    "Geek Gamer", "Wealthy Retired", "Old Money",
    "Broke Student", "Fitness Lifestyle", "Luxury Minimalist",
]

BUILDING_TYPES_FR = [
    "Maison", "Villa", "Appartement", "Loft", "Manoir",
    "Penthouse", "Bungalow", "Studio", "Duplex",
]

BUILDING_TYPES_EN = [
    "House", "Villa", "Apartment", "Loft", "Mansion",
    "Penthouse", "Bungalow", "Studio", "Duplex",
]



def fetch_image_url(query: str) -> str | None:
    """Fetch a reference image URL from Google Images."""
    search_url = f"https://www.google.com/search?q={quote_plus(query)}&tbm=isch&safe=active"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }
    try:
        session = requests.Session()
        resp = session.get(search_url, headers=headers, timeout=10)
        resp.raise_for_status()
        text = resp.text

        # Method 1: Extract from AF_initDataCallback JSON blobs
        matches = re.findall(r'\["(https?://[^"]+)",[0-9]+,[0-9]+\]', text)
        for url in matches:
            if "gstatic" not in url and "google" not in url and "googleapis" not in url:
                return url

        # Method 2: Regex for image URLs
        urls = re.findall(r'https?://[^"\'\s\\]+\.(?:jpg|jpeg|png|webp)', text)
        for url in urls:
            if "gstatic" not in url and "google" not in url and "googleapis" not in url:
                return url

        # Method 3: Look for base64 encoded thumbnail data URIs as last resort
        thumbs = re.findall(r'(https?://encrypted-tbn0\.gstatic\.com/images\?[^"\'\\]+)', text)
        if thumbs:
            return thumbs[0].replace("\\u003d", "=").replace("\\u0026", "&")

    except Exception:
        pass
    return None


# --- Page Config ---
st.set_page_config(page_title="Sims 4 Défi Construction", page_icon="🏠", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&display=swap');

    .main-title {
        font-family: 'Fredoka', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #4CAF50, #2196F3, #9C27B0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .theme-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        text-align: center;
    }
    .theme-label {
        font-family: 'Fredoka', sans-serif;
        color: #aaa;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
    }
    .theme-text {
        font-family: 'Fredoka', sans-serif;
        color: #fff;
        font-size: 2.2rem;
        font-weight: 700;
    }
    .ref-title {
        font-family: 'Fredoka', sans-serif;
        color: #888;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 1.5rem 0 0.8rem 0;
        text-align: center;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #4CAF50, #2196F3) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 2rem !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        font-family: 'Fredoka', sans-serif !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏠 Sims 4 — Défi Construction</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Lance les dés et découvre ton prochain défi !</div>', unsafe_allow_html=True)

if st.button("🎲  Nouveau Thème !", use_container_width=True):
    idx_style = random.randrange(len(STYLES))
    idx_building = random.randrange(len(BUILDING_TYPES_FR))

    st.session_state["style_fr"] = STYLES[idx_style]
    st.session_state["style_en"] = STYLES_EN[idx_style]
    st.session_state["building_fr"] = BUILDING_TYPES_FR[idx_building]
    st.session_state["building_en"] = BUILDING_TYPES_EN[idx_building]

    # Fetch image immediately on button press so it's ready
    query = f"{STYLES_EN[idx_style]} {BUILDING_TYPES_EN[idx_building]} architecture exterior photo"
    st.session_state["image_url"] = fetch_image_url(query) or ""

if "style_fr" in st.session_state:
    theme_fr = f"{st.session_state['style_fr']} — {st.session_state['building_fr']}"

    st.markdown(
        f'<div class="theme-card">'
        f'<div class="theme-label">Ton Défi</div>'
        f'<div class="theme-text">{theme_fr}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    img_url = st.session_state.get("image_url", "")
    if img_url:
        st.markdown('<div class="ref-title">📸 Inspiration</div>', unsafe_allow_html=True)
        st.image(img_url, use_container_width=True)
    else:
        st.info("Impossible de trouver une image de référence — relance le dé !")
else:
    st.markdown(
        '<div style="text-align:center; color:#888; margin-top:3rem; font-size:1.1rem;">'
        "👆 Appuie sur le bouton pour découvrir ton thème !"
        "</div>",
        unsafe_allow_html=True,
    )