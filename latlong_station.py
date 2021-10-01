import pandas as pd
import geopy

pos = pd.read_csv('./pos_pemadam.csv')
pos = pos.rename(columns={'keterangan':'nama'})
pos = pos.drop(['jumlah_kondisi_baik','jumlah_kondisi_rusak','luas_lahan','luas_bangunan'], axis=1)
pos['alamat'] = pos[['alamat','kelurahan','kecamatan','wilayah']].apply(lambda x: ', '.join(x), axis=1)
pos = pos.drop(pos.columns[[0,1,2]], axis=1)
pos = pos[['nama', 'alamat']]
geolocator = geopy.ArcGIS(user_agent="aws", timeout=None)
geocoder = geolocator.geocode
pos['location'] = pos['alamat'].apply(geocoder)
pos['latitude'] = [g.latitude for g in pos.location]
pos['longitude'] = [g.longitude for g in pos.location]
pos.dropna()
print(pos.shape)
pos.to_csv('latlongpos.csv')