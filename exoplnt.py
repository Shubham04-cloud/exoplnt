import streamlit as st
import pandas as pd
import requests
import os

DATA_PATH = "exoplanets.csv"
API_KEY = "zcbUROJOQKFXPRiZPXfqsYWmhv1DRzJYMhf7wYxypython -m streamlit run exoatlas.py"  # <-- Put your NASA API key here!

def download_data():
    url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+*+from+ps&format=csv"
    if not os.path.exists(DATA_PATH):
        response = requests.get(url)
        if response.status_code == 200:
            with open(DATA_PATH, "wb") as f:
                f.write(response.content)
            st.success("✅ NASA Exoplanet data downloaded!")
        else:
            st.error("❌ Failed to download exoplanet data")
    else:
        st.info("📁 Data file found locally.")

def load_and_process_data():
    df = pd.read_csv(DATA_PATH)
    df = df[['pl_name', 'pl_rade', 'pl_eqt', 'st_teff', 'st_rad', 'sy_dist']].dropna()
    df.columns = ['Planet Name', 'Radius (Earth)', 'Temp (K)', 'Star Temp (K)', 'Star Radius', 'Distance (ly)']

    def habitability(row):
        if 0.5 <= row['Radius (Earth)'] <= 2.5 and 200 <= row['Temp (K)'] <= 350:
            return 'High 🌍'
        elif 150 <= row['Temp (K)'] <= 500:
            return 'Medium ☁️'
        else:
            return 'Low 🔥'

    df['Habitability'] = df.apply(habitability, axis=1)
    return df

def get_apod():
    url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("❌ Failed to fetch Astronomy Picture of the Day.")
        return None

def main():
    st.set_page_config(page_title="🪐 ExoAtlas - Exoplanet Explorer + APOD", layout="wide")
    st.title("🪐 ExoAtlas – AI-powered Exoplanet Explorer & NASA's Astronomy Picture of the Day")

    # --- NASA APOD Section ---
    with st.expander("🔭 Astronomy Picture of the Day"):
        apod_data = get_apod()
        if apod_data:
            st.subheader(apod_data.get("title", ""))
            st.write(f"*Date: {apod_data.get('date', '')}*")
            st.image(apod_data.get("url", ""), caption=apod_data.get("explanation", ""), use_column_width=True)
    
    # --- Exoplanet Explorer Section ---
    st.markdown("---")
    st.markdown("### Explore real NASA exoplanets and filter them based on size, temperature, and distance.")
    
    download_data()
    df = load_and_process_data()

    with st.sidebar:
        st.header("🔍 Filters")
        radius = st.slider("Planet Radius (Earth units)", 0.1, 10.0, (0.5, 2.5))
        distance = st.slider("Distance (light years)", 0.0, 5000.0, (0.0, 500.0))
        habitability = st.multiselect("Habitability", df["Habitability"].unique(), default=df["Habitability"].unique())

    filtered = df[
        (df["Radius (Earth)"] >= radius[0]) & (df["Radius (Earth)"] <= radius[1]) &
        (df["Distance (ly)"] >= distance[0]) & (df["Distance (ly)"] <= distance[1]) &
        (df["Habitability"].isin(habitability))
    ]

    st.metric("🌍 Planets Found", len(filtered))
    st.dataframe(filtered, use_container_width=True)

    if st.button("🎲 Surprise Me"):
        sample = filtered.sampl
