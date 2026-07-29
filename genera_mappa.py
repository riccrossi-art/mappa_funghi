import folium
from folium.plugins import HeatMap
import requests

# ==========================================
# 1. IMPOSTA LA TUA PASSWORD QUI
# ==========================================
PASSWORD_SEGRETA = "Porcino2026!" 

# 2. Punti di monitoraggio tra Piemonte e Liguria
punti_monitoraggio = [
    {"nome": "Sassello (SV)", "lat": 44.478, "lon": 8.489},
    {"nome": "Calizzano (SV)", "lat": 44.235, "lon": 8.113},
    {"nome": "Santo Stefano d'Aveto (GE)", "lat": 44.547, "lon": 9.452},
    {"nome": "Torriglia (GE)", "lat": 44.520, "lon": 9.158},
    {"nome": "Chiusa di Pesio (CN)", "lat": 44.321, "lon": 7.676},
    {"nome": "Ormea (CN)", "lat": 44.148, "lon": 7.913},
    {"nome": "Acqui Terme (AL)", "lat": 44.675, "lon": 8.469},
    {"nome": "Varallo Sesia (VC)", "lat": 45.813, "lon": 8.258},
]

# 3. Funzione di calcolo
def calcola_indice(pioggia_mm, vento_kmh):
    if pioggia_mm < 20: f_p = 0.1
    elif 20 <= pioggia_mm < 60: f_p = (pioggia_mm - 20) / 40
    elif 60 <= pioggia_mm <= 120: f_p = 1.0
    else: f_p = max(0.1, 1.0 - (pioggia_mm - 120) / 120)

    if vento_kmh <= 8: f_v = 1.0
    elif 8 < vento_kmh <= 25: f_v = 1.0 - (vento_kmh - 8) / 25
    else: f_v = 0.1

    return round(f_p * f_v * 100, 1)

def get_colore(prob):
    if prob >= 75: return "green"
    elif prob >= 50: return "orange"
    else: return "red"

# 4. Creazione Mappa Base
m = folium.Map(location=[44.5, 8.2], zoom_start=8, tiles="OpenStreetMap")
heat_data = []

for punto in punti_monitoraggio:
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={punto['lat']}&longitude={punto['lon']}&daily=precipitation_sum,wind_speed_10m_max&past_days=7&forecast_days=1"
        res = requests.get(url, timeout=10).json()

        pioggia_cum = sum(res['daily']['precipitation_sum'])
        vento_max = max(res['daily']['wind_speed_10m_max'])

        probabilita = calcola_indice(pioggia_cum, vento_kmh=vento_max)
        heat_data.append([punto['lat'], punto['lon'], probabilita / 100])

        folium.CircleMarker(
            location=[punto['lat'], punto['lon']],
            radius=12,
            popup=f"<b>{punto['nome']}</b><br>"
                  f"Probabilità Funghi: <b>{probabilita}%</b><br>"
                  f"Pioggia 7gg: {round(pioggia_cum, 1)} mm<br>"
                  f"Vento Max: {round(vento_max, 1)} km/h",
            color=get_colore(probabilita),
            fill=True,
            fill_color=get_colore(probabilita),
            fill_opacity=0.7
        ).add_to(m)
    except Exception as e:
        print(f"Errore su {punto['nome']}: {e}")

HeatMap(heat_data, radius=35, blur=20, max_zoom=10).add_to(m)

# 5. Salva la mappa base
m.save("index.html")

# ==========================================
# 6. INIEZIONE DEL GATEWAY CON PASSWORD (JS)
# ==========================================
script_protezione = f"""
<script>
(function() {{
    const passwordCorretta = "{PASSWORD_SEGRETA}";
    let inserita = prompt("🔒 Questa mappa è privata.\\nInserisci la password di accesso:");
    
    if (inserita !== passwordCorretta) {{
        alert("❌ Password errata! Accesso negato.");
        document.body.innerHTML = "<div style='display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;background:#1a1a1a;color:white;'><h1>🔒 Accesso Negato</h1></div>";
    }}
}})();
</script>
"""

with open("index.html", "r", encoding="utf-8") as f:
    contenuto_html = f.read()

contenuto_protetto = contenuto_html.replace("</head>", f"{script_protezione}</head>")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(contenuto_protetto)

print("Mappa generata e protetta da password con successo!")
