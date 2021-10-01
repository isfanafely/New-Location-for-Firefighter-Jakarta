import pandas as pd
import geopandas as gpd
import webbrowser
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import folium

fire = pd.read_csv('./latlongFire.csv')
pos = pd.read_csv('./latlongpos.csv')

latlong_fire = fire[['latitude', 'longitude']]
latlong_fire_filtered = latlong_fire[(latlong_fire.quantile(0.0001) < latlong_fire) &
                                     (latlong_fire < latlong_fire.quantile(0.9999))]
latlong_fire_filtered = latlong_fire_filtered.dropna(how='any')


ssd = []
sil = []
for i in range(2, 20):
    kmean = KMeans(n_clusters=i, random_state=0)
    y_kmean = kmean.fit(latlong_fire_filtered)
    sil.append(silhouette_score(latlong_fire_filtered, kmean.labels_))
    centers = kmean.cluster_centers_
    ssd.append(kmean.inertia_)

plt.figure(1)
plt.subplot(211)
plt.title('elbow')
plt.plot(range(2, 20), ssd)
plt.subplot(212)
plt.title('silhouette')
plt.plot(range(2, 20), sil)
plt.tight_layout()
plt.show()

k_cluster = 4
kmeans = KMeans(n_clusters=k_cluster).fit(latlong_fire_filtered)
latlong_fire_filtered['labels'] = kmeans.labels_
centers = kmeans.cluster_centers_

latlong_fire_filtered = latlong_fire_filtered.merge(fire)


stations = gpd.GeoDataFrame(pos, geometry=gpd.points_from_xy(pos.longitude, pos.latitude))
stations.crs = {'init': 'epsg:4326'}
stations = stations.to_crs(epsg=3857)

fire_new = gpd.GeoDataFrame(latlong_fire_filtered,
                                         geometry=gpd.points_from_xy(latlong_fire_filtered.longitude,
                                                                     latlong_fire_filtered.latitude))
fire_new.crs = {'init': 'epsg:4326'}
fire_new = fire_new.to_crs(epsg=3857)

coverage = stations.geometry.buffer(2000)
my_union = coverage.geometry.unary_union
outside_range = fire_new.loc[~fire_new['geometry'].apply(lambda x: my_union.contains(x))]

percentage = round(100*len(outside_range)/len(fire_new), 2)


def regioncolors(counter):
    if counter['labels'] == 0:
        return 'red'
    elif counter['labels'] == 1:
        return 'yellow'
    elif counter['labels'] == 2:
        return 'lightgreen'
    elif counter['labels'] == 3:
        return 'blue'
    else:
        return 'white'


latlong_fire_filtered['color'] = latlong_fire_filtered.apply(regioncolors, axis=1)


map_1 = folium.Map(location=[-6.240148, 106.880051],
                 tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', zoom_start=12,
                 attr='CartoDB.DarkMatter')

# for idx, row in stations.iterrows():
#     folium.Marker([row['latitude'], row['longitude']], popup=row.nama).add_to(map)

folium.GeoJson(coverage.to_crs(epsg=4326)).add_to(map_1)

for lat, lng, cluster, alamat, color in zip(latlong_fire_filtered['latitude'], latlong_fire_filtered['longitude'],
                                            latlong_fire_filtered['labels'], latlong_fire_filtered['alamat'],
                                            latlong_fire_filtered['color']):
    folium.CircleMarker(
        [lat, lng],
        radius=4,
        popup=alamat,
        color=color,
        fill=False).add_to(map_1)

title_html = f'''<h3 align="center" style="font-size:25px">
                        <b>{"Presentase Titik Api dengan jarak > 2km dari Pos Pemadam Kebakaran: {}%".format(percentage)}</b></h3>
                     '''
map_1.get_root().html.add_child(folium.Element(title_html))

folium.LatLngPopup().add_to(map_1)

filepath = './original_map.html'
m = map_1
m.save(filepath)
webbrowser.open(filepath)


Latitude_1 = -6.1546
Longitude_1 = 106.9553

Latitude_2 = -6.3303
Longitude_2 = 106.8287

Latitude_3 = -6.2225
Longitude_3 = 106.7191

new_df = pd.DataFrame(
        {'Latitude': [Latitude_1, Latitude_2, Latitude_3],
         'Longitude': [Longitude_1, Longitude_2, Longitude_3]})
new_gdf = gpd.GeoDataFrame(new_df, geometry=gpd.points_from_xy(new_df.Longitude, new_df.Latitude))
new_gdf.crs = {'init': 'epsg:4326'}
new_gdf = new_gdf.to_crs(epsg=3857)

new_coverage = gpd.GeoDataFrame(new_gdf, geometry=new_gdf.geometry).buffer(2000)
new_my_union = new_coverage.geometry.unary_union
new_outside_range = outside_range.loc[~outside_range['geometry'].apply(lambda x: new_my_union.contains(x))]
new_percentage = round(100*len(new_outside_range)/len(fire_new), 2)

map_2 = folium.Map(location=[-6.240148, 106.880051],
                 tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', zoom_start=12,
                 attr='CartoDB.DarkMatter')

for idx, row in new_gdf.to_crs(epsg=4326).iterrows():
    folium.Marker([row['Latitude'], row['Longitude']], icon=folium.Icon(color='white', icon_color='red',
                                                                        icon='fire-extinguisher',
                                                                        prefix='fa')).add_to(map_2)

folium.GeoJson(coverage.to_crs(epsg=4326)).add_to(map_2)
folium.GeoJson(new_coverage.to_crs(epsg=4326)).add_to(map_2)

for lat, lng, cluster, alamat, color in zip(latlong_fire_filtered['latitude'], latlong_fire_filtered['longitude'],
                                            latlong_fire_filtered['labels'], latlong_fire_filtered['alamat'],
                                            latlong_fire_filtered['color']):
    folium.CircleMarker(
        [lat, lng],
        radius=4,
        popup=alamat,
        color=color,
        fill=False).add_to(map_2)

title_html = f'''<h3 align="center" style="font-size:25px">
                        <b>{"Presentase Titik Api dengan jarak > 2km dari Pos Pemadam Kebakaran: {}%".format(new_percentage)}</b></h3>
                     '''
map_2.get_root().html.add_child(folium.Element(title_html))

folium.LatLngPopup().add_to(map_2)

filepath = './new_map.html'
m = map_2
m.save(filepath)
webbrowser.open(filepath)
