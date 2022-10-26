import base64
import io
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from PIL import Image
from dash import dash, html, dcc, Input, Output, State, no_update
import db_map
import db_overview
import utils
from utils import is_retrofit

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(
    __name__,
    assets_folder='assets',
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets
)

server = app.server
about_file = open('assets/about_description.txt', 'r')


def generate_dataframe(cols=None):
    data = pd.read_csv('assets/database_display.csv',
                       index_col="Unnamed: 0",
                       usecols=cols)
    return data


data_intitial = generate_dataframe()
filter_fields = ['Project Built Year',
                 'Project Function Clean',
                 'System Type Clean',
                 'Simple System Building Element',
                 'System Coverage',
                 'System Specific Yield Calculated',
                 'System Generation',
                 'Array Orientation(s) Clean',
                 'Module Cell Type(s)',
                 'Module Transparency',
                 'Project Description']


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


def create_nav_row(menu_item_name):
    popover_child_hover = get_popover_children_hover()[menu_item_name]
    # popover_child_click = get_popover_children_click()[menu_item_name]
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

        # dbc.Popover(popover_child_click,
        #             hide_arrow=True,
        #             id=f"{menu_item_name}_click",
        #             target=f"{menu_item_name}_link",
        #             is_open=False,
        #             )
    ]
    return main_div


def create_nav_items():
    out_items = []
    for menu_item in get_menu_items():
        out_items.append(create_nav_row(menu_item))
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
    dcc.Store(data=data_intitial.to_dict(),
              id='dataframe_init'),
    dcc.Store(data=None,
              id='dataframe_temp'),
    # html.Div(children=[
    #         dash_table.DataTable(
    #             id='memory-table',
    #             columns=[{'name': i, 'id': i} for i in data_intitial.columns if "Project" in i]
    #         ),
    #     ]),
    html.Div(children=[
        db_map.legend_table_sizes(),
        db_map.legend_table_colors(),
    ],
        id="map_legend_container",
        className="map_overlay"
    ),
    db_map.create_filter_container(filter_fields,
                                   data_intitial),
    dcc.Graph(
        id='map',
        figure=db_map.generate_bipv_db_map_2(data_intitial),
        responsive=True,
        # animate=True,
        clear_on_unhover=True,
        config={"displayModeBar": False}),
    dcc.Tooltip(
        id="graph_tooltip",
        loading_text="Loading..."),
    html.Div(children=[db_map.map_modal()
                       ]
             ),
], className='content_container')

layout_overview_page = html.Div(children=[
    dcc.Store(data=data_intitial.to_dict(),
              id='dataframe_init'),
    dcc.Dropdown(['Year and Type',
                  'Generation and Capacity',
                  'Surface Area and Yield',
                  'Surface Type'],
                 'Year and Type',
                 id='graph_selector'),
    html.Div(children=[
        #         dcc.Graph(
        #             figure=db_overview.make_projects_by_year(data_intitial),
        #             responsive=True,
        #             clear_on_unhover=True),
        #     ], className='overview_graphs'),
        #     html.Div([
        #         dcc.Graph(
        #             figure=db_overview.make_projects_by_generation_capacity(data_intitial),
        #             responsive=True,
        #             clear_on_unhover=True),
    ], id='overview_graphs_target',
        className='overview_graph_box'),
],
    className='overview_container')

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


@app.callback(Output('overview_graphs_target', 'children'),
              Input('graph_selector', 'value'),
              Input('dataframe_init', 'data'))
def update_overview_graph(option, data_store):
    data = generate_dataframe()  # pd.DataFrame.from_dict(data_store)
    if option == 'Year and Type':
        fig = db_overview.make_projects_by_year(data)
    elif option == 'Generation and Capacity':
        fig = db_overview.make_projects_by_generation_capacity(data)
    elif option == 'Surface Area and Yield':
        fig = db_overview.make_projects_by_coverage_yield(data)
    elif option == 'Surface Type':
        fig = db_overview.make_surface_type_plot(data)
    else:
        return html.H4("No Option")
    return dcc.Graph(
        figure=fig,
        responsive=True,
        clear_on_unhover=True)


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
    [Input("map", "hoverData"),
     State('dataframe_init', 'data')])
def display_hover(hover_data, data_store):
    if hover_data is None:
        return False, no_update, no_update
    else:
        # hover_cols = ['Unnamed: 0',
        #               'Image Name',
        #               'Project Name',
        #               'Project Latitude',
        #               'Project Longitude',
        #               'Project Built Year',
        #               'Project Plant Year',
        #               'Project Function',
        #               'Project Description']

        # df = generate_dataframe(cols=hover_cols)
        df = pd.DataFrame.from_dict(data_store)
        pt = hover_data["points"][0]
        bbox = pt["bbox"]

        hover_lat = hover_data["points"][0]['lat']
        hover_lon = hover_data["points"][0]['lon']
        match = df[df['Project Latitude'] == hover_lat]
        match = match[match['Project Longitude'] == hover_lon]
        data_row = match.reset_index(drop=True).iloc[0]

        img_src = data_row['Image Name']
        name = data_row['Project Name']
        title_sz = 250 / len(name)
        lat = round(data_row['Project Latitude'], 2)
        long = round(data_row['Project Longitude'], 2)
        proj_type = is_retrofit(data_row['Project Built Year'], data_row['Project Plant Year'])
        build_type = data_row['Project Function Clean']
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
        elif desc == None:
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
    [Input('map', 'clickData'),
     State('dataframe_init', 'data')])
def show_modal(click_data, data_store):
    if click_data == None:
        return {"display": "none"}, None  # , {"display": "none"}
    else:
        df = pd.DataFrame.from_dict(data_store)
        pt = click_data["points"][0]
        bbox = pt["bbox"]

        hover_lat = click_data["points"][0]['lat']
        hover_lon = click_data["points"][0]['lon']
        match = df[df['Project Latitude'] == hover_lat]
        match = match[match['Project Longitude'] == hover_lon]
        data_row = match.reset_index(drop=True).iloc[0]

        img_src = data_row['Image Name']
        name = data_row['Project Name']
        link = data_row['Project Link']
        ext_link_id = "link_available"
        if pd.isna(link):
            link = None
            ext_link_id = "link_unavailable"

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
                     "Project Function Clean",
                     "Project Built Year",
                     "Project Plant Year"]  # if same as Project Built Year, select one and rename to Project Year

        sys_cols = ["System Type Clean",
                    "Simple System Building Element",
                    # (s) # if multiple in the system then list here "Roof, Facade, Louvre"
                    "System Rating",
                    "System Coverage",
                    "System Generation",
                    "System Specific Yield"]

        arr_cols = ["Array Orientation(s) Clean",  # (if not empty but non numeric, write in list (SW,NE,ROOF)
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
                                className="external_link"), id="more_info")
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
    create_nav_row("Map")
    return {"display": "none"}


@app.callback(Output('map', 'figure'),
              Output('dataframe_temp', 'data'),
              [Input('filter_built_year', 'value'),
               Input('filter_project_function', 'value'),
               Input('filter_type', 'value'),
               Input('filter_elements', 'value'),
               Input('filter_coverage', 'value'),
               Input('filter_specific_yield', 'value'),
               Input('filter_generation', 'value'),
               Input('filter_orientation', 'value'),
               Input('filter_cell_types', 'value'),
               Input('filter_transparency', 'value'),
               Input('filter_input_description', 'value'),
               State('dataframe_init', 'data'),
               Input('map', 'relayoutData')])
def filter_data(date_range, functions, sys_type, elements, coverage,
                sp_yield, generation, orientation, cells, transparency,
                search_term,
                data, map_info):
    if map_info == None:
        df_init = generate_dataframe()
        map = db_map.generate_bipv_db_map_2(df_init)
        return map, df_init.to_dict()
    else:
        if len(map_info.keys()) == 1:
            autosize = True
            lat = 40
            lon = 145
            zoom = None
        else:
            autosize = False
            lat = map_info['mapbox.center']['lat']
            lon = map_info['mapbox.center']['lon']
            zoom = map_info['mapbox.zoom']
        # load dataframe from memory store
        df = pd.DataFrame.from_dict(data)

        # filtering
        df = utils.filter_df_list_mixed_type(df,  # filter plant year
                                             date_range,
                                             "Project Built Year",
                                             clip=(1945, None))
        df = utils.filter_df_list(df,
                                  functions,
                                  "Project Function Clean")
        df = utils.filter_df_list(df,
                                  sys_type,
                                  "System Type Clean")
        df = utils.filter_df_list(df,
                                  elements,
                                  "Simple System Building Element")
        df = utils.filter_df_range(df,
                                   coverage,
                                   "System Coverage")
        df = utils.filter_df_range(df,  # filter specific yield
                                   sp_yield,
                                   "System Specific Yield",
                                   new_dtype=float)
        df = utils.filter_df_range(df,  # filter generation
                                   generation,
                                   "System Generation",
                                   new_dtype=float)
        df = utils.filter_df_list_mixed_type(df,
                                             orientation,
                                             "Array Orientation(s) Clean")
        df = utils.filter_df_list(df,
                                  cells,
                                  "Module Cell Type(s)")
        # df = utils.filter_df_range(df,  # filter transparency
        #                            transparency,
        #                            "Module Transparency",
        #                            new_dtype=float)
        df = utils.search_string_field(df,
                                       'Project Description',
                                       'Unknown',
                                       search_term)
        # render map
        map = db_map.generate_bipv_db_map_2(df,
                                            lat=lat,
                                            lon=lon,
                                            autosize=autosize,
                                            zoom=zoom)
        return map, df.to_dict()  # important to change DF to a dict for the store


if __name__ == '__main__':
    app.run_server(
        debug=True)
    # be sure to change to False when deploy to master
