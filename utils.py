from dash import html


def get_color_dict():
    k = ['highlight','retrofit_cat','new_cat','white','black',
         'colorbar_r4','colorbar_r3','colorbar_r2','colorbar_r1',
         'colorbar_b1','colorbar_b2','colorbar_b3','colorbar_b4']
    c = ["#e2c45e","#6f462e","#c2cb7e","#e9ede9","#1c221c","#da381f","#ee6a35","#fbac6d",
         "#edd5a9","#81a8a0","#238695","#1a698a","#062551"]
    return dict(zip(k,c))



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