import argparse
import logging
import sys
import time
import requests
import folium
from folium.plugins import HeatMap, MarkerCluster

def fetch_flights(url, timeout=10, retries=3, backoff=2):
    for i in range(retries):
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logging.warning(f"Fetch attempt {i+1}/{retries} failed: {e}")
            time.sleep(backoff ** i)
    raise RuntimeError("Failed to fetch flight data after retries")

def parse_data(data):
    coords, markers = [], []
    for state in data.get('states', []):
        callsign = (state[1] or '').strip() or 'N/A'
        country  = state[2] or 'N/A'
        lat, lon  = state[6], state[5]
        speed     = state[9] or 0
        if lat is None or lon is None: continue
        coords.append([lat, lon])
        popup = f"Callsign: {callsign}<br>Country: {country}<br>Speed: {speed:.1f} m/s"
        markers.append((lat, lon, popup))
    return coords, markers

def create_map(coords, markers, output, tiles):
    m = folium.Map(location=[20,0], zoom_start=2, tiles=tiles)
    mc = MarkerCluster(name='Live Flights').add_to(m)
    for lat,lon,popup in markers:
        folium.Marker([lat,lon], popup=popup,
                      icon=folium.Icon(color='lightblue', icon='plane', prefix='fa')
                     ).add_to(mc)
    HeatMap(coords, name='Flight Density', radius=8, blur=15).add_to(m)
    folium.LayerControl().add_to(m)
    m.save(output)
    logging.info(f"Map saved to {output}")

def parse_args():
    p = argparse.ArgumentParser(description="Real-time flight tracker")
    p.add_argument('--url',
                   default='https://opensky-network.org/api/states/all')
    p.add_argument('--timeout', type=int, default=10)
    p.add_argument('--retries', type=int, default=3)
    p.add_argument('--tiles', default='CartoDB dark_matter')
    p.add_argument('--output', default='flight_map.html')
    return p.parse_args()

def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    args = parse_args()
    try:
        data   = fetch_flights(args.url, args.timeout, args.retries)
        coords, markers = parse_data(data)
        create_map(coords, markers, args.output, args.tiles)
    except Exception as e:
        logging.error(e)
        sys.exit(1)

if __name__=='__main__':
    main()