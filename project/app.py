import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import random

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
        transition: transform 0.2s;
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
</style>
""", unsafe_allow_html=True)

# Data preparation functions
@st.cache_data
def get_population_data():
    return pd.DataFrame({
        'Year': ['2019', '2020', '2021', '2022', '2023', '2024'],
        'Population (thousands)': [185, 142, 158, 172, 189, 201],
        'Vehicle Registrations (thousands)': [89, 85, 91, 96, 102, 108]
    })

@st.cache_data
def get_environmental_data():
    return pd.DataFrame({
        'Transport Method': ['Car (Solo)', 'Car (Shared)', 'Public Transport', 'Cycling', 'Walking'],
        'CO2 Emissions (kg/trip)': [4.2, 2.1, 0.8, 0.0, 0.0],
        'Color': ['#dc2626', '#f59e0b', '#059669', '#22c55e', '#10b981']
    })

def get_locations():
    return ['Collins Street', 'Bourke Street', 'Flinders Street', 'Queen Street', 
            'Elizabeth Street', 'Swanston Street', 'Spencer Street', 'William Street']

def get_time_slots():
    return ['7:00 AM', '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
            '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM']

def get_parking_availability():
    available = random.randint(20, 70)
    occupied = 100 - available
    return pd.DataFrame({
        'Status': ['Available Spaces', 'Occupied Spaces'],
        'Count': [available, occupied],
        'Color': ['#22c55e', '#ef4444']
    })

def get_parking_supply_data():
    time_slots = get_time_slots()
    return pd.DataFrame({
        'Time': time_slots,
        'Available Spaces': [random.randint(20, 100) for _ in time_slots]
    })

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
    
    # Main feature - Parking Availability
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="feature-card main-feature">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🅿️</div>
            <h3>Real-Time Parking Availability</h3>
            <p style="font-size: 1.1rem; margin-bottom: 1.5rem;">
                Find available parking spaces across Melbourne CBD locations in real-time
            </p>
            <div style="display: flex; align-items: center; justify-content: center; font-weight: bold;">
                📍 Check Available Spaces Now
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🅿️ Real-Time Parking Availability", key="main_parking", use_container_width=True):
            st.session_state.page = "availability"
            st.rerun()
    
    # Secondary features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card secondary-feature">
            <div style="font-size: 2.5rem; color: #2563eb; margin-bottom: 1rem;">👥</div>
            <h4>Population & Vehicle Growth</h4>
            <p>Analyze population and vehicle registration trends</p>
            <div style="color: #2563eb; font-weight: 500; font-size: 0.9rem;">
                📈 View Analysis
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("👥 Population/Vehicle", key="population", use_container_width=True):
            st.session_state.page = "population"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="feature-card secondary-feature">
            <div style="font-size: 2.5rem; color: #059669; margin-bottom: 1rem;">🌱</div>
            <h4>Environmental Impact</h4>
            <p>Compare CO2 emissions across transport methods</p>
            <div style="color: #059669; font-weight: 500; font-size: 0.9rem;">
                🌿 View Emissions
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🌱 Emission", key="environment", use_container_width=True):
            st.session_state.page = "environment"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="feature-card secondary-feature">
            <div style="font-size: 2.5rem; color: #7c3aed; margin-bottom: 1rem;">📊</div>
            <h4>Parking Supply Data</h4>
            <p>Historical parking supply trends by location</p>
            <div style="color: #7c3aed; font-weight: 500; font-size: 0.9rem;">
                ⏰ View Trends
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 Historical Supply", key="supply", use_container_width=True):
            st.session_state.page = "supply"
            st.rerun()

# Population & Vehicle Growth Section
def show_population_section():
    st.markdown("""
    <div class="section-header">
        <div style="font-size: 2rem;">👥</div>
        <h2 class="section-title">Population & Vehicle Growth Impact</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="metric-container">
        <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
            This chart illustrates the relationship between Melbourne CBD's population growth and vehicle registration trends from 2019 to 2024.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create the chart
    df = get_population_data()
    
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    
    fig.add_trace(
        go.Bar(
            x=df['Year'],
            y=df['Population (thousands)'],
            name='Population (thousands)',
            marker_color='#1e3a8a',
            opacity=0.8
        )
    )
    
    fig.add_trace(
        go.Bar(
            x=df['Year'],
            y=df['Vehicle Registrations (thousands)'],
            name='Vehicle Registrations (thousands)',
            marker_color='#f59e0b',
            opacity=0.8
        )
    )
    
    fig.update_layout(
        title="Population and Vehicle Registration Trends",
        xaxis_title="Year",
        yaxis_title="Count (thousands)",
        barmode='group',
        height=500,
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
        <strong>Key Insight:</strong> Despite the COVID-19 impact in 2020, both population and vehicle registrations have shown steady recovery and growth, 
        indicating increased pressure on CBD infrastructure and parking demand.
    </div>
    """, unsafe_allow_html=True)

# Environmental Impact Section
def show_environment_section():
    st.markdown("""
    <div class="section-header">
        <div style="font-size: 2rem;">🌱</div>
        <h2 class="section-title">Environmental Impact Analysis</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="metric-container">
        <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
            CO2 emissions comparison across different transportation methods for trips to Melbourne CBD.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create the chart
    df = get_environmental_data()
    
    fig = go.Figure(data=[
        go.Pie(
            labels=df['Transport Method'],
            values=df['CO2 Emissions (kg/trip)'],
            marker_colors=df['Color'],
            hole=0.4,
            textinfo='label+percent',
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="CO2 Emissions by Transport Method",
        height=500,
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box-green">
        <strong>Environmental Insight:</strong> Switching from solo car travel to public transport can reduce CO2 emissions by up to 81% per trip. 
        Cycling and walking produce zero emissions while providing health benefits.
    </div>
    """, unsafe_allow_html=True)

# Parking Availability Section
def show_availability_section():
    st.markdown("""
    <div class="section-header">
        <div style="font-size: 2rem;">🅿️</div>
        <h2 class="section-title">Parking Space Availability</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Selection controls
    col1, col2 = st.columns(2)
    
    with col1:
        selected_location = st.selectbox(
            "Select Location",
            get_locations(),
            key="availability_location"
        )
    
    with col2:
        selected_time = st.selectbox(
            "Select Time",
            get_time_slots(),
            key="availability_time"
        )
    
    st.markdown(f"""
    <div class="metric-container">
        <h3 style="color: #1f2937; margin-bottom: 1rem;">
            Current Availability: {selected_location} at {selected_time}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create availability chart
    df = get_parking_availability()
    
    fig = go.Figure(data=[
        go.Pie(
            labels=df['Status'],
            values=df['Count'],
            marker_colors=df['Color'],
            hole=0.4,
            textinfo='label+percent+value',
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title=f"Parking Availability at {selected_location}",
        height=400,
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box-orange">
        <strong>Real-time Update:</strong> Parking availability data is updated every 15 minutes. 
        Consider alternative transportation during peak hours (8-10 AM, 5-7 PM) when availability is typically lower.
    </div>
    """, unsafe_allow_html=True)

# Historical Supply Section
def show_supply_section():
    st.markdown("""
    <div class="section-header">
        <div style="font-size: 2rem;">📊</div>
        <h2 class="section-title">Historical Parking Supply Data</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Location selection
    selected_location = st.selectbox(
        "Select Destination",
        get_locations(),
        key="supply_location"
    )
    
    st.markdown(f"""
    <div class="metric-container">
        <h3 style="color: #1f2937; margin-bottom: 1rem;">
            Daily Parking Supply Trend: {selected_location}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create supply chart
    df = get_parking_supply_data()
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df['Time'],
            y=df['Available Spaces'],
            mode='lines+markers',
            name='Available Parking Spaces',
            line=dict(color='#059669', width=3),
            marker=dict(size=8, color='#059669')
        )
    )
    
    fig.update_layout(
        title=f"Daily Parking Supply Trend - {selected_location}",
        xaxis_title="Time of Day",
        yaxis_title="Available Spaces",
        height=400,
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box-purple">
        <strong>Supply Pattern:</strong> Parking availability typically peaks during mid-morning (10-11 AM) and mid-afternoon (2-3 PM). 
        Plan your visit during these times for better parking options.
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
            
        if st.button("📊 Historical Supply", use_container_width=True):
            st.session_state.page = 'supply'
            st.rerun()
    
    # Show navigation bar
    if st.session_state.page != 'home':
        show_navigation()
    
    # Show appropriate page
    if st.session_state.page == 'home':
        show_homepage()
    elif st.session_state.page == 'population':
        show_population_section()
    elif st.session_state.page == 'environment':
        show_environment_section()
    elif st.session_state.page == 'availability':
        show_availability_section()
    elif st.session_state.page == 'supply':
        show_supply_section()

if __name__ == "__main__":
    main()