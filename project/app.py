import json
import re
from map import generate_map


import pandas as pd
import plotly.graph_objects as go
import pydeck as pdk
import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Melbourne CBD Parking & Transport Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%);
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 1rem 1rem;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    
    .main-subtitle {
        font-size: 1.25rem;
        color: #6b7280;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        text-align: center;
        margin: 1rem 0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .main-feature {
        background: linear-gradient(135deg, #f97316 0%, #dc2626 100%);
        color: white;
        padding: 3rem;
        margin: 2rem 0;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .main-feature:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 25px -5px rgba(255, 107, 53, 0.4);
    }
    
    .main-feature h3 {
        color: white !important;
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    .main-feature p {
        color: #fed7aa !important;
        font-size: 1.1rem;
    }
    
    .secondary-feature {
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .secondary-feature:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.15);
    }
    
    .secondary-feature h4 {
        color: #1f2937;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    
    .secondary-feature p {
        color: #6b7280;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    .section-header {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: white;
        border-radius: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .section-title {
        font-size: 2rem;
        font-weight: bold;
        color: #1f2937;
        margin-left: 1rem;
    }
    
    .insight-box {
        background: #f0f9ff;
        border: 1px solid #0ea5e9;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .insight-box-green {
        background: #f0fdf4;
        border: 1px solid #22c55e;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .insight-box-orange {
        background: #fff7ed;
        border: 1px solid #f97316;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .insight-box-purple {
        background: #faf5ff;
        border: 1px solid #a855f7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* Add visual hints for clickable cards */
    .clickable-card {
        position: relative;
        overflow: hidden;
    }
    
    .clickable-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .clickable-card:hover::before {
        left: 100%;
    }
</style>
""", unsafe_allow_html=True)


# Data preparation functions
@st.cache_data
def get_population_data(api_url="https://ldr1cwcs34.execute-api.ap-southeast-2.amazonaws.com/getPopulationGrowth"):
    """
    Obtain population data from the API and process it into data for the CBD area.
    """
    # Fetch data from Lambda/API Gateway
    response = requests.get(api_url)
    data = response.json()  # Should be a list of dicts

    # Convert to DataFrame
    population_growth = pd.DataFrame(data)

    # Filter only CBD data
    regions = ["Melbourne CBD - East", "Melbourne CBD - North", "Melbourne CBD - West"]
    population_growth_cbd = population_growth[population_growth["region"].isin(regions)]
    year_columns = [col for col in population_growth.columns if
                    col.isdigit() or (col.startswith("20") and col[2:].isdigit())]
    population_growth_cbd = population_growth_cbd.set_index("region").loc[regions, year_columns].T.astype(float)

    return population_growth_cbd, regions

# Route synchronization and clickable card functionality
def sync_page_from_query():
    """Sync page from URL query parameters to session state"""
    try:
        q = st.query_params.get("page", [None])[0]
        if q and q in ["home", "availability", "population", "environment"]:
            st.session_state.page = q
    except Exception:
        pass  # Fallback to session state if query params fail

# Initialize session state and sync with URL
if "page" not in st.session_state:
    st.session_state.page = "home"
sync_page_from_query()

# Clickable card CSS
st.markdown("""
<style>
    .click-card { 
        position: relative; 
        border-radius: 16px; 
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,.06); 
        transition: .2s ease;
        border: 1px solid rgba(0,0,0,.05); 
        cursor: pointer;
    }
    .click-card:hover { 
        transform: translateY(-2px);
        box-shadow: 0 14px 40px rgba(0,0,0,.08); 
    }
    .click-card a.stretched { 
        position: absolute; 
        inset: 0; 
        border-radius: inherit; 
        z-index: 10; 
        text-decoration: none; 
    }
    .click-card .icon { 
        font-size: 3.2rem; 
        margin-bottom: .75rem; 
    }
    .click-card h4 { 
        margin: .5rem 0 1rem; 
        font-weight: 700; 
    }
    .click-card p { 
        opacity: .85; 
        line-height: 1.6; 
        margin: 0; 
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_vehicle_data(api_url="https://ldr1cwcs34.execute-api.ap-southeast-2.amazonaws.com/getVehicleOwnership"):
    """
    Obtain the data on vehicle ownership in Victoria
    """
    # Fetch data from Lambda/API Gateway
    response = requests.get(api_url)
    data = response.json()  # Should be a list of dicts

    # Convert to DataFrame
    vehicle_ownership = pd.DataFrame(data)

    # Filter only Victoria data
    vic_data = vehicle_ownership[vehicle_ownership["state"] == "Vic."]

    # Get year columns
    years = [col for col in vehicle_ownership.columns if col.isdigit()]

    # Extract Victoria values
    vic_values = vic_data[years].values.flatten()

    return years, vic_values

@st.cache_data
def get_environmental_data(api_url="https://ldr1cwcs34.execute-api.ap-southeast-2.amazonaws.com/getCarbonEmission"):
    """
    Obtain carbon emission data
    """
    # Fetch data from Lambda/API Gateway
    response = requests.get(api_url)
    data = response.json()  # Should be a list of dicts

    # Convert to DataFrame
    carbon_emission = pd.DataFrame(data)

    # Sort by carbon_emission descending
    carbon_emission_sorted = carbon_emission.sort_values(by='carbon_emission', ascending=False).reset_index(drop=True)

    return carbon_emission_sorted

def get_locations():
    return ['Collins Street', 'Bourke Street', 'Flinders Street', 'Queen Street', 
            'Elizabeth Street', 'Swanston Street', 'Spencer Street', 'William Street']

def get_time_slots():
    return ['7:00 AM', '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
            '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM']


@st.cache_data
def get_streets_list():
    """
    obtain the list of streets
    """
    try:
        print("Fetching street list...")
        streets_response = requests.get("https://ldr1cwcs34.execute-api.ap-southeast-2.amazonaws.com/streets")
        print(f"Street API status code: {streets_response.status_code}")

        streets_list = []
        if streets_response.status_code == 200:
            streets_data = streets_response.json()
            print(f"Street API raw response: {streets_data}")
            print(f"Street data type: {type(streets_data)}")

            # ① Root-level on_street_list
            if isinstance(streets_data, dict) and 'on_street_list' in streets_data:
                raw_list = streets_data['on_street_list']
                # Clean data (remove line breaks and extra spaces)
                streets_list = [
                    ' '.join(s.replace('\r', ' ').replace('\n', ' ').split())
                    for s in raw_list if isinstance(s, str) and s.strip()
                ]
                print(f"Parsed from on_street_list, street count: {len(streets_list)}")

            # ② If body exists
            elif isinstance(streets_data, dict) and 'body' in streets_data:
                streets_body = streets_data['body']
                print(f"Street body content: {streets_body}")
                print(f"Street body type: {type(streets_body)}")
                try:
                    if isinstance(streets_body, str):
                        streets_list = json.loads(streets_body)
                    else:
                        streets_list = streets_body
                    print(f"Method 1 succeeded, street count: {len(streets_list)}")
                except Exception as e1:
                    print(f"Method 1 failed: {e1}")
                    try:
                        if isinstance(streets_body, str) and '"on street list"' in streets_body:
                            matches = re.findall(r'"([^"]*street[^"]*)"', streets_body, re.IGNORECASE)
                            streets_list = [match for match in matches if 'street' in match.lower()]
                            print(f"Method 2 succeeded, street count: {len(streets_list)}")
                    except Exception as e2:
                        print(f"Method 2 failed: {e2}")
                        print("Failed to parse street list")

            # ③ root is list
            elif isinstance(streets_data, list):
                streets_list = streets_data
                print(f"Directly parsed list, street count: {len(streets_list)}")

            # ④ root is result
            elif isinstance(streets_data, dict) and 'result' in streets_data:
                streets_list = streets_data['result']
                print(f"Parsed from result field, street count: {len(streets_list)}")

        else:
            print(f"Street API request failed: {streets_response.status_code} - {streets_response.text}")

        print(streets_list)
        return streets_list

    except Exception as e:
        print(f"Error occurred while retrieving the list of streets: {str(e)}")
        return []

def get_parking_zones_info(street_name):
    """
    Obtain the parking area information for the specified street
    """
    try:
        print(f"Fetching parking zones for {street_name}...")

        # Prepare request data
        request_data = {
            "on_street_list": [street_name]
        }

        zones_response = requests.post(
            "https://ldr1cwcs34.execute-api.ap-southeast-2.amazonaws.com/GetSignPlatesInfo",
            json=request_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        print(f"Zones API status code: {zones_response.status_code}")

        zones_df = pd.DataFrame()

        if zones_response.status_code == 200:
            zones_data = zones_response.json()
            print(f"Zones API response type: {type(zones_data)}")
            print(f"Zones API response content: {zones_data}")

            # Analyze parking area data
            if isinstance(zones_data, dict) and 'result' in zones_data:
                zones_df = pd.DataFrame(zones_data['result'])
                print(f"Number of rows in parking zones data: {len(zones_df)}")
                if not zones_df.empty:
                    print(f"Zone data columns: {zones_df.columns.tolist()}")
                    print("First 10 rows:")
                    df_display = zones_df.head(10).reset_index(drop=True)
                    df_display.index = df_display.index + 1
                    print(df_display)

                    print("\nData summary:")
                    if 'ParkingZone' in zones_df.columns:
                        print(f"Number of parking zones: {zones_df['ParkingZone'].nunique()}")
                    if 'Restriction_Display' in zones_df.columns:
                        print(f"Restriction type distribution:\n{zones_df['Restriction_Display'].value_counts()}")
                    if 'Restriction_Days' in zones_df.columns:
                        print(f"Restriction days distribution:\n{zones_df['Restriction_Days'].value_counts()}")
            else:
                print("Invalid Zones API response format")
        else:
            print(f"Zones API request failed: {zones_response.status_code} - {zones_response.text}")

        return zones_df

    except Exception as e:
        print(f"Error while fetching parking zones: {str(e)}")
        return pd.DataFrame()


def get_parking_status(street_name: str):
    """
    Obtain the parking status of the designated street.
    Returns:
        status_df: DataFrame with parking status info (no location column)
        zone_location_map: dict mapping zone_number -> (lat, lon, status)
    """
    try:
        resp = requests.post(
            "https://ldr1cwcs34.execute-api.ap-southeast-2.amazonaws.com/status",
            json={"on_street_list": [street_name]},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        if resp.status_code != 200:
            return pd.DataFrame(), {}

        data = resp.json()
        result = data.get("result", [])
        if not isinstance(result, list) or not result:
            return pd.DataFrame(), {}

        df = pd.DataFrame(result)

        # Standardize column names: lowercase, trim, spaces/hyphens -> underscore
        df.columns = (
            df.columns
              .str.strip()
              .str.lower()
              .str.replace(r"[ \-]+", "_", regex=True)
        )

        # Normalize key columns (align common aliases)
        rename_plan = {
            "kerbsideid": "kerbside_id",
            "zone_number": "zone_number",
            "zone number": "zone_number",
            "zonenumber": "zone_number",
            "zone": "zone_number",
            "status_description": "status",
            "status description": "status",
            "status": "status",
            "location": "location",
            "coordinates": "location",
            "coord": "location",
            "latlon": "location",
        }
        df = df.rename(columns={k: v for k, v in rename_plan.items() if k in df.columns})

        zone_col = "zone_number" if "zone_number" in df.columns else None
        loc_col  = "location"    if "location"    in df.columns else None
        stat_col = "status"      if "status"      in df.columns else None

        zone_location_map = {}
        if zone_col and loc_col:
            # Build zone_number -> (lat, lon, status)
            st_series = df[stat_col] if stat_col else pd.Series(["Unknown"] * len(df))
            for zn, loc, stt in zip(df[zone_col], df[loc_col], st_series):
                if pd.isna(zn) or pd.isna(loc):
                    continue
                # Support both English/Chinese commas
                parts = re.split(r"[，,]\s*", str(loc).strip(), maxsplit=1)
                if len(parts) != 2:
                    continue
                try:
                    lat, lon = float(parts[0]), float(parts[1])
                except ValueError:
                    continue
                zone_location_map[str(zn)] = (lat, lon, str(stt) if pd.notna(stt) else "Unknown")

            # Do not keep the 'location' column in the returned table
            if loc_col in df.columns:
                df = df.drop(columns=[loc_col])

        return df, zone_location_map

    except Exception:
        # On exception, keep the return contract
        return pd.DataFrame(), {}


# Navigation
def show_navigation():
    st.markdown("""
    <div style="background: white; padding: 1rem; margin: -1rem -1rem 2rem -1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2 style="color: #1f2937; margin: 0;">🚗 Melbourne CBD Dashboard</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Homepage
def show_homepage():
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">Melbourne CBD Transport & Parking Dashboard</h1>
        <p class="main-subtitle">Information on Available Parking in Melbourne CBD, Along with Commuting Details</p>
    </div>
    """, unsafe_allow_html=True)

    # Main Function - Parking Availability (Occupies Prominent Position)
    st.markdown("""
    <div class="click-card" style="background: linear-gradient(135deg,#ff9a56 0%,#ff6b35 100%); color:white; text-align:center; border:none; margin: 2rem 0;">
        <div class="icon">🅿️</div>
        <h4 style="font-size: 1.8rem;">Real-Time Parking Availability</h4>
        <p style="font-size: 1.3rem; margin-bottom: 2rem; opacity: 0.9;">
            Find available parking spaces across Melbourne CBD locations in real-time
        </p>
        <div style="
            background: rgba(255, 255, 255, 0.2);
            padding: 1rem 2rem;
            border-radius: 50px;
            display: inline-block;
            font-weight: bold;
            font-size: 1.1rem;
        ">
            📍 Click to access parking information
        </div>
        <a class="stretched" href="?page=availability" aria-label="Open availability"></a>
    </div>
    """, unsafe_allow_html=True)


    # Horizontal line
    st.markdown("<hr style='margin: 3rem 0; border: 1px solid #e5e7eb;'>", unsafe_allow_html=True)

    # Secondary Function Title
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h3 style="color: #374151; font-weight: 600; font-size: 1.5rem;">Additional Information Display</h3>
        <p style="color: #6b7280; font-size: 1rem;">Explore more insights about Melbourne transport patterns</p>
    </div>
    """, unsafe_allow_html=True)

    # Secondary Function - Balanced Layout
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="click-card" style="background:linear-gradient(135deg,#fef3e2 0%, #fed7aa 100%); color:#3a2a11; height: 280px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div class="icon">👥</div>
                <h4>Population & Vehicle Growth</h4>
                <p>Analyze population and vehicle registration trends affecting parking demand</p>
            </div>
            <a class="stretched" href="?page=population" aria-label="Open population"></a>
        </div>
        """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="click-card" style="background:linear-gradient(135deg,#f0fdf4 0%, #dcfce7 100%); color:#0e5132; height: 280px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div class="icon">🌱</div>
                    <h4>Environmental Impact</h4>
                    <p>Compare CO₂ emissions across transport methods and parking choices</p>
                </div>
                <a class="stretched" href="?page=environment" aria-label="Open environment"></a>
            </div>
            """, unsafe_allow_html=True)


def show_population_vehicle_section():
    """
    Display the chart showing population growth and vehicle ownership.
    """
    # back button
    if st.button("← Back to Home", key="back_to_home_population",
                 help="Return to main dashboard"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown("""
    <div class="section-header">
        <div style="font-size: 2rem;">👥</div>
        <h2 class="section-title">Population & Vehicle Growth Impact</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="metric-container">
        <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 1rem;">
            "Behind every car on the road is a story, someone late for a meeting, a parent on the school run, 
            a dreamer chasing a deadline," I explain. Over the years, Melbourne’s streets have seen more people, 
            more vehicles, and more pressure on space. Here is how our city has changed and what it might mean for tomorrow.
        </p>
    </div>
    """, unsafe_allow_html=True)

    try:
        # Obtain  data and display population growth
        population_growth_cbd, regions = get_population_data()

        # Get hex color codes for population chart
        set2_colors_population = ["#66c2a5", "#fc8d62", "#8da0cb"]

        # Create the population growth plot
        population_growth_plot = go.Figure()
        for i, region in enumerate(regions):
            # Plot
            population_growth_plot.add_trace(go.Scatter(
                x=population_growth_cbd.index,
                y=population_growth_cbd[region],
                mode='lines',
                stackgroup='one',
                name=region,
                line=dict(color=set2_colors_population[i])
            ))

        # Set y-axis to start at zero and go to the max value across all regions
        # For stacked area, y_max should be the max of the row-wise sum (total population per year)
        y_max = population_growth_cbd.sum(axis=1).max()

        population_growth_plot.update_layout(
            title=dict(
                text="Population Growth: Melbourne CBD Regions",
                x=0.5,
                xanchor="center"
            ),
            xaxis_title="Year",
            yaxis_title="Population",
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,  # Adjust as needed for spacing
                xanchor="center",
                x=0.5
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            yaxis=dict(range=[0, y_max])
        )

        st.plotly_chart(population_growth_plot, use_container_width=True)
        
        st.markdown("""
        <div class="insight-box">
            <strong>Our City, State, and Country&apos;s Population Trends</strong>
            <p>While the roads tell one story, Melbourne&apos;s population tells another. Between 2011 and 2021, Melbourne recorded the largest growth of any Australian capital. The city added 806,791 people. The centre of Victoria&apos;s population moved 1.2 km closer to the CBD, a clear sign that more people are choosing to live near the city&apos;s heart.</p>
            <p>The growth wasn&apos;t evenly spread across the CBD&apos;s three regions:</p>
            <ul>
                <li>East CBD: +28.5% growth</li>
                <li>West CBD: +116.4% growth (more than doubled)</li>
                <li>North CBD: +172.4% growth (nearly tripled)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        years, vic_values = get_vehicle_data()

        # Color for vehicle chart
        vehicle_color = "#e78ac3"

        # Create vehicle ownership plot
        vehicle_fig = go.Figure()
        vehicle_fig.add_trace(go.Scatter(
            x=years,
            y=vic_values,
            mode='lines+markers',
            name='Victoria Vehicle Ownership',
            line=dict(color=vehicle_color)
        ))

        vehicle_fig.update_layout(
            title=dict(
                text="Vehicle Ownership: Victoria",
                x=0.5,
                xanchor="center"
            ),
            xaxis_title="Year",
            yaxis_title="Vehicle Ownership",
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5
            ),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        st.plotly_chart(vehicle_fig, use_container_width=True)

        st.markdown("""
        <div class="insight-box">
            <strong>Our Vehicle Ownership Trends and Strategies</strong>
            <p>Not long ago, Victoria’s streets echoed with the steady rise of car ownership. The Motor Vehicle Census paints a more complex picture. 2018–2019: +4.5% growth. 2019–2020: +4.0%. 2020–2021: +3.5%. The slowdown arrived alongside the COVID-19 pandemic. This raises the question: is this a permanent shift in travel habits or just a temporary pause?</p>
            <p>The City of Melbourne is already preparing for change. Their Transport Strategy 2030 sets an ambitious direction. Public transport’s share of travel rose from 45% to 53% between 2001 and 2016. Private car use fell from 48% to 37%. By 2030, they aim to halve central city through-traffic compared to 2022. The plan involves massive investment in public transport expansion, walking-friendly streets, and cycling networks.</p>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.write("Please check the API connection and data format.")

    st.markdown("""
    <div class="metric-container">
        <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
            Together, these trends show a Melbourne in transformation.
            <ul>
                <li>Car growth is slowing, possibly signalling a shift toward sustainable travel</li>
                <li>Public transport, walking, and cycling are on the rise</li>
                <li>CBD population is surging, especially in the North and West</li>
                <li>Urban density is climbing fast, reshaping the way the city lives and moves</li>
                <li>Parking is becoming harder as more residents and commuters compete for fewer spaces, with some parking removed to make way for transport and pedestrian upgrades</li>
            </ul>
            For Melbourne commuters, these insights reveal why finding parking is increasingly difficult in the CBD and how population and transport trends are shaping congestion. This knowledge can help individuals adapt travel habits, plan trips more efficiently, and anticipate the future of urban mobility.
        </p>
    </div>
    """, unsafe_allow_html=True)


# Environmental Impact Section
def show_environment_section():
    """
    Display the environmental impact chart
    """
    # Back button - Fixed at the top
    with st.container():
        if st.button("← Back to Home", key="back_to_home_environment",
                     help="Return to main dashboard"):
            st.session_state.page = "home"
            st.rerun()

    st.markdown("""
    <div class="section-header">
        <div style="font-size: 2rem;">🌱</div>
        <h2 class="section-title">Environmental Impact Analysis</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="metric-container">
        <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
            "Every journey leaves a mark, but some marks fade faster than others," I remind you. 
            From solo car rides to shared trips, trains, bikes, and walking, each choice tells a different environmental story. 
            Let us see which ones are the quiet heroes of Melbourne’s air quality.
        </p>
    </div>
    """, unsafe_allow_html=True)

    try:
        # Obtain environmental data
        carbon_emission_sorted = get_environmental_data()

        # Color scheme for carbon emission chart
        set2_colors = ["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854", "#ffd92f", "#e5c494", "#b3b3b3"]

        # Create carbon emission bar chart
        carbon_emission_plot = go.Figure(
            go.Bar(
                x=carbon_emission_sorted['transport'],
                y=carbon_emission_sorted['carbon_emission'],
                marker_color=set2_colors[:len(carbon_emission_sorted)],
                text=[str(int(round(val))) for val in carbon_emission_sorted['carbon_emission']],
                textposition='outside'
            )
        )

        carbon_emission_plot.update_layout(
            title=dict(
                text="Average Individual Carbon Emission by Transport Type (Kg/Month)",
                x=0.5,
                xanchor="center"
            ),
            xaxis_title="Transport Type",
            yaxis_title="Carbon Emission (Kg/Month)",
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        # Modify the toolbar
        config = {
            'displayModeBar': True,
            'modeBarButtonsToRemove': ['resetScale2d', 'resetViewMapbox'],
            'displaylogo': False
        }

        st.plotly_chart(carbon_emission_plot, use_container_width=True, config=config)

    except Exception as e:
        st.error(f"Error loading environmental data: {str(e)}")
        st.write("Please check the API connection and data format.")

    st.markdown("""
    <div class="insight-box">
        <strong>My Carbon Footprint:</strong> 
        <p>Your mode of travel has a direct impact on your carbon emissions. The difference between options is striking:</p>
        <ul>
            <li>Petrol vehicles: ~3,750 kg CO₂/month (highest emissions)</li>
            <li>Diesel/LPG vehicles: Above 3,000 kg CO₂/month</li>
            <li>Hybrid vehicles: ~2,708 kg CO₂/month</li>
            <li>Electric vehicles: ~1,800–2,000 kg CO₂/month</li>
            <li>Public transport: Similar low range of ~1,800–2,000 kg CO₂/month</li>
            <li>Cycling or walking: Lowest emissions, almost negligible compared to motor vehicles</li>
        </ul>
        <br>
        <strong>What this means: </strong> Choosing public transport, cycling, walking, or electric vehicles can cut your monthly carbon footprint by over 40% compared to hybrid cars, and by more than 50% compared to petrol vehicles.
        <br>
        <br>
        <strong>Why This Matters for You as a Commuter</strong>
        <ul>
            <li>Clear environmental impact: You can see exactly how your travel choice translates into CO₂ emissions saved each month.</li>
            <li>Informed, greener decisions: Switching from a petrol car to public transport could save roughly 1,900 kg of CO₂ every month.</li>
            <li>Collective benefit: If thousands of commuters made the same shift, Melbourne’s air quality would improve dramatically.</li>
            <li>Personal contribution to a sustainable future: Every trip you make using low-emission transport supports the city’s climate goals.</li>
        </ul>
    </div> 
    """, unsafe_allow_html=True)

# Parking Availability Section
def show_availability_section():
    """
    Display parking space availability information
    """
    # Back button - Fixed at the top
    with st.container():
        if st.button("← Back to Home", key="availability_back",
                     help="Return to main dashboard"):
            st.session_state.page = "home"
            st.rerun()

    st.markdown("""
    <div class="section-header">
        <div style="font-size: 2rem;">🅿️</div>
        <h2 class="section-title">Parking Space Availability</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="metric-container">
        <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
            Select a street to view detailed parking zone information and current space availability.
        </p>
    </div>
    """, unsafe_allow_html=True)

    try:
        # Directly obtain the list of streets (list)
        streets_list = get_streets_list()

        # Debug print
        st.write(f"Number of streets: {len(streets_list)}")
        #st.write("Sample streets:", streets_list[1:10])

        if not streets_list:
            st.warning("Unable to obtain street list data")
            return

        # Search box (case-insensitive)
        search_input = st.text_input("🔍 Enter street name to search", key="availability_search")
        filtered_streets = []
        if search_input.strip():
            filtered_streets = [s for s in streets_list if search_input.lower() in s.lower()]

        # If there are search results, display selection box
        selected_street = None
        if filtered_streets:
            selected_street = st.selectbox("Please select a street", filtered_streets, key="availability_street")

        # —— Select and confirm street ——
        if "confirmed_street" not in st.session_state:
            st.session_state.confirmed_street = None

        # selected_street comes from the selectbox above
        if selected_street:
            # Confirm button
            if st.button("✅ Confirm this street", key="confirm_street"):
                st.session_state.confirmed_street = selected_street
                st.rerun()  # Newer Streamlit

        confirmed_street = st.session_state.confirmed_street

        # —— Only call the APIs after confirmation ——
        if confirmed_street:
            st.markdown(f"""
                <div class="metric-container">
                    <h3 style="color: #1f2937; margin-bottom: 1rem;">
                        Parking Information for: {confirmed_street}
                    </h3>
                </div>
                """, unsafe_allow_html=True)

            # Parking zone information
            zones_df = get_parking_zones_info(confirmed_street)
            if zones_df is not None and not zones_df.empty:
                st.subheader("Parking Zone Restrictions")
                try:
                    zones_display = zones_df[['Parkingzone', 'Restriction Days', 'Time Restrictions start',
                                              'Time Restrictions Finish', 'Restriction Display']].copy()
                    st.dataframe(zones_display, use_container_width=True)
                except KeyError:
                    st.dataframe(zones_df, use_container_width=True)
                
                # legend
                left, right = st.columns([2,1], gap="large")

                with right :
                    st.markdown("""
                    <div style="
                        background: rgba(248, 250, 252, 0.9);
                        border: 1px solid rgba(203, 213, 225, 0.6);
                        border-radius: 8px;
                        padding: 1rem;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                        margin-bottom: 1rem;">
                        <h4 style="text-align: center; margin-bottom: 1rem; color: #374151;">🚗 Zone Types</h4>
                        <div style="justify-content: center;">
                            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                                <div style="
                                    background: linear-gradient(135deg,rgb(152, 223, 178),rgb(99, 163, 124));
                                    color: white;
                                    border-radius: 8px;
                                    padding: 0.4rem 0.6rem;
                                    font-weight: bold;
                                    font-size: 0.8rem;
                                    min-width: 50px;
                                    text-align: center;
                                    box-shadow: 0 2px 4px rgba(34, 197, 94, 0.3);">FP1P</div>
                                <span style="margin-left: 0.75rem; font-size: 0.85rem; color: #374151;">Free Parking 1 hour</span>
                            </div>
                            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                                <div style="
                                    background: linear-gradient(135deg,rgb(236, 210, 165),rgb(198, 162, 120));
                                    color: white;
                                    border-radius: 8px;
                                    padding: 0.4rem 0.6rem;
                                    font-weight: bold;
                                    font-size: 0.8rem;
                                    min-width: 50px;
                                    text-align: center;
                                    box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);">MP2P</div>
                                <span style="margin-left: 0.75rem; font-size: 0.85rem; color: #374151;">Meter Parking 2 hours limit</span>
                            </div>
                            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                                <div style="
                                    background: linear-gradient(135deg,rgb(163, 186, 223),rgb(112, 140, 200));
                                    color: white;
                                    border-radius: 8px;
                                    padding: 0.4rem 0.6rem;
                                    font-weight: bold;
                                    font-size: 0.8rem;
                                    min-width: 50px;
                                    text-align: center;
                                    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);">LZ30</div>
                                <span style="margin-left: 0.75rem; font-size: 0.85rem; color: #374151;">Loading Zone 30 minutes limit</span>
                            </div>
                            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                                <div style="
                                    background: linear-gradient(135deg,rgb(208, 187, 228),rgb(179, 145, 211));
                                    color: white;
                                    border-radius: 8px;
                                    padding: 0.4rem 0.6rem;
                                    font-weight: bold;
                                    font-size: 0.8rem;
                                    min-width: 50px;
                                    text-align: center;
                                    box-shadow: 0 2px 4px rgba(168, 85, 247, 0.3);">QP</div>
                                <span style="margin-left: 0.75rem; font-size: 0.85rem; color: #374151;">Quarter Parking (15 minutes)</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning(f"Unable to obtain parking zone restriction data for {confirmed_street}")

            # Parking status information
            status_df, zone_location_map = get_parking_status(confirmed_street)

            if status_df is not None and not status_df.empty:
                st.subheader("Current Parking Space Status")


                if 'Status_Description' in status_df.columns:
                    status_summary = status_df['Status_Description'].value_counts().reset_index()
                    status_summary.columns = ['Status', 'Count']

                    color_map = {'Unoccupied': '#22c55e', 'Occupied': '#ef4444', 'Out of Order': '#f59e0b'}
                    status_summary['Color'] = status_summary['Status'].map(lambda x: color_map.get(x, '#6b7280'))

                    col1, col2 = st.columns(2)
                    with col1:
                        st.dataframe(status_summary[['Status', 'Count']], use_container_width=True)
                    with col2:
                        fig = go.Figure(data=[go.Pie(
                            labels=status_summary['Status'],
                            values=status_summary['Count'],
                            marker_colors=status_summary['Color'],
                            hole=0.4,
                            textinfo='label+percent+value',
                            textposition='outside'
                        )])
                        fig.update_layout(
                            title="Overall Parking Status Distribution",
                            height=400, showlegend=True,
                            plot_bgcolor='white', paper_bgcolor='white'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    #  parking_zones info display
                    if 'Parkingzone' in zones_df.columns:
                        available_zones = zones_df['Parkingzone'].unique().tolist()
                        st.subheader("Available Parking Zones")
                        if available_zones:
                            zones_text = ", ".join(available_zones)
                            st.markdown(f"""
                                <div style="background-color: #f0f9ff; padding: 1rem; border-radius: 8px; border-left: 4px solid #3b82f6;">
                                    <strong>Active Zones:</strong> {zones_text}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No active parking zones found")
                else:
                    st.dataframe(status_df, use_container_width=True)

                #  zone_location_map for map visulization
                if zone_location_map:
                    st.subheader("Parking Zones Map")
                    try:
                        generate_map(status_df, zone_location_map)
                    except Exception as e:
                        st.warning(f"Map rendering failed: {e}")
            else:
                st.warning(f"Unable to obtain parking space status data for {confirmed_street}")
        else:
            st.info("Please select a street and click 'Confirm this street' first.")

    except Exception as e:
        st.error(f"An error occurred while retrieving parking information: {str(e)}")
        st.write("Please check the data connection and function implementation")

    except Exception as e:
        st.error(f"Error occurred while obtaining parking information.: {str(e)}")
        st.write("Check the data connection and function implementation")

    st.markdown("""
    <div class="insight-box">
        <strong>Parking Insight:</strong> Parking availability data helps optimize parking space utilization 
        and reduces traffic congestion caused by drivers searching for parking spots.
    </div>
    """, unsafe_allow_html=True)



# Main application logic
def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    # Navigation buttons in sidebar
    with st.sidebar:
        st.markdown("### Navigation")
        
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()
        
        if st.button("🅿️ Availability", use_container_width=True):
            st.session_state.page = 'availability'
            st.rerun()
            
        if st.button("👥 Population/Vehicle", use_container_width=True):
            st.session_state.page = 'population'
            st.rerun()
            
        if st.button("🌱 Emission", use_container_width=True):
            st.session_state.page = 'environment'
            st.rerun()
            

    # Show navigation bar
    if st.session_state.page != 'home':
        show_navigation()
    
    # Show appropriate page
    if st.session_state.page == 'home':
        show_homepage()
    elif st.session_state.page == 'population':
        show_population_vehicle_section()
    elif st.session_state.page == 'environment':
        show_environment_section()
    elif st.session_state.page == 'availability':
        show_availability_section()


if __name__ == "__main__":
    main()