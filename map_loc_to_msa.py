from __future__ import print_function

import pandas as pd, os, pdb

from .utils import fetch_lat_lon, fetch_census_loc

class MSAMapper:
    def __init__(self, source_df):
        self.source_df = source_df
        self.api_endpoint_for = {
            'census_geocoder': "https://geocoding.geo.census.gov/geocoder/{returntype}/{searchtype}"
        }
        self.layer_code = {
            'msa': ( ['NAME', 'GEOID'], '80' ),
            'tracts': ( ['', 'GEOID'], '8' )
        }

    def map_data(self, census_name, target_fields, data_type='address'):
        if data_type == 'address':
            self.source_df = self._map_addr_to_latlng().fillna('')
        return self._map_latlng_to_msa(census_name, target_fields)

    def _map_latlng_to_msa(self, census_name, target_fields):
        target_field_names = self.source_df.columns.tolist() + target_fields
        target_df = pd.DataFrame(columns=target_field_names)
        url_template = self.api_endpoint_for['census_geocoder']
        
        fields = { 'benchmark': 'Public_AR_Current', 'vintage': 'Current_Current', 'format': 'json' }
        nrows, fields['layers'] = self.source_df.shape[0], self.layer_code[census_name][1]

        #  find the lat-lon columns
        loc_fields = [ col_name for col_name in self.source_df.columns.tolist() \
                    if col_name.lower() in 'latitude' or col_name.lower() in 'longitude' ]

        print('\nConverting lat-lon coordinates to MSA data. Please wait ..')
        for _idx, (index, row) in enumerate(self.source_df.iterrows()):
            print('Processed {} out of {} rows..'.format(_idx, nrows), end='\r', )
            lat, lon = row[ sorted(loc_fields) ].tolist()
            url_query = url_template.format(returntype='geographies', searchtype='coordinates')
            fields['x'], fields['y'] = lon, lat
            census_data = fetch_census_loc(url_query, fields, self.layer_code[census_name][0])
            target_df.loc[_idx] = row.tolist() + census_data

        print('Converting lat-lon coordinates to MSA data completed!\n')
        return target_df.reset_index()
    
    def _map_addr_to_latlng(self):
        target_df = pd.DataFrame(columns=self.source_df.columns.tolist() + \
                                    ['LATITUDE', 'LONGITUDE', 'CONFIDENCE'])
        nrows, _ = self.source_df.shape
        print('\nConverting addresses to lat-lon coordinates. Please wait..')
        
        for _idx, (index, row) in enumerate(self.source_df.iterrows()):
            print('Processed {} out of {} rows..'.format(_idx, nrows), end='\r', )
            lat, lon, confidence = fetch_lat_lon(" ".join(row.tolist()), 0)
            target_df.loc[counter] = row.tolist() + [ lat, lon, confidence ]
        
        print('Converting addresses to lat-lon coordinates completed!\n')
        return target_df.reset_index()
