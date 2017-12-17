from __future__ import print_function

import pandas as pd, os, pdb

from .utils import fetch_lat_lon, fetch_census_loc

class MSAMapper:
    def __init__(self, source_df):
        self.source_df = source_df
        self.api_endpoint_for = {
            'censusreporter':{
                'geo': "https://api.censusreporter.org/1.0/geo/search?lat={lat}&lon={lon}&sumlevs={level}"
            }
        }
        self.value_of_level = {
            'census': {
                'msa': '310'
            }
        }

    def map_data(self, data_type='address'):
        if data_type == 'address':
            self.source_df = self._map_addr_to_latlng()
        return self._map_latlng_to_msa()

    def _map_latlng_to_msa(self, census_name='msa'):
        target_df = pd.DataFrame(columns=self.source_df.columns.tolist() \
                                        + [ 'MSA_NAME', 'MSA_CODE' ])
        url_template = self.api_endpoint_for['censusreporter']['geo']
        
        counter, census_level = 0, self.value_of_level['census'][census_name]

        #  convert all column name to uppercase to keep things consistent
        column_renamer = lambda x: x.upper() 
        self.source_df.rename(columns=column_renamer, inplace=True)

        for index, row in self.source_df.iterrows():
            #  pdb.set_trace()
            counter += 1
            print('Processed {} rows..'.format(counter), end='\r', )
            lat, lon = row[ ['LATITUDE', 'LONGITUDE'] ].tolist()
            query_url = url_template.format(lat=lat, lon=lon, level=census_level)
            census_data = fetch_census_loc(query_url)
            target_df.loc[counter] = row.tolist() + census_data
        return target_df
    
    def _map_addr_to_latlng(self):
        target_df = pd.DataFrame(columns=self.source_df.columns.tolist() + \
                                    ['LATITUDE', 'LONGITUDE', 'CONFIDENCE'])
        counter = 0
        for index, row in self.source_df.iterrows():
            #  pdb.set_trace()
            counter += 1
            print('Processed {} rows..'.format(counter), end='\r', )
            lat, lon, confidence = fetch_lat_lon(" ".join(row.tolist()))
            target_df.loc[counter] = row.tolist() + [ lat, lon, confidence ]
        return target_df
