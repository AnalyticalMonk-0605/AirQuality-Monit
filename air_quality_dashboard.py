import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# CONFIG
API_KEY = 'Enter your API KEY From OpenWeather'

# ------------------------------
# Function to fetch air quality data
def get_air_quality_data(lat, lon):
    url = f'http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}'
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None, None, f"API error: {response.status_code} - {response.text}"

        data = response.json()

        if "list" in data and len(data["list"]) > 0:
            components = data["list"][0]["components"]
            aqi = data["list"][0]["main"]["aqi"]
            return components, aqi, None
        else:
            return None, None, "No data found in API response."

    except Exception as e:
        return None, None, f"Exception occurred: {e}"

# Function to fetch weather data
def get_weather_data(lat, lon):
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}'
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None, None, f"API error: {response.status_code} - {response.text}"

        data = response.json()
        if 'main' in data:
            temp = data['main']['temp'] - 273.15  # Convert from Kelvin to Celsius
            description = data['weather'][0]['description']
            return temp, description, None
        else:
            return None, None, "No weather data found."
    except Exception as e:
        return None, None, f"Exception occurred: {e}"

# ------------------------------
# UI Setup
st.set_page_config(page_title="Real-Time Air Quality", layout="centered")
st.title("🌍 Real-Time Air Quality Dashboard")
st.markdown("Analyze real-time AQI and pollutant concentration by location")

# User Input
city_data = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Bangalore": (12.9716, 77.5946),
    "Thoothukudi": (8.7762, 78.2132)
}

city = st.selectbox("Choose a city", list(city_data.keys()))
lat, lon = city_data[city]

# Fetch air quality data
components, aqi, error = get_air_quality_data(lat, lon)

# Fetch weather data
temp, description, weather_error = get_weather_data(lat, lon)

# ------------------------------
# Display the Air Quality and Weather Data
if components:
    st.subheader(f"Air Quality in {city}")
    st.metric("AQI (1-Good to 5-Hazardous)", aqi)

    # Pollutants concentration bar chart
    df = pd.DataFrame({
        "Pollutant": list(components.keys()),
        "Concentration (μg/m³)": list(components.values())
    })

    fig = px.bar(df, x="Pollutant", y="Concentration (μg/m³)", color="Pollutant", title="Pollutant Levels")
    st.plotly_chart(fig)

    # AI-assisted text summary for air quality
    st.markdown("**Insight (Generated with AI help):**")
    if aqi == 1:
        st.success("Air quality is **Good**. Ideal for outdoor activities.")
    elif aqi == 2:
        st.info("Air quality is **Fair**. Still okay, but be cautious.")
    elif aqi == 3:
        st.warning("Air quality is **Moderate**. Sensitive groups should reduce outdoor activity.")
    elif aqi == 4:
        st.error("Air quality is **Poor**. Consider staying indoors.")
    elif aqi == 5:
        st.error("Air quality is **Very Poor**. Avoid outdoor exposure.")

    # Weather Information
    if temp is not None and description:
        st.subheader(f"Weather in {city}")
        st.write(f"Temperature: {temp:.1f}°C")
        st.write(f"Condition: {description.capitalize()}")

    # Map visualization of the selected city
    fig = px.scatter_mapbox(
        lat=[lat],
        lon=[lon],
        hover_name=[city],
        color=[city],
        title=f"Location: {city}",
        mapbox_style="carto-positron"
    )
    st.plotly_chart(fig)

elif error:
    st.error(f"❌ Couldn't fetch air quality data.\n\n**Reason:** {error}")
elif weather_error:
    st.error(f"❌ Couldn't fetch weather data.\n\n**Reason:** {weather_error}")
else:
    st.error("Unknown error occurred while fetching data.")
