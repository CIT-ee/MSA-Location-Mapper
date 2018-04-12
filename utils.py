import requests, geocoder, pdb
from time import sleep

def fetch_census_loc(url, fields, layer_name):
    full_name, full_code = None, None
    
    res = requests.get(url, params=fields)

    #  extract the MSA data if payload and response are valid
    if res.status_code == 200:
        payload = res.json()
        census_data = payload['result']['geographies'][layer_name]
        full_name = census_data[0]['NAME'] if len(census_data) > 0 else full_name 
        full_code = census_data[0]['GEOID'] if len(census_data) > 0 else full_code
    elif res.status_code == 429:
        pdb.set_trace()
    else:
        print(res.status_code, url)

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
            print('Address: ', query)
            print('Exception: ', e)

    return lat, lon, confidence
