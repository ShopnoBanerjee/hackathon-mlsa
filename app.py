import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd
import geopandas as gpd
from folium import LinearColormap
import numpy as np
from folium.plugins import MarkerCluster
import scipy.stats as stats

# Streamlit app title
st.title("District Map with Survivors and Monsters")

# Define the API endpoints
api_url_resources = "https://api.mlsakiit.com/resources"
api_url_survivors = "https://api.mlsakiit.com/survivors"
api_url_monsters = "https://api.mlsakiit.com/monsters"

@st.cache_data
def fetch_data(url):
    """Fetch data from the API and return as JSON."""
    try:
        response = requests.get(url, headers={"accept": "application/json"})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from {url}: {e}")
        return None

@st.cache_data
def fetch_survivor_data():
    """Fetch survivor data from the API and return as a DataFrame."""
    data = fetch_data(api_url_survivors)
    if data:
        df_survivors = pd.DataFrame(data)
        return df_survivors
    return None

@st.cache_data
def fetch_monster_data():
    """Fetch monster data from the API and return as a DataFrame."""
    data = fetch_data(api_url_monsters)
    if data and "monsters" in data:
        df_monsters = pd.DataFrame(data["monsters"])
        return df_monsters
    return None

# Fetch district data
geojson_data = fetch_data(api_url_resources)
if not geojson_data:
    st.warning("No district data available.")
    st.stop()

# Fetch survivor data
df_survivors = fetch_survivor_data()

# Identify districts with survivor camps
if df_survivors is not None:
    districts_with_camps = df_survivors['district'].unique().tolist()
else:
    districts_with_camps = []

# Add 'camp_exists' property to each GeoJSON feature
for feature in geojson_data['features']:
    district_name = feature['properties']['dist_name']
    feature['properties']['camp_exists'] = district_name in districts_with_camps

# Read GeoJSON into Geopandas DataFrame
gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])

# Set initial CRS if not set
if gdf.crs is None:
    gdf = gdf.set_crs(epsg=4326)

# Reproject to an equal-area CRS for area calculation
gdf_area = gdf.to_crs(epsg=5070)

# Calculate area in square kilometers
gdf_area['area_sqkm'] = gdf_area['geometry'].area / 1e6

# Convert back to WGS84 for plotting
gdf_plot = gdf_area.to_crs(epsg=4326)

# Extract features into a Pandas DataFrame
df = pd.DataFrame(gdf_area.drop(columns=['geometry']))

# List of features to include
selected_features = ["water", "temp", "ammo", "medkits", "food_rations"]

# Convert selected features to numeric, coercing errors to NaN
for feature in selected_features:
    df[feature] = pd.to_numeric(df[feature], errors='coerce')

# Remove rows with NaN in any selected feature
df = df.dropna(subset=selected_features)

# Create feature selection dropdown
selected_feature = st.selectbox('Select a resource to display:', selected_features)

# Create color mapping based on selected feature
if selected_feature == 'temp':
    colormap = LinearColormap(['lightcoral', 'darkred'], 
                              vmin=df[selected_feature].min(), 
                              vmax=df[selected_feature].max())
elif selected_feature == 'ammo':
    colormap = LinearColormap(['#D7C7E3', '#5A2C6C'], 
                              vmin=df[selected_feature].min(), 
                              vmax=df[selected_feature].max())
elif selected_feature == 'water':
    colormap = LinearColormap(['lightblue', 'darkblue'], 
                              vmin=df[selected_feature].min(), 
                              vmax=df[selected_feature].max())
elif selected_feature in ['medkits', 'food_rations']:
    colormap = LinearColormap(['lightgreen', 'darkgreen'], 
                              vmin=df[selected_feature].min(), 
                              vmax=df[selected_feature].max())

# Define style function
def style_function(feature):
    value = feature['properties'].get(selected_feature, None)
    camp_exists = feature['properties'].get('camp_exists', False)
    if value is None:
        return {
            'fillColor': 'gray',
            'fillOpacity': 0.7,
            'color': 'black' if camp_exists else 'gray',
            'weight': 2 if camp_exists else 1
        }
    return {
        'fillColor': colormap(value),
        'fillOpacity': 0.7,
        'color': 'black' if camp_exists else 'gray',
        'weight': 2 if camp_exists else 1
    }

# Function to calculate bounds for a GeoDataFrame
def get_gdf_bounds(gdf):
    bounds = gdf.total_bounds  # [min_x, min_y, max_x, max_y]
    return [bounds[1], bounds[0], bounds[3], bounds[2]]  # [min_lat, min_lon, max_lat, max_lon]

# Function to calculate bounds for point data
def get_point_bounds(df):
    min_lat = df['lat'].min()
    max_lat = df['lat'].max()
    min_lon = df['lon'].min()
    max_lon = df['lon'].max()
    return [min_lat, min_lon, max_lat, max_lon]

# Calculate bounds for districts
district_bounds = get_gdf_bounds(gdf_plot)

# Initialize overall_bounds with district bounds
overall_bounds = district_bounds.copy()

# Update overall_bounds with survivor bounds if available
if df_survivors is not None:
    survivor_bounds = get_point_bounds(df_survivors)
    overall_bounds[0] = min(overall_bounds[0], survivor_bounds[0])
    overall_bounds[1] = min(overall_bounds[1], survivor_bounds[1])
    overall_bounds[2] = max(overall_bounds[2], survivor_bounds[2])
    overall_bounds[3] = max(overall_bounds[3], survivor_bounds[3])

# Fetch monster data
df_monsters = fetch_monster_data()

# Update overall_bounds with monster bounds if available
if df_monsters is not None:
    monster_bounds = get_point_bounds(df_monsters)
    overall_bounds[0] = min(overall_bounds[0], monster_bounds[0])
    overall_bounds[1] = min(overall_bounds[1], monster_bounds[1])
    overall_bounds[2] = max(overall_bounds[2], monster_bounds[2])
    overall_bounds[3] = max(overall_bounds[3], monster_bounds[3])

# Calculate map bounds for Folium
folium_bounds = [[overall_bounds[0], overall_bounds[1]], [overall_bounds[2], overall_bounds[3]]]

# Set map location to the center of overall bounds
center_lat = (overall_bounds[0] + overall_bounds[2]) / 2
center_lon = (overall_bounds[1] + overall_bounds[3]) / 2

# Create the Folium map
district_map = folium.Map(location=[center_lat, center_lon], zoom_start=8)

# Add GeoJSON layer with style function
folium.GeoJson(
    gdf_plot.to_json(),
    style_function=style_function,
    name='Districts'
).add_to(district_map)

# Add separate MarkerClusters for each district
if df_survivors is not None:
    for district in districts_with_camps:
        district_df = df_survivors[df_survivors['district'] == district]
        marker_cluster = MarkerCluster(name=district).add_to(district_map)
        for index, row in district_df.iterrows():
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=f"Survivor ID: {row['survivor_id']}<br>District: {row['district']}"
            ).add_to(marker_cluster)

# Add monster markers to the map
if df_monsters is not None:
    for index, row in df_monsters.iterrows():
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=row['monster_id']
        ).add_to(district_map)

# Add LayerControl to the map
district_map.add_child(folium.LayerControl())

# Add colormap to the map
colormap.add_to(district_map)

# Display the map in Streamlit
st.subheader("Interactive District Map with Survivor and Monster Markers")
st_folium(district_map, width=800, height=600)