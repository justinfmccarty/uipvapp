import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
from utils import get_color_dict as colors
from utils import is_retrofit



def make_projects_by_year(data):
    plot_data = data[['Project Built Year', 'Project Plant Year']].dropna().copy()
    plot_data['Project Type'] = plot_data.apply(lambda x: is_retrofit(x['Project Built Year'], x['Project Plant Year']),
                                                axis=1)
    new_build_data = plot_data[plot_data['Project Type'] == 'New Build']['Project Plant Year'].astype(int)
    retrofit_data = plot_data[plot_data['Project Type'] == 'Retrofit']['Project Plant Year'].astype(int)

    years = np.arange(plot_data['Project Plant Year'].min(), time.localtime().tm_year)

    years_df = pd.DataFrame(pd.Series(years).astype(int).rename('index'))
    new = new_build_data.value_counts().reset_index().set_index('index').rename(
        columns={'Project Plant Year': 'newbuild'})
    retro = retrofit_data.value_counts().reset_index().set_index('index').rename(
        columns={'Project Plant Year': 'retrofit'})

    years_df = years_df.set_index('index').join(new)
    years_df = years_df.join(retro).fillna(0)
    years_df = years_df.astype(int)

    years = years_df.index.tolist()
    newbuild = years_df.newbuild.tolist()
    retro = years_df.retrofit.tolist()

    fig = go.Figure(data=[
        go.Bar(name='New Construction', x=years, y=newbuild,
               marker_color= colors()['new_cat']),
        go.Bar(name='Retrofit', x=years, y=retro,
               marker_color= colors()['retrofit_cat'])
    ])

    fig.update_layout(
        barmode='stack',
        title={"text": "BIPV Projects by Year and Type",
               'y': 0.9,
               'x': 0.5,
               'xanchor': 'center',
               'yanchor': 'top'},
        xaxis_title="Year",
        yaxis_title="Project Count",
        legend_title="Legend Title",
        font=dict(
            family="Urbanist",
            size=12,
            color= colors()['black']
        )
    )
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.98,
        xanchor="left",
        x=0.01
    ))

    return fig

def make_projects_by_generation_capacity(data):

    plot_data = data.copy()
    plot_data['Project Type'] = plot_data.apply(lambda x: is_retrofit(x['Project Built Year'], x['Project Plant Year']),
                                                axis=1)
    plot_data.dropna(subset=['Project Function', 'System Rating', 'System Specific Yield'], inplace=True)
    plot_data['System Specific Yield'] = plot_data['System Specific Yield'].astype(float)
    plot_data = plot_data[plot_data['System Specific Yield'] != 0]
    plot_data['System Generation Measured'].fillna(0, inplace=True)
    plot_data['System Generation Simulated'].fillna(0, inplace=True)
    plot_data['System Generation'] = plot_data[
        ['System Generation Measured', 'System Generation Simulated']].values.max(1)

    new = plot_data[plot_data['Project Type'] == 'New Build']
    retro = plot_data[plot_data['Project Type'] == 'Retrofit']

    x_new = new['System Rating']
    y_new = new['System Generation']

    x_retro = retro['System Rating']
    y_retro = retro['System Generation']

    fig = go.Figure(data=[
        go.Scatter(name='New Build', x=x_new, y=y_new, mode='markers',
                   marker_color= colors()['new_cat']),
        go.Scatter(name='Retrofit', x=x_retro, y=y_retro, mode='markers',
                   marker_color= colors()['retrofit_cat'])])

    fig.update_layout(
        title={"text": "BIPV Projects by Generation and Capacity",
               'y': 0.9,
               'x': 0.5,
               'xanchor': 'center',
               'yanchor': 'top'},
        xaxis_title="System Capacity (kW)",
        yaxis_title="Annual Generation (kWh/year)",
        legend_title="Legend Title",
        font=dict(
            family="Urbanist",
            size=12,
            color= colors()['black']
        )
    )
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.98,
        xanchor="left",
        x=0.01
    ))
    return fig