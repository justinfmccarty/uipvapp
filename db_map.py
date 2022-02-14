import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from utils import get_color_dict as colors
from utils import is_retrofit

mapbox_access_token = "pk.eyJ1IjoianVzdGluZm1jY2FydHkiLCJhIjoiY2tkb3hnbzVzMDBuMTJ4bXl1eXdvc3oyaiJ9.Vl4TxX3lRX8YxfrFV8PJ8g"


def choose_colors(project_type):
    if project_type == 'Retrofit':
        return colors()['retrofit_cat']
    else:
        return colors()['new_cat']


def generate_bipv_db_map(data):
    plot_data = data.copy()
    plot_data['Project Type'] = plot_data.apply(lambda x: is_retrofit(x['Project Built Year'], x['Project Plant Year']),
                                                axis=1)

    plot_data['Color'] = plot_data.apply(lambda x: choose_colors(x['Project Type']),
                                         axis=1)

    fig = go.Figure(
        go.Scattermapbox(
            lat=plot_data['Project Latitude'],
            lon=plot_data['Project Longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=12,
                color=plot_data['Color'],
                opacity=0.5,
            ),
            hoverinfo='none',
        ),
    )

    fig.update_layout(
        autosize=True,
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
