# District Map with Survivors and Monsters

This is a Streamlit application that displays an interactive map of districts, showing the distribution of survivors and monsters, along with key resources in each district.

## Overview

The application fetches data from specified API endpoints to display:

- **District Boundaries**: Each district is displayed on the map with a color-coded fill based on the selected resource (e.g., water, ammo, etc.).
- **Survivor Camps**: Markers indicate the locations of survivor camps within each district.
- **Monster Locations**: Markers indicate the locations of monsters.
- **Key Metrics**: Displays the total number of survivors and monsters.

## Features

- **Interactive Map**: Zoom and pan to explore the districts.
- **Resource Visualization**: Choose a resource to visualize its distribution across districts.
- **Survivor and Monster Markers**: Clustered markers for survivors and individual markers for monsters.
- **Color Legend**: A colormap indicating the quantity of the selected resource in each district.
- **Layer Control**: Toggle the visibility of district boundaries, survivor camps, and monster markers.

## Live Demo

Check out the live deployment of the app here: [Survival Map](https://survival-map.streamlit.app/)

![image](https://github.com/user-attachments/assets/fed1ea84-4267-46e9-a65c-0d59dfe99809)

## Requirements

- Python 3.8 or higher
- Streamlit
- Requests
- Folium
- Geopandas
- Pandas
- NumPy
- SciPy

## Usage

1. **Deployed Version**: Access the app directly through the [Live Demo](https://survival-map.streamlit.app/) link.
2. **Local Version**: 
   - Ensure all requirements are installed.
   - Run the application using the following command:
     ```bash
     streamlit run app.py
     ```
   - Open the web browser and navigate to `http://localhost:8501` to view the application.

## API Endpoints

- **Resources (Districts)**: `https://api.mlsakiit.com/resources`
- **Survivors**: `https://api.mlsakiit.com/survivors`
- **Monsters**: `https://api.mlsakiit.com/monsters`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
