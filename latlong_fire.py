import pandas as pd
import glob
import geopy

list_of_names = ['januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli', 'agustus', 'september',
                 'oktober', 'november', 'desember']

all_files = glob.glob('./cases/*.csv')
fire = []
for filename in all_files:
    ls = pd.read_csv(filename, index_col=None, header=0, encoding='unicode_escape')
    fire.append(ls)

dataframe = pd.concat(fire, axis=0, ignore_index=True)
dataframe = dataframe.drop(dataframe.columns[[2,3,8,9,10,11]], axis=1)
dataframe = dataframe.dropna()
dataframe['alamat'] = dataframe[['alamat_kejadian','kelurahan','kecamatan','wilayah']].apply(lambda x: ', '.join(x), axis=1)
dataframe = dataframe.drop(dataframe.columns[[2,3,4,5]], axis=1)
fire = dataframe[dataframe['jenis_kejadian_bencana'] == 'Kebakaran']
print(fire.shape)
print(fire.head().to_string())

geolocator = geopy.ArcGIS(user_agent="aws", timeout=None)
geocoder = geolocator.geocode
fire['location'] = fire['alamat'].apply(geocoder)
fire['latitude'] = [g.latitude for g in fire.location]
fire['longitude'] = [g.longitude for g in fire.location]
fire.dropna()
print(fire.shape)
fire.to_csv('latlongFire.csv')
