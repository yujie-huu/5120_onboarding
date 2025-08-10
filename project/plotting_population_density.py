import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests

def plotting_population_density(api_url = "https://ldr1cwcs34.execute-api.ap-southeast-2.amazonaws.com/getPopulationGrowth"):
    # Fetch data from Lambda/API Gateway
    response = requests.get(api_url)
    data = response.json()  # Should be a list of dicts

    # Convert to DataFrame
    population_growth = pd.DataFrame(data)
    
    # Select regions and years
    regions = ["Melbourne CBD - East", "Melbourne CBD - North", "Melbourne CBD - West", "Total Victoria", "Total Australia"]
    years = ["2001", "2011", "2021"]

    # Prepare data for grouped bar chart
    population_density = []
    for region in regions:
        densities = []
        area = float(population_growth.loc[population_growth["region"] == region, "area"].values[0])
        for year in years:
            population = float(population_growth.loc[population_growth["region"] == region, year].values[0])
            densities.append(population / area)
        population_density.append(densities)

    # Create grouped bar chart
    population_density_plot = go.Figure()
    set2_colors = ["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854"]
    for i, region in enumerate(regions):
        population_density_plot.add_trace(go.Bar(
            x=years,
            y=population_density[i],
            name=region,
            marker_color=set2_colors[i],
            text=[str(int(round(val))) for val in population_density[i]],
            textposition='outside'
        ))

    population_density_plot.update_layout(
        barmode='group',
        title=dict(
            text="Population Density by Region (2001, 2011, 2021)",
            x=0.5,
            xanchor="center"
        ),
        xaxis_title="Year",
        yaxis_title="Population Density (per sq km)",
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
    st.plotly_chart(population_density_plot, use_container_width=True)


# Example usage in your Streamlit app:
# plotting_population_density("https://your-api-gateway-url/prod/your-lambda-endpoint")