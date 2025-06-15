import subprocess
import pandas as pd
import os

api_command = 'curl --form x=@longitude --form y=@latitude --form benchmark=2020 --form vintage=2010 https://geocoding.geo.census.gov/geocoder/geographies/coordinates --output @output'
out_dir = 'raw_api_output'
us_airports = pd.read_csv('../src_data/large_airports.csv')
us_airports = us_airports[us_airports['iso_country'] == 'US'].reset_index(drop=True)

if not os.path.exists(out_dir):
    os.mkdir(out_dir)

print(len(us_airports))

for i in range(len(us_airports)):
    airport = us_airports.iloc[i]
    code = airport['iata_code']
    region = airport['region']

    query_command = api_command.replace('@longitude',str(airport['longitude'])).replace('@latitude',str(airport['latitude']))
    query_command = query_command.replace('@output', '%s/%s_%s.json'%(out_dir, region, code))
    query_command = query_command.split(' ')

    subprocess.call(query_command)
    print('%d: %s done'%(i, code))

