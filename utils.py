import requests, geocoder

def fetch_census_loc(url):
    full_name, full_code = None, None
    res = requests.get(url)
    payload = res.json()
    if res.status_code == 200 and len(payload['results']) > 0:
        full_name = payload['results'][0]['full_name']
        full_code = payload['results'][0]['full_geoid'][-5:]
    return [ full_name, full_code ]

def fetch_lat_lon(query):
    g = geocoder.bing(query)
    try:
        lat, lon = g.latlng
        confidence = g.json['raw']['confidence']
    except TypeError:
        print('Retrying for ', query)
        return fetch_lat_lon(query)
    return lat, lon, confidence
