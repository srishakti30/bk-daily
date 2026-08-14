import json
import os
from datetime import datetime
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import requests

# Page Setup
st.set_page_config(page_title="BK Daily Quotes Generator", page_icon="🌸", layout="centered")

st.title("🌸 BK Daily Quotes Generator")
st.write("ఆధ్యాత్మిక రోజువారీ శుభసందేశాల పోస్టర్ తయారీ వ్యవస్థ")

START_DATE = datetime(2026, 8, 15).date()

# Majestic Fonts Dictionary & URLs
FONTS_INFO = {
    "ramabhadra": {
        "name": "👑 రామభద్ర (Ramabhadra - గంభీరమైన బోల్డ్ లుక్)",
        "file": "Ramabhadra-Regular.ttf",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/ramabhadra/Ramabhadra-Regular.ttf",
        "size": 52,
        "line_gap": 26
    },
    "ramaraja": {
        "name": "📜 రామరాజ (Ramaraja - క్లాసికల్ గ్రంథ శైలి)",
        "file": "Ramaraja-Regular.ttf",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/ramaraja/Ramaraja-Regular.ttf",
        "size": 56,
        "line_gap": 28
    },
    "mandali": {
        "name": "🌸 మండలి (Mandali - క్లీన్ & సింపుల్)",
        "file": "Mandali-Regular.ttf",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/mandali/Mandali-Regular.ttf",
        "size": 54,
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

# Wrap Text Function
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
def generate_poster(text, template_name, font_key):
    template_path = f"template_{template_name}.jpg"
    
    if not os.path.exists(template_path):
        st.error(f"❌ '{template_path}' ఫైల్ లభించలేదు. దయచేసి అప్‌లోడ్ చేయండి.")
        return None

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    img_w, img_h = image.size

    font_cfg = FONTS_INFO[font_key]
    font_file = get_font_file(font_key)
    font_size = font_cfg["size"]

    try:
        font = ImageFont.truetype(font_file, font_size, layout_engine=ImageFont.Layout.RAQM)
    except Exception:
        font = ImageFont.truetype(font_file, font_size)

    max_width = int(img_w * 0.76)
    lines = wrap_text(text, font, max_width, draw)

    line_height = font_size + font_cfg["line_gap"]
    total_text_h = len(lines) * line_height
    start_y = (img_h - total_text_h) // 2

    # Majestic Rich Colors
    text_color = (110, 10, 80)     # Deep Royal Maroon/Magenta
    glow_color = (255, 255, 255)   # Crisp White Outline for pop
    shadow_color = (210, 180, 140) # Soft Gold/Tan Shadow

    for i, line in enumerate(lines):
        try:
            bbox = draw.textbbox((0, 0), line, font=font, layout_engine=ImageFont.Layout.RAQM)
            line_w = bbox[2] - bbox[0]
            x = (img_w - line_w) // 2
            y = start_y + (i * line_height)
            
            # Subtle Elegant Shadow
            draw.text((x + 2, y + 2), line, font=font, fill=shadow_color, layout_engine=ImageFont.Layout.RAQM)
            
            # Crisp Outline Stroke for 3D Pop
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

col1, col2 = st.columns(2)
with col1:
    selected_date = st.date_input("📅 తేదీని ఎంచుకోండి:", value=START_DATE, min_value=START_DATE)
with col2:
    selected_theme = st.selectbox(
        "🎨 ఫ్రేమ్ రంగును ఎంచుకోండి:",
        options=["pink", "green", "olive"],
        format_func=lambda x: "🌸 గులాబీ (Pink)" if x == "pink" else ("🍃 లేత ఆకుపచ్చ (Light Green)" if x == "green" else "🌿 ముదురు ఆకుపచ్చ (Olive Green)")
    )

selected_font = st.selectbox(
    "✍️ అక్షరాల శైలి (Font Style) ఎంచుకోండి:",
    options=list(FONTS_INFO.keys()),
    format_func=lambda k: FONTS_INFO[k]["name"]
)

day_diff = (selected_date - START_DATE).days

if day_diff < 0:
    st.warning("దయచేసి ఆగస్టు 15, 2026 లేదా తర్వాతి తేదీని ఎంచుకోండి.")
elif day_diff >= len(quotes_list):
    st.info("ℹ️ ఎంచుకున్న తేదీకి సంబంధించిన వాక్యాలు త్వరలో అప్‌డేట్ చేయబడతాయి.")
else:
    today_quote = quotes_list[day_diff]
    
    st.markdown(f"### 💬 ఈరోజు వాక్యం ({selected_date.strftime('%d-%m-%Y')}):")
    st.success(f"\"{today_quote}\"")

    with st.spinner("🖼️ గంభీరమైన పోస్టర్ సిద్ధమవుతోంది..."):
        poster_file = generate_poster(today_quote, selected_theme, selected_font)

    if poster_file and os.path.exists(poster_file):
        st.image(poster_file, caption=f"BK Daily Quote - {selected_date.strftime('%d-%m-%Y')}", use_container_width=True)

        with open(poster_file, "rb") as file:
            st.download_button(
                label=f"📥 Download {selected_theme.upper()} Poster Image",
                data=file,
                file_name=f"BK_Quote_{selected_theme}_{selected_date.strftime('%Y_%m_%d')}.jpg",
                mime="image/jpeg",
                type="primary",
                use_container_width=True
            )
