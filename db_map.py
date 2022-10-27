import itertools
import os
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import html

import utils

mapbox_access_token = os.getenv('UIPV_APP_MAPBOX_KEY')
# secret_file = os.path.join('secrets', 'mapbox_token.txt')
# with open(secret_file, "r") as fp:
#     mapbox_access_token = fp.readlines()[0]

# head_file = os.path.join('.git', 'HEAD')
# with open(head_file, "r") as fp:
#     branch = fp.readlines()[0]
# if "master" in branch:
#     mapbox_access_token = os.getenv('MAPBOX_KEY')
# else:
#     secret_file = os.path.join('secrets', 'mapbox_token.txt')
#     with open(secret_file, "r") as fp:
#         mapbox_access_token = fp.readlines()[0]
# def generate_bipv_db_map(data):
#     plot_data = data.copy()
#     plot_data['Project Type'] = plot_data.apply(lambda x: is_retrofit(x['Project Built Year'],
#                                                                       x['Project Plant Year']),
#                                                 axis=1)
#
#     plot_data['Color'] = plot_data.apply(lambda x: choose_colors(x['Project Type']),
#                                          axis=1)
#
#     fig = go.Figure(
#         go.Scattermapbox(
#             lat=plot_data['Project Latitude'],
#             lon=plot_data['Project Longitude'],
#             mode='markers',
#             marker=go.scattermapbox.Marker(
#                 size=12,
#                 color=plot_data['Color'],
#                 opacity=0.5,
#             ),
#             hoverinfo='none',
#         ),
#     )
#
#     fig.update_layout(
#         autosize=True,
#         margin=dict(l=0, r=0, t=0, b=0),
#         hovermode='closest',
#         mapbox=dict(
#             accesstoken=mapbox_access_token,
#             bearing=0,
#             center=dict(
#                 lat=40,
#                 lon=145
#             ),
#             pitch=0
#         ),
#     )
#
#     return fig


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
        df.drop(labels=['Project Plant Year'], inplace=True)
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

    return html.Table(utils.flatten(set), id=div_id,
                      className="map_modal_table")


def generate_sub_table(label, size):
    content = html.Div(children=[
        html.Div(id=f"legend_size_{size}",
                 className="legend_sizes_symbol"),
        html.Div(label,
                 className="legend_sizes_text"),
    ],
        className="legend_sizes_col_cont"
    )
    return content


def legend_table_sizes():
    content = [generate_sub_table("<=5kW", "5"),
               generate_sub_table("5-20kW", "20"),
               generate_sub_table("20-100kW", "100"),
               generate_sub_table(">=100kW", "100plus")]

    return html.Div(content, id="legend_sizes_cont")


def legend_table_colors():
    content = [html.Div([html.Div(id="legend_retrofit",
                                  className="legend_colors"),
                         html.Div("Retrofit",
                                  className="legend_colors_text")],
                        id="legend_colors_row_retrofit",
                        className="legend_colors_row"),
               html.Div([html.Div(id="legend_new",
                                  className="legend_colors"),
                         html.Div("New Construction",
                                  className="legend_colors_text")],
                        id="legend_colors_row_new",
                        className="legend_colors_row")
               ]
    return html.Div(content, id="legend_colors_cont")


def split_dataframe(df):
    sizes = df['Map Sizes'].unique().tolist()
    shapes = df['Map Symbols2'].unique().tolist()
    colors = df['Map Colors'].unique().tolist()

    combs = list(itertools.product(*[sizes, shapes, colors]))
    df_list = []
    for comb in combs:
        sub_df = df[df['Map Sizes'] == comb[0]]
        sub_df = sub_df[sub_df['Map Symbols2'] == comb[1]]
        sub_df = sub_df[sub_df['Map Colors'] == comb[2]]
        df_list.append(sub_df)

    return df_list


def generate_bipv_db_map_2(data, lat=40, lon=145, autosize=True, zoom=None):
    plot_data = data.copy()

    fig = go.Figure(
        go.Scattermapbox(
            lat=plot_data['Project Latitude'],
            lon=plot_data['Project Longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                # symbol=plot_data['Map Symbols'],
                size=plot_data['Map Sizes'],
                color=plot_data['Map Colors'],
                allowoverlap=True,
                opacity=0.5,
            ),
            hoverinfo='none',
        ),
    )

    # fig = go.Figure()
    # for df_group in split_dataframe(plot_data):
    #     fig.add_trace(
    #         go.Scattermapbox(
    #             lat=df_group['Project Latitude'],
    #             lon=df_group['Project Longitude'],
    #             # customdata=my_gr['value'],
    #             # hovertemplate='<b>Value</b>: %{customdata}',
    #             # name=shape,
    #             mode='markers',
    #             marker=go.scattermapbox.Marker(
    #                 # symbol=df_group['Map Symbols2'],
    #                 size=df_group['Map Sizes'],
    #                 color=df_group['Map Colors'],
    #                 allowoverlap=True,
    #                 opacity=0.5,
    #             ),
    #         )
    #     )

    fig.update_layout(
        autosize=autosize,
        margin=dict(l=0, r=0, t=0, b=0),
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=lat,
                lon=lon
            ),
            zoom=zoom,
            pitch=0
        ),
    )

    # fig.update_layout(showlegend=True,
    #                   legend=dict(bordercolor='rgb(100,100,100)',
    #                               borderwidth=2,
    #                               yanchor="top",
    #                               y=0.5,
    #                               xanchor="left",
    #                               x=0.5))

    return fig


def change_filter_name(og_name):
    if og_name == 'Project Built Year':
        return 'Built Year'
    elif og_name == 'Project Function Clean':
        return 'Project Function'
    elif og_name == 'System Type Clean':
        return 'System Type'
    elif og_name == 'Simple System Building Element':
        return 'Surface Element'
    elif og_name == 'System Coverage':
        return og_name
    elif og_name == 'System Specific Yield Calculated':
        return 'Specific Yield'
    elif og_name == 'System Generation':
        return og_name
    elif og_name == 'Array Orientation(s) Clean':
        return 'Orientation'
    elif og_name == 'Module Cell Type(s)':
        return 'Cell Type'
    elif og_name == 'Module Transparency':
        return 'Transparency'
    elif og_name == 'Project Description':
        return 'Search Text'
    else:
        return og_name


def create_filter_button(filter_field):
    filter_name = change_filter_name(filter_field)
    child = html.Div(filter_name,
                     className='filter_button_label')
    return html.Div(child,
                    n_clicks=0,
                    id=f"{filter_field.replace(' ', '_')}_button_target",
                    className='filter_button')


def create_filter_button_container(filters):
    main_div = html.Div(
        children=[create_filter_button(f) for f in filters],  # filter_buttons,
        id="filter_button_container",
        # className="map_overlay"
    )
    return main_div


def create_filter_popovers(filter_field, data_intitial):
    # popover_content = utils.add_date_picker(1945,
    #                                         "filter_built_year",
    #                                         marks=True)
    click_content, hover_content = choose_popover_content(filter_field, data_intitial)
    popover_click = dbc.Popover(html.Div(click_content,
                                         id=f"filter_{filter_field.replace(' ', '_')}",
                                         className='filter_click_content'),
                                id=f"{filter_field.replace(' ', '_')}_hover",
                                class_name='filter_click_container',
                                inner_class_name='filter_click_content',
                                target=f"{filter_field.replace(' ', '_')}_button_target",
                                placement="top",
                                hide_arrow=True,
                                trigger="click")

    popover_hover = dbc.Popover(html.Div(hover_content,
                                         id=f"filter_{filter_field.replace(' ', '_')}",
                                         className='filter_hover_content'),
                                id=f"{filter_field.replace(' ', '_')}_hover",
                                class_name='filter_hover_container',
                                inner_class_name='filter_hover_content',
                                target=f"{filter_field.replace(' ', '_')}_button_target",
                                placement="top",
                                hide_arrow=True,
                                trigger="hover")
    return [popover_click, popover_hover]


def create_filter_popover_container(filters, data_intitial):
    main_div = html.Div(
        children=utils.flatten([create_filter_popovers(f, data_intitial) for f in filters]),  # filter_buttons,
        id="filter_popovers_container",
        # className="map_overlay"
    )
    return main_div


def create_filter_container(filters, data_intitial):
    buttons = create_filter_button_container(filters)
    popovers = create_filter_popover_container(filters, data_intitial)
    return html.Div(
        children=[
            buttons,
            popovers
            # "Hello World"
        ],
        id='filter_container'
    )


def choose_popover_content(filter_field, data_intitial):
    filter_name = change_filter_name(filter_field)
    if filter_field == 'Project Built Year':
        click_content = utils.add_date_picker(1945,
                                              "filter_built_year",
                                              marks=True)
        hover_content = html.Div(f"Click '{filter_name}' and use the slider"
                                 f" to select a date range for the project's"
                                 f" date of construction.",
                                 className='filter_hover_content')

    elif filter_field == 'Project Function Clean':
        click_content = utils.add_checklist(data_intitial,
                                            'Project Function Clean',
                                            "filter_project_function")
        hover_content = html.Div(f"Click '{filter_name}' and use the checklist"
                                 f" to select which types of programmes you"
                                 f" would like to see on the map.",
                                 className='filter_hover_content')

    elif filter_field == 'System Type Clean':
        click_content = utils.add_checklist(data_intitial,
                                            'System Type Clean',
                                            "filter_type")
        hover_content = html.Div(f"Click '{filter_name}' and use the checklist"
                                 f" to select which types of projects (integrated"
                                 f" or attached) you would like to see on the map.",
                                 className='filter_hover_content')

    elif filter_field == 'Simple System Building Element':
        click_content = utils.add_checklist(data_intitial,
                                            'Simple System Building Element',
                                            "filter_elements")
        hover_content = html.Div(f"Click '{filter_name}' and use the checklist"
                                 f" to select which types of surface integrations you"
                                 f" would like to see on the map.",
                                 className='filter_hover_content')

    elif filter_field == 'System Coverage':
        click_content = utils.add_range_slider(0,
                                               data_intitial['System Coverage'].max(),
                                               "filter_coverage",
                                               marks=True)
        hover_content = html.Div(f"Click '{filter_name}' and use the slider"
                                 f" to select a range of surface coverage (sqm.)"
                                 f" to filter the projects on the map.",
                                 className='filter_hover_content')

    elif filter_field == 'System Specific Yield Calculated':
        click_content = utils.add_range_slider(0,
                                               data_intitial['System Specific Yield'].max(),
                                               "filter_specific_yield",
                                               marks=True)
        hover_content = html.Div(f"Click '{filter_name}' and use the slider"
                                 f" to select a range of specific yield "
                                 f" (annual kWh/total kW) to filter the "
                                 f" projects on the map.",
                                 className='filter_hover_content')

    elif filter_field == 'System Generation':
        click_content = utils.add_range_slider(0,
                                               data_intitial['System Generation'].max(),
                                               "filter_generation",
                                               marks=True)
        hover_content = html.Div(f"Click '{filter_name}' and use the slider"
                                 f" to select a range of annual generation to"
                                 f" filter the projects on the map.",
                                 className='filter_hover_content')

    elif filter_field == 'Array Orientation(s) Clean':
        click_content = utils.add_compass_slider("filter_orientation")
        hover_content = html.Div(f"Click '{filter_name}' and use the slider"
                                 f" to select a range of orientation angles"
                                 f" to filter the projects on the map. Roof"
                                 f" and mixed systems will not be filtered.",
                                 className='filter_hover_content')

    elif filter_field == 'Module Cell Type(s)':
        click_content = utils.add_checklist(data_intitial,
                                            'Module Cell Type(s)',
                                            "filter_cell_types")
        hover_content = html.Div(f"Click '{filter_name}' and use the checklist"
                                 f" to select which types of solar cells"
                                 f" would like to see on the map.",
                                 className='filter_hover_content')

    elif filter_field == 'Module Transparency':
        click_content = utils.add_range_slider(0,
                                               100,
                                               "filter_transparency",
                                               marks=True)
        hover_content = html.Div(f"Click '{filter_name}' and use the slider"
                                 f" to select a range of transparency values "
                                 f" to filter the projects on the map.",
                                 className='filter_hover_content')

    elif filter_field == 'Project Description':
        click_content = utils.add_filter_input('filter_input_description')
        hover_content = html.Div(f"Click '{filter_name}' and input some text"
                                 f" to search the project descriptions and titles."
                                 f" The search is currently simple looks to match"
                                 f" single words, phrases, and partial words.",
                                 className='filter_hover_content')

    else:
        click_content = html.P('This filter has not been setup.')
        hover_content = html.Div("", className='filter_hover_content')

    return click_content, hover_content
