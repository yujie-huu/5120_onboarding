import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests

def plotting_carbon_emission(api_url):
    # Fetch data from Lambda/API Gateway
    response = requests.get(api_url)
    data = response.json()  # Should be a list of dicts

    # Convert to DataFrame
    carbon_emission = pd.DataFrame(data)

    # Sort by carbon_emission descending
    carbon_emission_sorted = carbon_emission.sort_values(by='carbon_emission', ascending=False).reset_index(drop=True)
    set2_colors = ["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854", "#ffd92f", "#e5c494", "#b3b3b3"]
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
        yaxis_title="Carbon Emission",
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    st.plotly_chart(carbon_emission_plot, use_container_width=True)

# Example usage in your Streamlit app:
# plotting_carbon_emission("https://your-api-gateway-url/prod/your-lambda-endpoint")