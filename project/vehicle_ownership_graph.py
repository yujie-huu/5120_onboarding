import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os

def get_ownership_data(file_name):
    
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, file_name)
    vehicle_ownership = pd.read_csv(file_path)

    return vehicle_ownership

def vehicle_ownership_line_chart(vehicle_ownership):
    years = [col for col in vehicle_ownership.columns if col.isdigit()]
    set2_colors = ["#e78ac3", "#a6d854"]

    fig = go.Figure()
    # Vic. on primary y-axis
    fig.add_trace(go.Scatter(
        x=years,
        y=vehicle_ownership[vehicle_ownership["state"] == "Vic."][years].values.flatten(),
        mode='lines+markers',
        name='Victoria',
        line=dict(color=set2_colors[0]),
        yaxis='y1'
    ))
    # Aust. on secondary y-axis
    fig.add_trace(go.Scatter(
        x=years,
        y=vehicle_ownership[vehicle_ownership["state"] == "Aust."][years].values.flatten(),
        mode='lines+markers',
        name='Australia',
        line=dict(color=set2_colors[1]),
        yaxis='y2'
    ))
    fig.update_layout(
        title=dict(
            text="Vehicle Ownership: Victoria vs Australia",
            x=0.5,
            xanchor="center"
        ),
        xaxis_title="Year",
        yaxis=dict(title='Victoria'),
        yaxis2=dict(title='Australia', overlaying='y', side='right'),
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
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    vehicle_ownership = get_ownership_data("vehicle_ownership_clean.csv")
    print(vehicle_ownership.head())
    vehicle_ownership_line_chart(vehicle_ownership)