# This file contains all the necessary functions and variables used in "app.py".
# they are left here to ease the development and to let the "app.py" file focus only on the app itself

# importing necessary dependencies
from dash import dcc, html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json


# read the data into a pandas dataframe.
df = pd.read_csv("rolling_works.csv")
df['month_year'] = pd.to_datetime(df['month_year'])

# configuration for plotly charts
config = {'displaylogo': False,
         'modeBarButtonsToAdd':['drawline',
                                'drawopenpath',
                                'drawclosedpath',
                                'drawcircle',
                                'drawrect',
                                'eraseshape'
                               ]}


# The following 3 functions are for the slider values
def make_main_dict():
    main_dict = dict()
    counter = 0
    for i in df['month_year'].unique():
        main_dict[counter] = pd.to_datetime(i).strftime("%Y-%m")

        counter += 1
    return main_dict


main_dict = make_main_dict()
def make_main_dict_short():
    main_dict_short = dict()
    for i in main_dict:
        if main_dict[i][5:7] == "01":
            main_dict_short[i] = main_dict[i][0:4]
        else:
            main_dict_short[i] = main_dict[i][5:7]
    return main_dict_short


main_dict_short = make_main_dict_short()


def make_main_dict_step(steps):
    counter = 0
    main_dict_step = dict()
    for i in main_dict_short:
        if counter % (steps + 1) == 0:
            main_dict_step[i] = main_dict_short[i]
        counter += 1
    return main_dict_step

main_dict_step = make_main_dict_step(1)







def blank_fig():
    """this function returns an empty plotly chart
        it is necessary to avoid the appearance of the base figure of dcc.Graph while the callback is loading"""
    fig = go.Figure(go.Scatter(x=[], y = []))
    fig.update_layout(template = None,
                     plot_bgcolor="rgba(0,0,0, 0)",
                     paper_bgcolor="rgba(0,0,0, 0)",)
    fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)

    return fig



def make_dropdown(rank_order):
    """this function makes the dropdown used in the tables.
       it takes 1 argument "rank_order", which is a number which will determine the id of the dropdown
       for example: rank_order = 1 will result in a dropdown with an id == "dropdown1" """
    layout = dcc.Dropdown(id=f'dropdown{rank_order}',
                options=[
                    {'label':x, 'value':x} for x in df.sort_values('Region')['Region'].unique()
                ],
                multi = True,
                clearable = False,
                searchable = False,
                value = df['Region'].unique())
    #returns the layout of the dropdown
    return layout


def make_slider(rank_order):
    """This functions makes the slider used in all the tables and the line chart.
        it takes the same argument as the dropdown."""
    layout = dcc.RangeSlider(
                id=f'slider{rank_order}',
                min = 0,
                max = len(df['month_year'].unique()) - 1,
                value = [0, len(df['month_year'].unique()) - 1],
                marks= main_dict_step,
                step = 1,
                dots = True,
                className = "slider"
                    )

    #returns the layout of the slider
    return layout


def make_table_layout(title, rank_order):
    """This functions makes the layout of the table
        it takes 2 arguments: "title" and "rank_order". 
        title will appear at the top of the table container as 'Gender' or 'Age'.
        while "rank_order" behaves the same way as the slider and dropdown functions.
        here the "rank_order" argument will control all the ids in the whole layout of the table section"""
    layout = html.Div([
    html.Div([
        html.Div([
                html.P(title)
            ], className = "title-section"),
        html.Div([
            html.Div([
                make_dropdown(rank_order)
            ], className = "dropdown-box"),
            html.Div([
                html.Button("Chart view",
                n_clicks = 0,
                style = {
                    "height": "auto",
                    "padding": "12px",
                    "width": "50%",
                    "background-color": "#e79e1e",
                    "border-radius": "5px",
                    "border": "0px",
                    "color": "white",
                    "text-shadow": "0 0.075em 0.075em rgb(0 0 0 / 50%)",
                    "font-size": "16px"
                },
                id = f"button{rank_order}",
                className = "button")
            ],
            className = "button-box")

        ], className = "dropdown-and-button"),

        html.Div([
            make_slider(rank_order)
        ], className = "slider-box")
    ], className = "control-section"),
    html.Div([

    ], className = "content-section", 
    id = f"table{rank_order}")])

    # returns the layout of the table section
    return layout




def make_map(date_range):
    """This function makes the choropleth map.
        takes no arguments and isn't connected to any callbacks"""
    dff = df[(df["month_year"] >= pd.to_datetime(main_dict[date_range[0]])) & (df['month_year'] <= pd.to_datetime(main_dict[date_range[1]]))]
    dff = dff[['month_year', 'Region', 'age_banding',]]
    dff = dff.groupby(['month_year', 'Region'], as_index = False).count()
    dff = dff.rename(columns = {"age_banding": "count"})
    dff = dff.sort_values('month_year')
    dff['month_year'] = pd.DatetimeIndex(dff['month_year']).strftime("%Y-%m")
    dff = dff.groupby('Region', as_index = False).sum()
    kuntaur = pd.DataFrame({'Region': ['Kuntaur'], 'count': [0]})
    all_extras = pd.DataFrame({'Region': [region for region in set(df['Region'].unique())-set(dff['Region'].unique())], 'count': [0]*len(set(df['Region'].unique())-set(dff['Region'].unique()))})
    dff = pd.concat([dff, kuntaur, all_extras], ignore_index=True)

    geojson = json.load(open('map (4).geojson', 'r'))

    fig = px.choropleth(dff, geojson=geojson, 
                        color="count",
                        locations="Region", 
                        featureidkey="properties.name_1",
                        color_continuous_scale = ["rgba(250, 250, 250, 0)", "#215285", "#214275", "#213265","#212255","#211245","#213235", 
                        "#213225", "#213225", "#213215", "#b95535", "#b95535","#b95535","#b95535","#b95535","#b95535","#b95535","#b95535", 
                        "#b95535","#b95535", "#b95535", "#e79e1e", ]
                    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_traces(
    marker_line_width=3
    )
    # returns a plotly.express.choropleth figure
    return fig
