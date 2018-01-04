import requests, geocoder

def fetch_census_loc(lat, lon, census_level, url_template):
    full_name, full_code = None, None
    
    #  check if both lat and lon coordinates are available for query
    if len(" ".join(map(str, [ lat, lon ])).split()) == 2:
        url = url_template.format(lat=lat, lon=lon, level=census_level)
        res = requests.get(url)
        payload = res.json()

        #  extract the MSA data if payload and response are valid
        if res.status_code == 200 and len(payload['results']) > 0:
            full_name = payload['results'][0]['full_name']
            full_code = payload['results'][0]['full_geoid'][-5:]

    return [ full_name, full_code ]

def fetch_lat_lon(query, retry_idx, retry_lim=50):
    lat, lon, confidence = None, None, None

    #  query geocoder only if query is valid
    if len(query.split()) > 0:
        #  remove excess whitespace
        query = " ".join(query.split())
        g = geocoder.bing(query)

        try:
            lat, lon = g.latlng
            confidence = g.json['raw']['confidence']
        except TypeError:
            print('Retrying for ', query)
            if retry_idx < retry_lim:
                lat, lon, confidence = fetch_lat_lon(query, retry_idx + 1)
        except Exception as e:
            print('Exception occurred when query address to latlng')
            pdb.set_trace()

    return lat, lon, confidence
