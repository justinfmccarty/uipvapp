import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc

mapbox_access_token = "pk.eyJ1IjoianVzdGluZm1jY2FydHkiLCJhIjoiY2tkb3hnbzVzMDBuMTJ4bXl1eXdvc3oyaiJ9.Vl4TxX3lRX8YxfrFV8PJ8g"

def generate_bipv_db_map(file_path):
    data = pd.read_csv(file_path)
    fig = go.Figure(
        go.Scattermapbox(
            lat=data['Project Latitude'],
            lon=data['Project Longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=8,
                color='rgb(242, 177, 172)',
                opacity=0.5
                ),
            text=data['Project Name'],
        ),
        )

    fig.update_layout(
        autosize=False,
        margin=dict(l=0, r=0, t=0, b=0),
        
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=40,
                lon=145
            ),
            pitch=0
        ),
    )

    return fig 