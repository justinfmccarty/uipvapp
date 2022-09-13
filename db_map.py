import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from utils import get_color_dict as colors
from utils import is_retrofit, choose_colors, flatten

import os

head_file = os.path.join('.git', 'HEAD')

with open(head_file, "r") as fp:
    branch = fp.readlines()[0]

if "master" in branch:
    mapbox_access_token = os.getenv('MAPBOX_KEY')
else:
    secret_file = os.path.join('secrets', 'token.txt')
    with open(secret_file, "r") as fp:
        mapbox_access_token = fp.readlines()[0]


def generate_bipv_db_map(data):
    plot_data = data.copy()
    plot_data['Project Type'] = plot_data.apply(lambda x: is_retrofit(x['Project Built Year'],
                                                                      x['Project Plant Year']),
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


def map_modal():
    return html.Div(
        id='map_modal',
        className='map_modal',
        style={"display": "none"},
    )


def map_table(data, columns, header, col_list, div_id):
    df = data.copy()
    plant_year = df["Project Plant Year"]
    built_year = df["Project Built Year"]
    if plant_year == built_year:
        df.drop(labels=['Project Plant Year'],inplace=True)
        col_list[0] = [x for x in col_list[0] if not "Project Plant Year" in x]

    header_lists = ["Project Details", "System Details", "Array Details"]

    tables = list(zip(header_lists, col_list))
    set = []
    for tup in tables:
        title = [html.Tr(html.Td(tup[0], colSpan=2), className="modal_table_break")]
        content = [html.Tr([html.Td(col,
                                    className="table_col_a"),
                            html.Td(df[col],
                                    className="table_col_b")],
                           className="modal_table_row") for col in tup[1]]
        set.append(title + content)

    return html.Table(flatten(set), id=div_id,
                      className="map_modal_table")
