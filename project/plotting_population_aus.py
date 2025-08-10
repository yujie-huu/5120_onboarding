import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
from plotly.subplots import make_subplots
import pandas as pd

def plotting_population_growth_aus(api_url):
    # Fetch data from Lambda/API Gateway
    response = requests.get(api_url)
    data = response.json()  # Should be a list of dicts

    # Convert to DataFrame
    population_growth = pd.DataFrame(data)
    
    # Filter only Vic and Aus data
    regions = ["Total Victoria", "Total Australia"]
    population_growth_aus = population_growth[population_growth["region"].isin(regions)]
    year_columns = [col for col in population_growth.columns if col.isdigit() or (col.startswith("20") and col[2:].isdigit())]
    population_growth_aus = population_growth_aus.set_index("region").loc[regions, year_columns].T.astype(float)

    # Plotly line chart with two y-axes
    
    # Get hex color codes
    set2_colors = ["#e78ac3", "#a6d854"]
    # Get 2 y-axes
    population_growth_plot = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces: first region on primary y, second region on secondary y
    population_growth_plot.add_trace(
        go.Scatter(
            x = population_growth_aus.index,
            y = population_growth_aus[regions[0]],
            mode = 'lines',
            name = regions[0],
            line = dict(color = set2_colors[0])
        ),
        secondary_y=False
    )
    population_growth_plot.add_trace(
        go.Scatter(
            x = population_growth_aus.index,
            y = population_growth_aus[regions[1]],
            mode = 'lines',
            name = regions[1],
            line = dict(color = set2_colors[1])
        ),
        secondary_y = True
    )

    population_growth_plot.update_layout(
        title = dict(
            text = "Population Growth: Victoria and Australia",
            x = 0.5,
            xanchor = "center"
        ),
        xaxis_title = "Year",
        height = 500,
        showlegend = True,
        legend = dict(
            orientation = "h",
            yanchor = "bottom",
            y = -0.3,
            xanchor = "center",
            x = 0.5
        ),
        plot_bgcolor = 'white',
        paper_bgcolor = 'white'
    )
    # Force y-axes to start at zero by setting autorange to False and specifying max
    vic_max = population_growth_aus[regions[0]].max()
    aus_max = population_growth_aus[regions[1]].max()
    population_growth_plot.update_yaxes(title_text=regions[0], range=[0, vic_max], autorange=False, secondary_y=False)
    population_growth_plot.update_yaxes(title_text=regions[1], range=[0, aus_max], autorange=False, secondary_y=True)
    
    st.plotly_chart(population_growth_plot, use_container_width=True)

# Example usage in your Streamlit app:
# plotting_population_growth_aus("https://your-api-gateway-url/prod/your-lambda-endpoint")