import numpy as np
from dash import dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL, no_update
import db_map, db_overview
import dash_bootstrap_components as dbc
import pandas as pd
import io
import base64
import plotly.graph_objects as go
import time
from utils import is_retrofit, choose_colors, generate_table
from PIL import Image

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(
    __name__,
    assets_folder='assets',
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets
)

server = app.server
about_file = open('assets/about_description.txt', 'r')
data = pd.read_csv('assets/database_display.csv')


def get_menu_items():
    return ['About', 'Map', 'Overview', 'Viewer', 'Literature'][::-1]


def popover_description_hover(menu_item_name):
    if menu_item_name == 'About':
        text = """Here you can read more about the repository and see our partners. We also have a link to 
                    similar catalogs of BIPV projects and our own code base."""
        return text
    elif menu_item_name == 'Map':
        text = """We have built an interactive map for all of the projects in the repository. Hover over a point 
                  to view a preview or click expand to see the entire record of data."""
        return text
    elif menu_item_name == 'Overview':
        text = """View and download plots of the data in the reporsitory from this page. We are constantly expanding 
                    the visualizations used to describe the project list."""
        return text
    elif menu_item_name == 'Viewer':
        text = """Coming soon."""
        return text
    elif menu_item_name == 'Literature':
        text = """Using a Natural Language Processing technique known as Latent Dirichlet Allocation we have
                    created a set of ten research topics from over 3,400 papers relevant to urban photovoltaic 
                    research. On this page you can query the database of papers."""
        return text


def popover_description_click(menu_item_name):
    if menu_item_name == 'About':
        text = "None"
        return text
    elif menu_item_name == 'Map':
        text = "Legend Detail"
        return text
    elif menu_item_name == 'Overview':
        text = "None"
        return text
    elif menu_item_name == 'Viewer':
        text = "None"
        return text
    elif menu_item_name == 'Literature':
        text = "None"
        return text


def get_popover_children_hover():
    popover_children = dict()
    menu_items = get_menu_items()
    for item in menu_items:
        popover_children[item] = dbc.PopoverBody(popover_description_hover(item),
                                                 class_name='hover_note')
    return popover_children


def get_popover_children_click():
    popover_children = dict()
    menu_items = get_menu_items()
    for item in menu_items:
        popover_children[item] = dbc.PopoverBody(popover_description_click(item),
                                                 class_name='hover_note')
    return popover_children


def create_menu_row(menu_item_name):
    popover_child_hover = get_popover_children_hover()[menu_item_name]
    popover_child_click = get_popover_children_click()[menu_item_name]
    main_div = [html.Div(
        dbc.NavItem(
            dbc.NavLink(menu_item_name,
                        active=True,
                        href=f"/page-{menu_item_name.lower()}",
                        className='link_text',
                        id=f'{menu_item_name}_link')
        ),
        n_clicks=0,
        className='nav_item',
        id=f'{menu_item_name}_button'),
        dbc.Popover(popover_child_hover,
                    hide_arrow=True,
                    id=f"{menu_item_name}_hover",
                    target=f"{menu_item_name}_link",
                    delay={"show": 0, "hide": 100},
                    trigger="hover"),

        dbc.Popover(popover_child_click,
                    hide_arrow=True,
                    id=f"{menu_item_name}_click",
                    target=f"{menu_item_name}_link",
                    # delay={"show": 150, "hide": 10000},
                    is_open=False,
                    # trigger="focus"
                    )
    ]
    return main_div


def create_nav_items():
    out_items = []
    for menu_item in get_menu_items():
        out_items.append(create_menu_row(menu_item))
    return [item for sublist in out_items for item in sublist]


def build_layout():
    return dbc.Container([
        dbc.Row([
            html.Div(id="hidden_div", style={"display": "none"}),
            dbc.Col([
                dbc.Nav(
                    create_nav_items(),
                    vertical=False, id='nav_bar'),
            ], width=3, id='nav_col'),
            ######## break to body
            dbc.Col([
                html.Div(id='body_col_child')],
                width=9,
                id='body_col'),
        ], id='main_row'),
        dbc.Row([
            dbc.Col(html.Div(), width=12, id='footer')
        ], id='footer_row')
    ], id='page')


layout = build_layout()

layout_about_page = html.Div([
    html.H3('The Repository for Integrated Solar Energy in the Built Environment',
            style={"color": "white"}),
    html.P(about_file.read(), id='abstract')
], id='about_page')

layout_map_page = html.Div([
    dcc.Graph(
        id='map',
        figure=db_map.generate_bipv_db_map(data),
        responsive=True,
        animate=True,
        clear_on_unhover=True,
        config={"displayModeBar": False}),
    dcc.Tooltip(
        id="graph_tooltip",
        loading_text="Loading..."),
    html.Div(
        id="legend_container"
    ),
    html.Div(children=[db_map.map_modal()
                       ]
             ),
], className='content_container')

layout_overview_page = html.Div([
    html.Div([
        dcc.Graph(
            figure=db_overview.make_projects_by_year(data),
            responsive=True,
            clear_on_unhover=True),
    ], className='overview_graphs'),
    html.Div([
        dcc.Graph(
            figure=db_overview.make_projects_by_generation_capacity(data),
            responsive=True,
            clear_on_unhover=True),
    ], className='overview_graphs'),
    html.Div([
        dcc.Graph(
            figure=db_overview.make_projects_by_generation_capacity(data),
            responsive=True,
            clear_on_unhover=True),
    ], className='overview_graphs'),
    html.Div([
        dcc.Graph(
            figure=db_overview.make_projects_by_year(data),
            responsive=True,
            clear_on_unhover=True),
    ], className='overview_graphs'),
], className='overview_container')

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
    elif pathname == "/page-overview":
        return layout_overview_page
    else:
        return layout_about_page


@app.callback(
    Output("graph_tooltip", "show"),
    Output("graph_tooltip", "bbox"),
    Output("graph_tooltip", "children"),
    Input("map", "hoverData"))
def display_hover(hover_data):
    if hover_data is None:
        return False, no_update, no_update
    else:
        # time.sleep(0.25)

        pt = hover_data["points"][0]
        bbox = pt["bbox"]
        num = pt["pointNumber"]

        data_row = data.iloc[num]
        img_src = data_row['Image Name']
        name = data_row['Project Name']
        title_sz = 250 / len(name)
        lat = round(data_row['Project Latitude'], 2)
        long = round(data_row['Project Longitude'], 2)
        proj_type = is_retrofit(data_row['Project Built Year'], data_row['Project Plant Year'])
        build_type = data_row['Project Function']
        year = data_row['Project Plant Year'].astype(int)
        desc = data_row['Project Description']

        if img_src is np.nan:
            image_path = r'assets/images/placeholder.jpg'
        else:
            image_path = f'assets/images/{img_src}.jpg'
        im = Image.open(image_path)
        buffer = io.BytesIO()
        im.save(buffer, format="jpeg")
        encoded_image = base64.b64encode(buffer.getvalue()).decode()
        img_src = "data:image/jpeg;base64, " + encoded_image

        if desc is np.nan:
            desc = 'No description available'
        else:
            if len(desc) > 300:
                pass
                # desc = desc[:100] + '...'

        children = [
            html.Div(children=[
                html.Img(src=img_src, id="hover_image"),
                html.H2(name,
                        id="hover_name",
                        style={"font-size": f"clamp({int(title_sz * 0.75)}px,{int(title_sz * 1.5)}px,25px"}
                        ),
                html.P(f"{build_type} {proj_type} {year}"),
                html.P(f"{desc}",
                       id="hover_description"),
            ],
                className='map_hover_box')
        ]
        return True, bbox, children


@app.callback(
    Output('map_modal', 'style'),
    Output("map_modal", "children"),
    # Output("modal_close_button", "style"),
    [Input('map', 'clickData')])
def show_modal(click_data):
    if click_data == None:
        return {"display": "none"}, None  # , {"display": "none"}
    else:

        pt = click_data["points"][0]
        bbox = pt["bbox"]
        num = pt["pointNumber"]

        data_row = data.iloc[num]
        img_src = data_row['Image Name']
        name = data_row['Project Name']
        link = data_row['Project Link']
        ext_link_id = "link_available"
        if pd.isna(link):
            link = None
            ext_link_id = "link_unavailable"
        title_sz = 250 / len(name)
        lat = round(data_row['Project Latitude'], 2)
        long = round(data_row['Project Longitude'], 2)
        proj_type = is_retrofit(data_row['Project Built Year'], data_row['Project Plant Year'])
        build_type = data_row['Project Function']
        year = data_row['Project Plant Year'].astype(int)
        desc = data_row['Project Description']

        if img_src is np.nan:
            image_path = r'assets/images/placeholder.jpg'
            image_text = "image unavailable"
        else:
            image_path = f'assets/images/{img_src}.jpg'
            if img_src == "placeholder":
                image_text = "image unavailable"
            else:
                image_text = ""  # data_row['Project Link']

        im = Image.open(image_path)
        buffer = io.BytesIO()
        im.save(buffer, format="jpeg")
        encoded_image = base64.b64encode(buffer.getvalue()).decode()
        img_src = "data:image/jpeg;base64, " + encoded_image

        # for the table in the modal
        proj_cols = ["Project Country",
                     # "Project Description",
                     "Project Type",
                     "Project Function",
                     "Project Built Year",
                     "Project Plant Year"]  # if same as Project Built Year, select one and rename to Project Year

        sys_cols = ["System Type",
                    "System Building Element",  # (s) # if multiple in the system then list here "Roof, Facade, Louvre"
                    "System Rating",
                    "System Coverage",
                    "System Generation",
                    "System Specific Yield"]

        arr_cols = ["Array Orientation(s)",  # (if not empty but non numeric, write in list (SW,NE,ROOF)
                    "Array Surface(s)",
                    "Array Tilt(s)",
                    "Module Transparency",
                    "Module Cell Type(s)"]  # rename "Module Cell Type(s)": "Cell Type"

        children = [
            html.Div(children=[
                html.Div(name,
                        id="modal_name",
                        # style={"font-size": f"clamp({int(title_sz * 0.75)}px,{int(title_sz * 1.5)}px,25px"}
                        ),
                html.Div("",
                         id='modal_close_button',
                         className="close",
                         n_clicks=0)
            ],
                id='map_modal_top',
                className="map_modal_container",
            ),
            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.Img(src=img_src,
                                     id="map_modal_image"
                                     ),
                            html.P(image_text,
                                   id="map_modal_image_text"),
                        ],
                        id="map_modal_image_container"),
                    html.Div(
                        children=[
                            db_map.map_table(data_row,
                                             arr_cols,
                                             "Array Details",
                                             [proj_cols, sys_cols, arr_cols],
                                             div_id=""),

                        ],
                        id="map_modal_body", )
                ],
                id="map_modal_middle",
                className="map_modal_container"
            ),
            html.Div(children=[
                html.Div(html.A("More info",
                       href=link,
                       target="_blank",
                       id=ext_link_id,
                       className="external_link"),id="more_info")
            ],
                id='map_modal_bottom',
                className="map_modal_container",
            ),
        ]
        return {"display": "block"}, children


# Close modal
@app.callback(Output('map', 'clickData'),
              [Input('modal_close_button', 'n_clicks')])
def close_modal(n):
    return None


# rebuild the popovers for the nav bar to show legends
@app.callback(Output('hidden_div', 'style'),
              [Input('Map_button', 'n_clicks'),
               Input('Map_button', 'id')])
def update_popover(n, id):
    create_menu_row("Map")
    return {"display": "none"}


# clear the open popover when a new page is opened
# @app.callback(Output('hidden_div', 'style'),
#               [Input('Map_button', 'n_clicks'),
#                Input('Map_button', 'id')])
# def update_popover(n,id):
#     create_menu_row("Map")
#     return {"display": "none"}

if __name__ == '__main__':
    app.run_server(
        debug=True)
