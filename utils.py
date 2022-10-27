from dash import html, dcc
from datetime import date
import pandas as pd
import numpy as np


def get_color_dict():
    k = ['highlight', 'retrofit_cat', 'new_cat', 'white', 'black',
         'colorbar_r4', 'colorbar_r3', 'colorbar_r2', 'colorbar_r1',
         'colorbar_b1', 'colorbar_b2', 'colorbar_b3', 'colorbar_b4']
    c = ["#e2c45e", "#6f462e", "#c2cb7e", "#e9ede9", "#1c221c", "#da381f", "#ee6a35", "#fbac6d",
         "#edd5a9", "#81a8a0", "#238695", "#1a698a", "#062551"]
    return dict(zip(k, c))


def is_retrofit(built_year, plant_year):
    if plant_year == built_year:
        return 'New Build'
    else:
        return 'Retrofit'


def choose_colors(project_type):
    if project_type == 'Retrofit':
        return get_color_dict()['retrofit_cat']
    else:
        return get_color_dict()['new_cat']


def generate_table():
    return html.Table(
        # Body
        [html.Tr([
            html.Td("Type:"),
            html.Td("Retrofit")]),
            html.Tr([
                html.Td("Use:"),
                html.Td("REsidential")]),
            html.Tr([
                html.Td("Year:"),
                html.Td("2003")]),
            html.Tr([
                html.Td("Source:"),
                html.Td("EURAC")]),
            html.Tr([
                html.Td("Yield"),
                html.Td("500 kWh/kwp")])])


def flatten(l):
    return [item for sublist in l for item in sublist]


def add_date_picker(min_year, id_name, marks=True):
    min_year = int(min_year)
    max_year = int(date.today().year)
    if marks == True:
        slider = dcc.RangeSlider(min=min_year,
                                 max=max_year,
                                 step=1,
                                 marks={1945: {'label': '<=1945',
                                               # 'style': {'font-size': '5px'}
                                               },
                                        1970: {'label': '1970',
                                               # 'style': {'font-size': '5px'}
                                               },
                                        1995: {'label': '1995',
                                               # 'style': {'font-size': '5px'}
                                               },
                                        # 2020: '2020',
                                        max_year: {'label': f'{max_year}',
                                                   # 'style': {'font-size': '5px'}
                                                   }
                                        },
                                 value=[min_year, date.today().year],
                                 tooltip={"placement": "bottom",
                                          "always_visible": False},
                                 allowCross=True,
                                 id=id_name,
                                 className="range_slider_container")
    else:
        slider = dcc.RangeSlider(min=min_year,
                                 max=max_year,
                                 step=1,
                                 marks=None,
                                 value=[min_year, date.today().year],
                                 allowCross=True,
                                 id=id_name,
                                 className="range_slider_container")
    return slider


def add_range_slider(min, max, id_name, marks=True):
    if marks == True:
        mid = (max - min) / 2
        slider = dcc.RangeSlider(min=min,
                                 max=max,
                                 step=1,
                                 marks={min: {'label': str(min),
                                              # 'style': {'font-size': '5px'}
                                              },
                                        mid: {'label': str(mid),
                                              # 'style': {'font-size': '5px'}
                                              },
                                        max: {'label': str(max),
                                              # 'style': {'font-size': '5px'}
                                              }
                                        },
                                 value=[min, max],
                                 tooltip={"placement": "bottom",
                                          "always_visible": False},
                                 allowCross=True,
                                 id=id_name,
                                 className="range_slider_container")
    else:
        slider = dcc.RangeSlider(min=min,
                                 max=max,
                                 step=1,
                                 marks=None,
                                 value=[min, max],
                                 allowCross=True,
                                 id=id_name,
                                 className="range_slider_container")
    return slider


def add_compass_slider(id_name):
    slider = dcc.RangeSlider(min=0,
                             max=360,
                             step=1,
                             marks={0: {'label': 'North',
                                        # 'style': {'font-size': '5px'}
                                        },
                                    90: {'label': 'East',
                                         # 'style': {'font-size': '5px'}
                                         },
                                    180: {'label': 'South',
                                          # 'style': {'font-size': '5px'}
                                          },
                                    270: {'label': 'West',
                                          # 'style': {'font-size': '5px'}
                                          },
                                    360: {'label': 'North',
                                          # 'style': {'font-size': '5px'}
                                          }
                                    },
                             value=[0, 360],
                             tooltip={"placement": "bottom",
                                      "always_visible": False},
                             allowCross=True,
                             id=id_name.replace(' ', '_'),
                             className="range_slider_container")
    return slider


def filter_df_range(df, range, col, new_dtype=int):
    df[col] = df[col].astype(new_dtype)
    return df[df[col].between(range[0], range[1])]


def add_checklist(df, col, id_name):
    option_list = df[col].unique().tolist()
    drop = dcc.Checklist(
        options=option_list,
        value=option_list,
        # placeholder=col,
        # multi=True,
        # optionHeight=10,
        # searchable=True,
        # inline=True,
        id=id_name,
        className="filter_checklist",
        labelClassName='checklist_label',
        inputClassName="checkbox"
    )
    return drop


def add_dropdown(df, col, id_name):
    option_list = df[col].unique().tolist()
    drop = dcc.Dropdown(
        options=option_list,
        value=option_list,
        multi=True,
        placeholder=col,
        optionHeight=10,
        searchable=True,
        id=f"{id_name.replace(' ', '_')}_dropdown",
        className="filter_dropdown",
    )
    return drop


def add_filter_input(id_name):
    input = html.Div(dcc.Input(
        id=id_name,
        type='search',
        placeholder='Search...',
        className="filter_input"), className='filter_input_cont')
    return input


def filter_df_list(df, elements, col):
    return df[df[col].isin(elements)]


def filter_df_list_mixed_type(df, range, col, clip=None):
    # # print(range)
    # string_df = df[~df[col].astype(str).str.isnumeric()].copy()
    # # print(len(string_df))
    # num_df = df[df[col].astype(str).str.isnumeric()].copy()

    def check_dig(s):
        return str(s).replace('.', '', 1).isdigit()

    string_df = df[~df.apply(lambda x: check_dig(x[col]), axis=1)].copy()
    num_df = df[df.apply(lambda x: check_dig(x[col]), axis=1)].copy()

    if clip == None:
        num_df = filter_df_range(num_df, range, col, new_dtype=int)
    else:
        clipped = pd.Series(np.clip(num_df[col].astype(float),
                                    clip[0],
                                    clip[1]))
        num_df = num_df[clipped.between(range[0], range[1])]
    out_df = pd.concat([string_df,
                        num_df])
    return out_df


def map_dict_names(map_dict, key):
    if key in map_dict.keys():
        return map_dict[key]
    else:
        return key


def search_string_field(df, col, missing, search_term):
    if search_term == None:
        return df
    else:
        na_df = df[df[col] == missing]
        desc_df = df[df[col] != missing]
        out_df = pd.concat([na_df,
                            desc_df[desc_df[col].str.contains(search_term)]])
        return out_df
