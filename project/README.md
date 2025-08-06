# Melbourne CBD Parking & Transport Dashboard

A comprehensive web application built with Python Streamlit for displaying parking availability and commuting information in Melbourne's CBD.

## Features

1. **Real-Time Parking Availability** - Find available parking spaces across Melbourne CBD locations
2. **Population & Vehicle Growth Analysis** - Track demographic and vehicle registration trends
3. **Environmental Impact Assessment** - Compare CO2 emissions across different transport methods
4. **Historical Parking Supply Data** - Analyze parking supply trends by location and time

## Installation

1. Install Python 3.8 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Deployment

This application can be deployed to various cloud platforms:

- **Streamlit Cloud**: Connect your GitHub repository to Streamlit Cloud
- **Heroku**: Use the provided requirements.txt for deployment
- **AWS/GCP/Azure**: Deploy using container services or app platforms

## Data Sources

The application uses simulated data for demonstration purposes. In a production environment, you would connect to:

- Real-time parking sensors and APIs
- Government demographic databases
- Transport authority data feeds
- Environmental monitoring systems

## Technology Stack

- **Python 3.8+**
- **Streamlit** - Web application framework
- **Plotly** - Interactive charts and visualizations
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computations