import numpy as np
from dash import dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL, no_update
import db_map
import dash_bootstrap_components as dbc
import pandas as pd
import io
import base64
import plotly.graph_objects as go
import time
from PIL import Image


external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(
    __name__,
    assets_folder = 'assets',
    external_stylesheets=external_stylesheets
    )

server = app.server

data = pd.read_csv('assets/database_records.csv')

def get_menu_items():
    return ['About','Map','Overview','Viewer','Compare'][::-1]

def pop_over_description(menu_item_name):
    if menu_item_name=='About':
        return 'About Popup'
    elif menu_item_name=='Map':
        return 'About Map'
    elif menu_item_name=='Overview':
        return 'About Overview'
    elif menu_item_name=='Viewer':
        return 'About Viewer'
    elif menu_item_name=='Compare':
        return 'About Compare'

def get_popover_children():
    popover_children = dict()
    menu_items = get_menu_items()
    for item in menu_items:
        popover_children[item]=dbc.PopoverBody(pop_over_description(item),className='hover_note')
    return popover_children

def create_menu_row(menu_item_name):
    popover_children = get_popover_children()[menu_item_name]
    main_div = [html.Div(
        dbc.NavItem(
            dbc.NavLink(menu_item_name,
                        active=True,
                        href=f"/page-{menu_item_name.lower()}",
                        className='link_text',
                        id=f'{menu_item_name}_link')
            ),className='nav_item',id=f'{menu_item_name}_button'),
            dbc.Popover(popover_children,
                        hide_arrow=True,
                        id=f"{menu_item_name}_hover",
                        target=f"{menu_item_name}_link",
                        trigger="hover")]
    return main_div

def create_nav_items():
    out_items = []
    for menu_item in get_menu_items():
        out_items.append(create_menu_row(menu_item))
    return [item for sublist in out_items for item in sublist]

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Nav(
                create_nav_items(),
                vertical=False,id='nav_bar'),
                ],width=3,id='nav_col'),
        ######## break to body
        dbc.Col([
            html.Div(id='body_col_child')],
            width=9,
            id='body_col'),
    ],id='main_row'),
    dbc.Row([
        dbc.Col(html.Div(),width=12,id='footer')
        ],id='footer_row')
],id='page')


layout_about_page = html.Div([
    html.H2('About goes here',className='placeholder_text')
])

layout_map_page = html.Div([
    dcc.Graph(
        id='map',
        figure=db_map.generate_bipv_db_map(data),
        responsive=True,
        clear_on_unhover=True),
    dcc.Tooltip(
        id="graph_tooltip",
        loading_text="LOADING",),
], className='content_container')

url_bar_and_content_div = html.Div([
    dcc.Location(id='url', refresh=False),
    layout
])

# index layout
app.layout = url_bar_and_content_div

# "complete" layout
app.validation_layout = html.Div([
    url_bar_and_content_div,
    layout,
    layout_about_page,
    layout_map_page,
])

# Index callbacks
@app.callback(Output('body_col_child', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == "/page-about":
        return layout_about_page
    elif pathname == "/page-map":
        return layout_map_page
    else:
        return layout_about_page

@app.callback(
    Output("graph_tooltip", "show"),
    Output("graph_tooltip", "bbox"),
    Output("graph_tooltip", "children"),
    Input("map", "hoverData"),
)
def display_hover(hoverData):
    if hoverData is None:
        return False, no_update, no_update
    else:
        time.sleep(0.5)
        # demo only shows the first point, but other points may also be available
        pt = hoverData["points"][0]
        bbox = pt["bbox"]
        num = pt["pointNumber"]
        #
        data_row = data.iloc[num]
        # img_src = data_row['IMG_URL']
        name = data_row['Project Name']
        lat = data_row['Project Latitude']
        long = data_row['Project Longitude']
        desc = data_row['Project Description']

        image_path = r'assets/test_image.jpeg'
        im = Image.open(image_path)
        # dump it to base64
        buffer = io.BytesIO()
        im.save(buffer, format="jpeg")
        encoded_image = base64.b64encode(buffer.getvalue()).decode()
        img_src = "data:image/jpeg;base64, " + encoded_image

        if desc is np.nan:
            desc = 'No description available'
        else:
            if len(desc) > 300:
                desc = desc[:100] + '...'

        children = [
            html.Div([
                html.Img(src=img_src, style={"width": "100%"}),
                html.H2(f"{name}", style={"color": "darkblue"}),
                html.P(f"{lat}, {long}"),
                html.P(f"{desc}"),
            ], className='map_hover_box')
        ]
        return True, bbox, children


if __name__ == '__main__':
    app.run_server(
        debug=True)

