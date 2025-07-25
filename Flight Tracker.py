import requests
import folium
from folium.plugins import HeatMap, MarkerCluster

# 1. Fetch current flights from OpenSky
url = 'https://opensky-network.org/api/states/all'
resp = requests.get(url, timeout=10)
data = resp.json()

# 2. Parse out valid coordinates and marker info
coords = []
markers = []
for state in data.get('states', []):
    callsign = (state[1] or '').strip() or 'N/A'
    country  = state[2] or 'N/A'
    lat, lon = state[6], state[5]
    velocity = state[9] or 0
    if lat is None or lon is None:
        continue
    coords.append([lat, lon])
    popup = f"Callsign: {callsign}<br>Country: {country}<br>Speed: {velocity:.1f} m/s"
    markers.append((lat, lon, popup))

# 3. Create base map
m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB dark_matter')

# 4. Add clustered flight markers
mc = MarkerCluster(name='Live Flights').add_to(m)
for lat, lon, popup in markers:
    folium.Marker(
        location=[lat, lon],
        popup=popup,
        icon=folium.Icon(color='lightblue', icon='plane', prefix='fa')
    ).add_to(mc)

# 5. Add a flight-density heatmap
HeatMap(coords, name='Flight Density', radius=8, blur=15).add_to(m)

# 6. Layer control & save
folium.LayerControl().add_to(m)
m.save('flight_map.html')
print("Saved → flight_map.html")