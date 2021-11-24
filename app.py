from dash import dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import db_map
import dash_bootstrap_components as dbc

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(
    __name__,
    assets_folder = 'assets',
    external_stylesheets=external_stylesheets
    )

server = app.server

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

# layout = dbc.Container([
#     dbc.Row([
#         dbc.Col([
#             dbc.Nav(
#                 create_nav_items(),
#                 vertical=False,id='nav_bar'),
#                 ],width=3,id='nav_col'),
#         ######## break to body
#         dbc.Col(
#             html.Div(id='body_col_child'),
#             width=12,id='body_col'),
#     ],id='main_row'),
#     dbc.Row([
#         dbc.Col(html.Div(id='page-content'),width=12,id='footer')
#         ],id='footer_row')
# ],id='page')

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Nav(
                create_nav_items(),
                vertical=False,id='nav_bar'),
                ],width=3,id='nav_col'),
        ######## break to body
        dbc.Col(
            html.Div(id='body_col_child'),
            width=12,id='body_col'),
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
        figure=db_map.generate_bipv_db_map('assets/database_records.csv'),
        responsive=True,id='map'),
    # html.H2('Map goes here',className='test_h')
],className='content_container')

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

if __name__ == '__main__':
    app.run_server(
        debug=True)

