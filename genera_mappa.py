import folium
from folium.plugins import HeatMap
import requests

# ==========================================
# 1. IMPOSTA LA TUA PASSWORD QUI
# ==========================================
PASSWORD_SEGRETA = "Porcino2026!" 

# 2. Località predefinite (Piemonte e Liguria)
punti_predefiniti = [
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

for punto in punti_predefiniti:
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
# 6. PANNELLO LOGIN + GESTIONE LOCALITÀ (JS)
# ==========================================
interfaccia_completa = f"""
<!-- SCHERMATA LOGIN -->
<div id="loginOverlay" style="
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background-color: #1a1a1a; z-index: 999999; display: flex;
    flex-direction: column; justify-content: center; align-items: center;
    font-family: system-ui, -apple-system, sans-serif; color: white;">
    
    <div style="background: #2d2d2d; padding: 30px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); text-align: center; max-width: 320px; width: 80%;">
        <h2 style="margin-top:0;">🍄 Mappa Riservata</h2>
        <p style="color:#aaa; font-size: 14px;">Inserisci la password per sbloccare la mappa e gestire le tue località.</p>
        <input type="password" id="passInput" placeholder="Password" style="
            width: 100%; padding: 12px; margin: 15px 0; border-radius: 6px; border: 1px solid #444; background: #1a1a1a; color: white; box-sizing: border-box; font-size: 16px;">
        <button onclick="checkPass()" style="
            width: 100%; padding: 12px; background: #2e7d32; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 16px;">Sblocca Mappa</button>
        <p id="errorMsg" style="color: #ff5252; margin-top: 15px; display: none; font-size: 14px;">❌ Password errata!</p>
    </div>
</div>

<!-- PANNELLO DI CONTROLLO AGGIUNTA LOCALITÀ (In alto a destra sulla mappa) -->
<div id="controlPanel" style="
    position: fixed; top: 10px; right: 10px; z-index: 99999;
    background: rgba(30, 30, 30, 0.9); backdrop-filter: blur(5px);
    padding: 15px; border-radius: 8px; color: white;
    font-family: system-ui, -apple-system, sans-serif; max-width: 280px; box-shadow: 0 4px 15px rgba(0,0,0,0.4);">
    
    <h3 style="margin: 0 0 10px 0; font-size: 15px; display: flex; align-items: center; justify-content: space-between;">
        ➕ Aggiungi Località 
        <button onclick="caricaSalvate()" style="background:none; border:none; color:#4caf50; cursor:pointer; font-size:12px;">🔄 Aggiorna</button>
    </h3>
    <input type="text" id="nuovaLocalita" placeholder="Es. Bobbio Pellice" style="
        width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #555; background: #2a2a2a; color: white; box-sizing: border-box; font-size: 13px;">
    <button onclick="cercaE Salva()" style="
        width: 100%; margin-top: 8px; padding: 8px; background: #1976d2; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 13px;">Cerca e Salva</button>
    <p id="statusMsg" style="margin: 8px 0 0 0; font-size: 11px; color: #aaa;"></p>
    
    <hr style="border: 0; border-top: 1px solid #444; margin: 12px 0;">
    <p style="margin: 0; font-size: 12px; color: #bbb;">Le località aggiunte vengono salvate in automatico nel tuo browser.</p>
</div>

<script>
function checkPass() {{
    const pass = document.getElementById('passInput').value;
    if (pass === "{PASSWORD_SEGRETA}") {{
        document.getElementById('loginOverlay').style.display = 'none';
        caricaSalvate();
    }} else {{
        document.getElementById('errorMsg').style.display = 'block';
    }}
}}

document.getElementById('passInput').addEventListener('keypress', function (e) {{
    if (e.key === 'Enter') checkPass();
}});

// LOGICA CALCOLO INDICE LATO BROWSER
function calcolaIndiceJS(pioggia, vento) {{
    let fp = 0.1, fv = 0.1;
    if (pioggia < 20) fp = 0.1;
    else if (pioggia < 60) fp = (pioggia - 20) / 40;
    else if (pioggia <= 120) fp = 1.0;
    else fp = Math.max(0.1, 1.0 - (pioggia - 120) / 120);

    if (vento <= 8) fv = 1.0;
    else if (vento <= 25) fv = 1.0 - (vento - 8) / 25;
    else fv = 0.1;

    return (fp * fv * 100).toFixed(1);
}}

function getColoreJS(prob) {{
    if (prob >= 75) return "green";
    if (prob >= 50) return "orange";
    return "red";
}}

// CERCA, RILEVA METEO E SALVA IN LOCALSTORAGE
async function cercaESalva() {{
    const nome = document.getElementById('nuovaLocalita').value.trim();
    const status = document.getElementById('statusMsg');
    if (!nome) return;

    status.innerText = "🔍 Ricerca coordinate...";
    try {{
        // Geocoding via OpenStreetMap Nominatim
        const geoRes = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${{encodeURIComponent(nome)}},Italia`);
        const geoData = await geoRes.json();

        if (geoData.length === 0) {{
            status.innerText = "❌ Località non trovata.";
            return;
        }}

        const lat = parseFloat(geoData[0].lat);
        const lon = parseFloat(geoData[0].lon);
        const nomeCompleto = geoData[0].display_name.split(',')[0];

        status.innerText = "🌧️ Recupero dati meteo...";

        // Fetch Meteo
        const meteoRes = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${{lat}}&longitude=${{lon}}&daily=precipitation_sum,wind_speed_10m_max&past_days=7&forecast_days=1`);
        const meteoData = await meteoRes.json();

        const pioggia = meteoData.daily.precipitation_sum.reduce((a, b) => a + b, 0);
        const vento = Math.max(...meteoData.daily.wind_speed_10m_max);
        const prob = calcolaIndiceJS(pioggia, vento);

        // Salva in LocalStorage
        let salvate = JSON.parse(localStorage.getItem('funghi_punti') || '[]');
        salvate.push({{ nome: nomeCompleto, lat, lon, pioggia, vento, prob }});
        localStorage.setItem('funghi_punti', JSON.stringify(salvate));

        // Aggiungi marker alla mappa
        disegnaMarker(nomeCompleto, lat, lon, pioggia, vento, prob);

        status.innerText = `✅ Salvala: ${{nomeCompleto}} (${{prob}}%)`;
        document.getElementById('nuovaLocalita').value = '';
    }} catch (err) {{
        status.innerText = "❌ Errore nel recupero dati.";
        console.error(err);
    }}
}}

function disegnaMarker(nome, lat, lon, pioggia, vento, prob) {{
    // Trova l'oggetto mappa creato da Folium
    const mapObj = Object.values(window).find(val => val && val.addLayer && val.getCenter);
    if (mapObj) {{
        const color = getColoreJS(prob);
        const circle = L.circleMarker([lat, lon], {{
            radius: 12,
            color: color,
            fillColor: color,
            fillOpacity: 0.8
        }}).addTo(mapObj);

        circle.bindPopup(`<b>${{nome}} (Personalizzata)</b><br>Probabilità Funghi: <b>${{prob}}%</b><br>Pioggia 7gg: ${{pioggia.toFixed(1)}} mm<br>Vento Max: ${{vento.toFixed(1)}} km/h`);
        mapObj.setView([lat, lon], 9);
    }}
}}

function caricaSalvate() {{
    let salvate = JSON.parse(localStorage.getItem('funghi_punti') || '[]');
    salvate.forEach(p => {{
        disegnaMarker(p.nome, p.lat, p.lon, p.pioggia, p.vento, p.prob);
    }});
}}
</script>
"""

with open("index.html", "r", encoding="utf-8") as f:
    contenuto_html = f.read()

contenuto_protetto = contenuto_html.replace("<body>", f"<body>{interfaccia_completa}")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(contenuto_protetto)

print("Mappa aggiornata con ricerca e salvataggio località!")
