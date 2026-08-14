import json
import os
import urllib.parse
from datetime import datetime, date
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import requests

# Page Setup
st.set_page_config(
    page_title="BK Daily Quotes Generator",
    page_icon="🌸",
    layout="centered"
)

# Custom CSS for aesthetics
st.markdown("""
<style>
    .stDownloadButton button {
        border-radius: 8px;
        font-weight: bold;
    }
    .quote-box {
        background-color: #f8f9fa;
        border-left: 5px solid #6e0a50;
        padding: 15px;
        border-radius: 5px;
        font-size: 1.15rem;
        color: #333;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌸 BK Daily Quotes Generator")
st.write("ఆధ్యాత్మిక రోజువారీ శుభసందేశాల రాయల్ పోస్టర్ తయారీ వ్యవస్థ")

START_DATE = date(2026, 8, 15)

# Majestic Fonts Dictionary & URLs
FONTS_INFO = {
    "ramabhadra": {
        "name": "👑 రామభద్ర (Ramabhadra - గంభీరమైన బోల్డ్ లుక్)",
        "file": "Ramabhadra-Regular.ttf",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/ramabhadra/Ramabhadra-Regular.ttf",
        "default_size": 52,
        "line_gap": 26
    },
    "ramaraja": {
        "name": "📜 రామరాజ (Ramaraja - క్లాసికల్ గ్రంథ శైలి)",
        "file": "Ramaraja-Regular.ttf",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/ramaraja/Ramaraja-Regular.ttf",
        "default_size": 56,
        "line_gap": 28
    },
    "mandali": {
        "name": "🌸 మండలి (Mandali - క్లీన్ & సింపుల్)",
        "file": "Mandali-Regular.ttf",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/mandali/Mandali-Regular.ttf",
        "default_size": 54,
        "line_gap": 24
    }
}

def get_font_file(font_key):
    info = FONTS_INFO[font_key]
    file_path = info["file"]
    if not os.path.exists(file_path):
        try:
            res = requests.get(info["url"], timeout=10)
            if res.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(res.content)
        except Exception:
            pass
    return file_path

# Load Quotes
@st.cache_data
def load_quotes():
    if os.path.exists("quotes.json"):
        with open("quotes.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return ["సత్యము, ధర్మముల ఆచరణతోనే సర్వ శ్రేయస్సులను పొందగలము."]

quotes_list = load_quotes()

# Function to Wrap Text
def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        try:
            bbox = draw.textbbox((0, 0), test_line, font=font, layout_engine=ImageFont.Layout.RAQM)
        except Exception:
            bbox = draw.textbbox((0, 0), test_line, font=font)
            
        width = bbox[2] - bbox[0]
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines

# Majestic Poster Generator
def generate_poster(text, template_name, font_key, font_size_override=None):
    template_path = f"template_{template_name}.jpg"
    
    if not os.path.exists(template_path):
        st.error(f"❌ '{template_path}' ఫైల్ లభించలేదు. దయచేసి రిపోజిటరీలో అప్‌లోడ్ చేయండి.")
        return None

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    img_w, img_h = image.size

    font_cfg = FONTS_INFO[font_key]
    font_file = get_font_file(font_key)
    font_size = font_size_override if font_size_override else font_cfg["default_size"]

    try:
        font = ImageFont.truetype(font_file, font_size, layout_engine=ImageFont.Layout.RAQM)
    except Exception:
        font = ImageFont.truetype(font_file, font_size)

    max_width = int(img_w * 0.76)
    lines = wrap_text(text, font, max_width, draw)

    line_height = font_size + font_cfg["line_gap"]
    total_text_h = len(lines) * line_height
    start_y = (img_h - total_text_h) // 2

    # Majestic Styling Colors
    text_color = (110, 10, 80)     # Deep Royal Maroon
    glow_color = (255, 255, 255)   # Crisp White Outline for 3D pop
    shadow_color = (210, 180, 140) # Soft Gold Shadow

    for i, line in enumerate(lines):
        try:
            bbox = draw.textbbox((0, 0), line, font=font, layout_engine=ImageFont.Layout.RAQM)
            line_w = bbox[2] - bbox[0]
            x = (img_w - line_w) // 2
            y = start_y + (i * line_height)
            
            # Shadow
            draw.text((x + 2, y + 2), line, font=font, fill=shadow_color, layout_engine=ImageFont.Layout.RAQM)
            # Outline & Main Text
            draw.text((x, y), line, font=font, fill=text_color, stroke_width=1, stroke_fill=glow_color, layout_engine=ImageFont.Layout.RAQM)
        except Exception:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_w = bbox[2] - bbox[0]
            x = (img_w - line_w) // 2
            y = start_y + (i * line_height)
            draw.text((x, y), line, font=font, fill=text_color)

    output_path = f"output_{template_name}.jpg"
    image.save(output_path, quality=95)
    return output_path

# --- UI Controls ---
st.markdown("---")

mode = st.radio(
    "📌 మోడ్ ఎంచుకోండి:",
    ["📅 రోజువారీ వాక్యాలు (Daily Mode)", "✍️ నా స్వంత వాక్యం (Custom Mode)"],
    horizontal=True
)

current_quote = ""
display_title = ""

if mode == "📅 రోజువారీ వాక్యాలు (Daily Mode)":
    col1, col2 = st.columns(2)
    with col1:
        today_val = date.today() if date.today() >= START_DATE else START_DATE
        selected_date = st.date_input("📅 తేదీని ఎంచుకోండి:", value=today_val, min_value=START_DATE)
    with col2:
        selected_theme = st.selectbox(
            "🎨 ఫ్రేమ్ రంగును ఎంచుకోండి:",
            options=["pink", "green", "olive"],
            format_func=lambda x: "🌸 గులాబీ (Pink)" if x == "pink" else ("🍃 లేత ఆకుపచ్చ (Light Green)" if x == "green" else "🌿 ముదురు ఆకుపచ్చ (Olive Green)")
        )
    
    day_diff = (selected_date - START_DATE).days
    if day_diff < 0:
        st.warning("దయచేసి ఆగస్టు 15, 2026 లేదా తర్వాతి తేదీని ఎంచుకోండి.")
    elif day_diff >= len(quotes_list):
        st.info("ℹ️ ఎంచుకున్న తేదీకి సంబంధించిన వాక్యాలు త్వరలో అప్‌డేట్ చేయబడతాయి.")
    else:
        current_quote = quotes_list[day_diff]
        display_title = f"ఈరోజు వాక్యం ({selected_date.strftime('%d-%m-%Y')})"
else:
    col1, col2 = st.columns(2)
    with col1:
        custom_input = st.text_area(
            "✍️ మీ ఆధ్యాత్మిక వాక్యాన్ని ఇక్కడ టైప్ చేయండి:",
            value="సర్వ ప్రాణుల యందు దయ మరియు ప్రేమ కలిగి ఉండుటయే నిజమైన ఆధ్యాత్మికత.",
            height=100
        )
        current_quote = custom_input.strip()
        display_title = "మీ ఆధ్యాత్మిక సందేశం"
    with col2:
        selected_theme = st.selectbox(
            "🎨 ఫ్రేమ్ రంగును ఎంచుకోండి:",
            options=["pink", "green", "olive"],
            format_func=lambda x: "🌸 గులాబీ (Pink)" if x == "pink" else ("🍃 లేత ఆకుపచ్చ (Light Green)" if x == "green" else "🌿 ముదురు ఆకుపచ్చ (Olive Green)")
        )

# Typography & Adjustments
with st.expander("⚙️ అక్షరాల శైలి & సర్దుబాట్లు (Font & Size Settings)", expanded=False):
    selected_font = st.selectbox(
        "✍️ ఫాంట్ ఎంచుకోండి:",
        options=list(FONTS_INFO.keys()),
        format_func=lambda k: FONTS_INFO[k]["name"]
    )
    custom_size = st.slider(
        "🔤 అక్షరాల పరిమాణం (Font Size):",
        min_value=35,
        max_value=75,
        value=FONTS_INFO[selected_font]["default_size"],
        step=1
    )

if current_quote:
    st.markdown(f"### 💬 {display_title}:")
    st.markdown(f'<div class="quote-box">"{current_quote}"</div>', unsafe_allow_html=True)

    with st.spinner("🖼️ రాయల్ పోస్టర్ సిద్ధమవుతోంది..."):
        poster_file = generate_poster(current_quote, selected_theme, selected_font, custom_size)

    if poster_file and os.path.exists(poster_file):
        st.image(poster_file, caption="BK Spiritual Poster", use_container_width=True)

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            with open(poster_file, "rb") as file:
                st.download_button(
                    label=f"📥 Download Poster Image",
                    data=file,
                    file_name=f"BK_Quote_{selected_theme}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                    mime="image/jpeg",
                    type="primary",
                    use_container_width=True
                )
        with col_btn2:
            whatsapp_msg = f"✨ *ఓంశాంతి* ✨\n\n🌸 *ఈరోజు శుభసందేశం:*\n\"{current_quote}\"\n\n💐 *బ్రహ్మాకుమారీస్* | www.brahmakumaris.com"
            encoded_msg = urllib.parse.quote(whatsapp_msg)
            whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_msg}"
            st.markdown(
                f'<a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">'
                f'<button style="width: 100%; background-color: #25D366; color: white; border: none; padding: 10px; border-radius: 8px; font-weight: bold; cursor: pointer;">'
                f'📲 Share Text to WhatsApp'
                f'</button></a>',
                unsafe_allow_html=True
            )
