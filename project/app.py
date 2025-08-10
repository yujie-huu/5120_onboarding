import requests
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
def get_parking_availability():
    """
    获取停车相关的所有数据：街道列表、停车区域信息、车位状态
    """
    try:
        # 获取街道列表
        print("正在获取街道列表...")
        streets_response = requests.get("https://ldr1cwcs34.execute-api.ap-southeast-2.amazonaws.com/streets")
        print(f"街道API状态码: {streets_response.status_code}")

        streets_list = []
        if streets_response.status_code == 200:
            streets_data = streets_response.json()
            print(f"街道API原始响应: {streets_data}")
            print(f"街道数据类型: {type(streets_data)}")

            # 解析街道列表
            if isinstance(streets_data, dict) and 'body' in streets_data:
                streets_body = streets_data['body']
                print(f"街道body内容: {streets_body}")
                print(f"街道body类型: {type(streets_body)}")

                # 尝试多种解析方法
                try:
                    # 方法1: 直接JSON解析
                    if isinstance(streets_body, str):
                        import json
                        streets_list = json.loads(streets_body)
                    else:
                        streets_list = streets_body
                    print(f"方法1成功，街道数量: {len(streets_list)}")
                except Exception as e1:
                    print(f"方法1失败: {e1}")
                    try:
                        # 方法2: 处理特殊格式
                        if isinstance(streets_body, str) and '"on street list"' in streets_body:
                            # 提取引号内的内容
                            import re
                            matches = re.findall(r'"([^"]*street[^"]*)"', streets_body, re.IGNORECASE)
                            streets_list = [match for match in matches if 'street' in match.lower()]
                            print(f"方法2成功，街道数量: {len(streets_list)}")
                    except Exception as e2:
                        print(f"方法2失败: {e2}")
                        print("街道列表解析失败")

        # 获取停车区域信息
        print("正在获取停车区域信息...")
        zones_response = requests.get(
            "https://ldr1cwcs34.execute-api.ap-southeast-2.amazonaws.com/sign-plates-requirements")
        print(f"区域API状态码: {zones_response.status_code}")

        zones_df = pd.DataFrame()
        if zones_response.status_code == 200:
            zones_data = zones_response.json()
            print(f"区域API响应类型: {type(zones_data)}")
            print(f"区域API响应内容: {zones_data}")

            # 解析停车区域数据
            if isinstance(zones_data, dict) and 'body' in zones_data:
                try:
                    zones_body = json.loads(zones_data['body'])
                    if 'result' in zones_body:
                        zones_df = pd.DataFrame(zones_body['result'])
                        print(f"停车区域数据行数: {len(zones_df)}")
                        if not zones_df.empty:
                            print(f"区域数据列: {zones_df.columns.tolist()}")
                            print(f"区域数据示例:\n{zones_df.head()}")
                    else:
                        print("区域数据中没有找到 'result' 字段")
                except json.JSONDecodeError as e:
                    print(f"解析区域JSON数据时出错: {e}")
            else:
                print("区域API响应格式不正确")

        # 获取车位状态
        print("正在获取车位状态...")
        status_response = requests.get("https://ldr1cwcs34.execute-api.ap-southeast-2.amazonaws.com/status")
        print(f"状态API状态码: {status_response.status_code}")

        status_df = pd.DataFrame()
        available_zones = []
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"状态API响应类型: {type(status_data)}")
            print(f"状态API响应内容: {status_data}")

            # 解析车位状态数据
            if isinstance(status_data, dict) and 'body' in status_data:
                try:
                    status_body = json.loads(status_data['body'])

                    # 获取可用区域列表
                    available_zones = status_body.get('zones', [])
                    print(f"可用区域数量: {len(available_zones)}")
                    print(f"可用区域: {available_zones[:10]}...")  # 显示前10个区域

                    # 获取车位状态详细信息
                    if 'result' in status_body:
                        status_df = pd.DataFrame(status_body['result'])
                        print(f"车位状态数据行数: {len(status_df)}")
                        if not status_df.empty:
                            print(f"状态数据列: {status_df.columns.tolist()}")
                            print(f"状态数据示例:\n{status_df.head()}")

                            # 显示状态分布
                            if 'Status_Description' in status_df.columns:
                                status_counts = status_df['Status_Description'].value_counts()
                                print(f"车位状态分布:\n{status_counts}")
                    else:
                        print("状态数据中没有找到 'result' 字段")
                except json.JSONDecodeError as e:
                    print(f"解析状态JSON数据时出错: {e}")
            else:
                print("状态API响应格式不正确")

        return streets_list, zones_df, status_df, available_zones

    except Exception as e:
        print(f"获取停车数据时出错: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return [], pd.DataFrame(), pd.DataFrame(), []

def get_parking_supply_data():
    pass

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

    # 主要功能 - 停车可用性 (占据显著位置)
    st.markdown("""
    <div class="feature-card main-feature" style="
        background: linear-gradient(135deg, #ff9a56 0%, #ff6b35 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(255, 107, 53, 0.3);
        text-align: center;
        margin: 2rem 0;
        border: none;
    ">
        <div style="font-size: 5rem; margin-bottom: 1rem;">🅿️</div>
        <h2 style="margin-bottom: 1rem; font-size: 2.2rem; font-weight: 700;">Real-Time Parking Availability</h2>
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
            📍 Check Available Spaces Now
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 主要功能按钮
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🅿️ **FIND PARKING NOW**", key="main_parking",
                     use_container_width=True, type="primary"):
            st.session_state.page = "availability"
            st.rerun()

    # 分隔线
    st.markdown("<hr style='margin: 3rem 0; border: 1px solid #e5e7eb;'>", unsafe_allow_html=True)

    # 次要功能标题
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h3 style="color: #374151; font-weight: 600; font-size: 1.5rem;">Additional Information Display</h3>
        <p style="color: #6b7280; font-size: 1rem;">Explore more insights about Melbourne transport patterns</p>
    </div>
    """, unsafe_allow_html=True)

    # 次要功能 - 平衡布局
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="feature-card secondary-feature" style="
            background: linear-gradient(135deg, #fef3e2 0%, #fed7aa 100%);
            color: #92400e;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(251, 146, 60, 0.2);
            text-align: center;
            height: 280px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            border: 1px solid #fed7aa;
        ">
            <div>
                <div style="font-size: 3.5rem; margin-bottom: 1rem;">👥</div>
                <h4 style="margin-bottom: 1rem; font-size: 1.4rem; font-weight: 600;">Population & Vehicle Growth</h4>
                <p style="font-size: 1rem; opacity: 0.8; line-height: 1.5;">
                    Analyze population and vehicle registration trends affecting parking demand
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("👥 **Population & Vehicle Trends**", key="population",
                     use_container_width=True):
            st.session_state.page = "population"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="feature-card secondary-feature" style="
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            color: #166534;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(34, 197, 94, 0.2);
            text-align: center;
            height: 280px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            border: 1px solid #dcfce7;
        ">
            <div>
                <div style="font-size: 3.5rem; margin-bottom: 1rem;">🌱</div>
                <h4 style="margin-bottom: 1rem; font-size: 1.4rem; font-weight: 600;">Environmental Impact</h4>
                <p style="font-size: 1rem; opacity: 0.8; line-height: 1.5;">
                    Compare CO2 emissions across different transport methods and parking choices
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🌱 **Environmental Analysis**", key="environment",
                     use_container_width=True):
            st.session_state.page = "environment"
            st.rerun()


def show_population_vehicle_section():
    """
    Display the chart showing population growth and vehicle ownership.
    """
    # 返回按钮 - 永远置顶
    st.markdown('<div style="position: sticky; top: 0; z-index: 999; background: white; padding: 10px 0;">', unsafe_allow_html=True)
    if st.button("← Back to Home", key="back_to_home_population",
                 help="Return to main dashboard"):
        st.session_state.page = "home"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="section-header">
        <div style="font-size: 2rem;">👥</div>
        <h2 class="section-title">Population & Vehicle Growth Impact</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="metric-container">
        <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
            This section illustrates the population growth trends across Melbourne CBD regions and vehicle ownership in Victoria.
        </p>
    </div>
    """, unsafe_allow_html=True)

    try:
        # 获取人口数据并显示人口增长图表
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

        # 配置去除工具栏中的reset和plotly logo
        config = {
            'displayModeBar': True,
            'modeBarButtonsToRemove': ['resetScale2d', 'resetViewMapbox'],
            'displaylogo': False
        }

        st.plotly_chart(population_growth_plot, use_container_width=True, config=config)

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

        st.plotly_chart(vehicle_fig, use_container_width=True, config=config)

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.write("Please check the API connection and data format.")

    st.markdown("""
    <div class="insight-box">
        <strong>Key Insight:</strong> The combined trends of population growth in Melbourne CBD and increasing vehicle ownership in Victoria 
        indicate growing pressure on urban infrastructure and parking demand, highlighting the need for sustainable transportation solutions.
    </div>
    """, unsafe_allow_html=True)

# Environmental Impact Section
def show_environment_section():
    """
    显示环境影响图表 - 各交通方式的碳排放
    """
    # 返回按钮 - 固定在顶部
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
            This chart shows the average individual carbon emissions by different transport types, highlighting the environmental impact of transportation choices.
        </p>
    </div>
    """, unsafe_allow_html=True)

    try:
        # 获取环境数据
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

        # 配置去除工具栏中的reset和plotly logo
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
        <strong>Environmental Insight:</strong> The data reveals significant differences in carbon emissions across transport modes, 
        demonstrating the environmental benefits of choosing more sustainable transportation options like public transport and cycling.
    </div>
    """, unsafe_allow_html=True)

# Parking Availability Section
def show_availability_section():
    """
    显示停车位可用性信息
    """
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
        # 获取停车数据
        streets_list, zones_df, status_df, available_zones = get_parking_availability()

        # 在Streamlit中显示调试信息
        with st.expander("调试信息 (Debug Info)", expanded=False):
            st.write(f"街道列表长度: {len(streets_list)}")
            st.write(f"停车区域数据行数: {len(zones_df)}")
            st.write(f"车位状态数据行数: {len(status_df)}")
            st.write(f"可用区域数量: {len(available_zones)}")

        # 检查街道列表
        if not streets_list:
            st.warning("无法获取街道列表数据")
            return

        # 街道选择
        selected_street = st.selectbox(
            "Select Street",
            streets_list,
            key="availability_street"
        )

        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #1f2937; margin-bottom: 1rem;">
                Parking Information for: {selected_street}
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # 显示停车区域信息
        if not zones_df.empty:
            st.subheader("Parking Zone Restrictions")
            zones_display = zones_df[['Parkingzone', 'Restriction Days', 'Time Restrictions start',
                                      'Time Restrictions Finish', 'Restriction Display']].copy()
            st.dataframe(zones_display, use_container_width=True)
        else:
            st.warning("无法获取停车区域限制数据")

        # 显示车位状态统计
        if not status_df.empty:
            st.subheader("Current Parking Space Status")

            # 统计各状态的车位数量
            status_summary = status_df['Status_Description'].value_counts().reset_index()
            status_summary.columns = ['Status', 'Count']

            # 添加颜色映射
            color_map = {
                'Unoccupied': '#22c55e',  # 绿色
                'Occupied': '#ef4444',  # 红色
                'Out of Order': '#f59e0b'  # 黄色
            }
            status_summary['Color'] = status_summary['Status'].map(lambda x: color_map.get(x, '#6b7280'))

            # 显示统计表格
            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(status_summary[['Status', 'Count']], use_container_width=True)

            with col2:
                # 创建饼图显示状态分布
                fig = go.Figure(data=[
                    go.Pie(
                        labels=status_summary['Status'],
                        values=status_summary['Count'],
                        marker_colors=status_summary['Color'],
                        hole=0.4,
                        textinfo='label+percent+value',
                        textposition='outside'
                    )
                ])

                fig.update_layout(
                    title="Overall Parking Status Distribution",
                    height=400,
                    showlegend=True,
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )

                st.plotly_chart(fig, use_container_width=True)

            # 显示可用停车区域
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
            st.warning("无法获取车位状态数据")

    except Exception as e:
        st.error(f"Error loading parking availability data: {str(e)}")
        st.write("Please check the API connections and data format.")

    st.markdown("""
    <div class="insight-box">
        <strong>Parking Insight:</strong> Real-time parking availability data helps optimize parking space utilization 
        and reduces traffic congestion caused by drivers searching for parking spots.
    </div>
    """, unsafe_allow_html=True)
'''
def show_availability_section():
        """
        显示停车位可用性信息
        """
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
            # 获取停车数据
            streets_list, zones_df, status_df, available_zones = get_parking_availability()

            if not streets_list:
                st.error("无法获取街道列表")
                return

            # 街道选择
            selected_street = st.selectbox(
                "Select Street",
                streets_list,
                key="availability_street"
            )

            st.markdown(f"""
            <div class="metric-container">
                <h3 style="color: #1f2937; margin-bottom: 1rem;">
                    Parking Information for: {selected_street}
                </h3>
            </div>
            """, unsafe_allow_html=True)

            # 显示该街道的停车区域信息
            if not zones_df.empty:
                st.subheader("Parking Zone Restrictions")

                # 显示停车区域限制信息
                zones_display = zones_df[['Parkingzone', 'Restriction Days', 'Time Restrictions start',
                                          'Time Restrictions Finish', 'Restriction Display']].copy()

                st.dataframe(zones_display, use_container_width=True)

            # 显示车位状态统计
            if not status_df.empty:
                st.subheader("Current Parking Space Status")

                # 统计各状态的车位数量
                status_summary = status_df['Status_Description'].value_counts().reset_index()
                status_summary.columns = ['Status', 'Count']

                # 添加颜色映射
                color_map = {
                    'Unoccupied': '#22c55e',  # 绿色
                    'Occupied': '#ef4444',  # 红色
                    'Out of Order': '#f59e0b'  # 黄色
                }
                status_summary['Color'] = status_summary['Status'].map(lambda x: color_map.get(x, '#6b7280'))

                # 显示统计表格
                col1, col2 = st.columns(2)

                with col1:
                    st.dataframe(status_summary[['Status', 'Count']], use_container_width=True)

                with col2:
                    # 创建饼图显示状态分布
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=status_summary['Status'],
                            values=status_summary['Count'],
                            marker_colors=status_summary['Color'],
                            hole=0.4,
                            textinfo='label+percent+value',
                            textposition='outside'
                        )
                    ])

                    fig.update_layout(
                        title="Overall Parking Status Distribution",
                        height=400,
                        showlegend=True,
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )

                    st.plotly_chart(fig, use_container_width=True)

                # 显示可用停车区域
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

        except Exception as e:
            st.error(f"Error loading parking availability data: {str(e)}")
            st.write("Please check the API connections and data format.")

        st.markdown("""
        <div class="insight-box">
            <strong>Parking Insight:</strong> Real-time parking availability data helps optimize parking space utilization 
            and reduces traffic congestion caused by drivers searching for parking spots.
        </div>
        """, unsafe_allow_html=True)
'''


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