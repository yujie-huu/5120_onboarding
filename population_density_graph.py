import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os

def get_population_data(file_name):
    
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, file_name)
    population_growth = pd.read_csv(file_path)
    
    return population_growth

def population_density_plotting()