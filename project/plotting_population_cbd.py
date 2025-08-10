import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests


def plotting_population_growth_cbd(api_url):
    # Fetch data from Lambda/API Gateway
    response = requests.get(api_url)
    data = response.json()  # Should be a list of dicts

    # Convert to DataFrame
    population_growth = pd.DataFrame(data)
    
    # Filter only CBD data
    regions = ["Melbourne CBD - East", "Melbourne CBD - North", "Melbourne CBD - West"]
    population_growth_cbd = population_growth[population_growth["region"].isin(regions)]
    year_columns = [col for col in population_growth.columns if col.isdigit() or (col.startswith("20") and col[2:].isdigit())]
    population_growth_cbd = population_growth_cbd.set_index("region").loc[regions, year_columns].T.astype(float)

    # Plotly area chart
    
    # Get hex color codes
    set2_colors = ["#66c2a5", "#fc8d62", "#8da0cb"]
    # Create the plot
    population_growth_plot = go.Figure()
    for i, region in enumerate(regions):
        # Plot
        population_growth_plot.add_trace(go.Scatter(
            x = population_growth_cbd.index,
            y = population_growth_cbd[region],
            mode = 'lines',
            stackgroup = 'one',
            name = region,
            line = dict(color = set2_colors[i])
        ))
    # Set y-axis to start at zero and go to the max value across all regions
    # For stacked area, y_max should be the max of the row-wise sum (total population per year)
    y_max = population_growth_cbd.sum(axis=1).max()
    population_growth_plot.update_layout(
        title = dict(
            text = "Population Growth: Melbourne CBD Regions",
            x = 0.5,
            xanchor = "center"
        ),
        xaxis_title = "Year",
        yaxis_title = "Population",
        height = 500,
        showlegend = True,
        legend = dict(
            orientation = "h",
            yanchor = "bottom",
            y = -0.3,  # Adjust as needed for spacing
            xanchor = "center",
            x = 0.5
        ),
        plot_bgcolor = 'white',
        paper_bgcolor = 'white',
        yaxis=dict(range=[0, y_max])
    )
    
    st.plotly_chart(population_growth_plot, use_container_width=True)
    

# Example usage in your Streamlit app:
# plotting_population_growth_cbd("https://your-api-gateway-url/prod/your-lambda-endpoint")