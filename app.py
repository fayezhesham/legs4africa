# importing necessary dependencies
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, dash_table

# importing necessary functions and variables from the local file "functions.py"
from functions import make_table_layout, make_slider, blank_fig, make_map, main_dict, df, config



#initializing dash app
app = dash.Dash(__name__)
server = app.server
# set the app title
app.title = 'Legs4Africa | Dashboard'
# the app layout
app.layout = html.Div([
    html.Div([
        # the layout of the header of the dashboard
        html.Div([
            #The logo
            html.Div([
                html.Img(
                    src=app.get_asset_url("logo.png"), 
                    id="logo"),
            ], className = "logo-area"),
            #The second logo
            html.Div([
                html.Img(
                    src=app.get_asset_url("dsw_logo.png"), 
                    id="logo2"),
            ], className = "logo-area"),
            # The title
            html.Div([
                html.P("National Rehabilitation Centre Dashboard", id='title-text')
            ], className = "title-area")
        ], className = "top-section"),
        #The main section of the dashboard
        html.Div([
            # the first table 
            html.Div(
                # function "make_table_layout" from functions.py file
                make_table_layout(title = "Gender", rank_order ="1"),
            id = "table-area-1",
            className = "table-area"),
            #The second table
            html.Div(
                make_table_layout(title = "Age", rank_order = "2"),
             id = "table-area-2",
            className = "table-area"),
            # The third table
            html.Div(
                make_table_layout(title = "Work type", rank_order = "3"),
            id = "table-area-3", 
            className = "table-area"),
            #The forth table
            html.Div(
                make_table_layout(title = "Region", rank_order = "4"),
            id = "table-area-4",
            className = "table-area"),
            # The map
            html.Div([
                html.Div([
                    html.Div([
                        # function "make_slider" from functions.py file
                        make_slider(6),
                    ], className = 'slider-box')
                ], className = 'control-section'),
                html.Div([
                    #dcc graph component to contain the line chart
                    dcc.Graph(id = "map-chart", figure = blank_fig(), config = config)
                ], className = "content-section-2")
            ], className = "map-container"),
            #The line chart
            html.Div([
                html.Div([
                    html.Div([
                        # function "make_slider" from functions.py file
                        make_slider(5),
                    ], className = 'slider-box')
                ], className = 'control-section'),
                html.Div([
                    #dcc graph component to contain the line chart
                    dcc.Graph(id = "line-chart", figure = blank_fig(), config = config)
                ], className = "content-section-2")
            ], className = "line-container")


        ], className = "main-section"),

    ], className = "dashboard")

], id = "layout")



#the following 4 callbacks are similar to eachother, the sligth difference is the data used in the tables.
# each callback takes 3 inputs (slider, dropdown, button)
# and outputs the children of the corresponding html.Div according to the selected view (chart view, or table view),
# and changes the style and the text displayed on the button
@app.callback(
    # the outputs /// must be specified before the inputs
    #the Input and Output functions take 2 arguments(component_id, component_property)
    [Output('table1', 'children'),
     Output('button1', 'style'),
     Output('button1', 'children')],
    # the inputs
    [Input('slider1', 'value'),
     Input('dropdown1', 'value'),
     Input('button1', 'n_clicks')]
)
# This function is called everytime the callback is triggered
def update_table_chart(date_range, regions, nclicks):
    # filter the data by region
    dff = df[df['Region'].isin(regions)]
    # select necessary columns
    dff = dff[['month_year', 'Sex', 'age_banding', 'work_undertaken']]
    # filter the data by date
    dff = dff[(dff["month_year"] >= pd.to_datetime(main_dict[date_range[0]])) & (dff['month_year'] <= pd.to_datetime(main_dict[date_range[1]]))]
    dff['month_year'] = dff['month_year'].astype(str)
    dff['month_year'] = dff['month_year'].apply(lambda x:x[0:7])
    dff2 = dff.pivot_table(index = 'Sex', columns = 'month_year', values='age_banding', aggfunc='count')
    dff2.loc['sum']= dff2.sum(numeric_only=True, axis=0)
    dff2 = dff2.reset_index(drop = False)
    dffig = dff.groupby(['Sex', 'work_undertaken'], as_index = False).count()
    dffig = dffig.rename(columns = {'age_banding': 'count'})

    

    # if the button is not clicked or clicked an even number of times
    if (nclicks % 2) == 0:
        # the children of the div is the table
        children = [
            #call the datatable function
            dash_table.DataTable(
                # the id of the table
                id='datatable1',
                # the columns of the table,
                # each id should correspond to a name of a column in the dataframe
                columns=[{'name': i, 'id': i} for i in dff2.columns],
                # the data passed into the DataTable function
                data = dff2.to_dict('records'),
                # set the page action to none
                # to allow scrolling
                page_action = 'none',
                # set the table style
                style_as_list_view=False,
                style_table={
                            'overflowY': 'auto',
                            "width": "auto",
                            'overflowX': 'auto'},
                # set the style of the cells
                style_cell={
                    'minWidth': 100, 'maxWidth': 100, 'width': 100,
                    'font-weight': 'bold',
                    'textAlign': 'center',
                },
                # set the style of the data
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'background-color': '#efefef'
                },
                # set the style of the headers
                style_header={
                    'backgroundColor': '#b95535',
                    'fontWeight': 'bold',
                    'color': 'white'
                },
                # conditional styling of the data
                # accepts a list of dictionaries
                # where each dictionary resembles an if statement
                # "if" will be the key, and another dictionary will be the condition
                # followed by the style
                style_data_conditional = [
                    {
                    "if": {"state": "selected"}, 
                    "backgroundColor": "#213285",
                    "border": "1px solid green",
                    "color": "white"
                    }],
                export_format="csv",
                export_headers = 'display'
            ),
        ]
        # dash_table.DataTable(
        #     data=dff2.to_dict('records'),
        #     columns=[{'id': c, 'name': c} for c in dff2.columns],
        #     style_table={'overflowX': 'auto', 'width': '100%'},
        # )]
        # set the style of the button
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
        }
    # display "Chart view" on the button
        button_children = "Chart view"
    # if the button is clicked an odd number of times
    else:
        # make the figure
        fig = px.bar(dffig, 
        x = 'Sex', 
        y = 'count', 
        color = 'work_undertaken',
        color_discrete_sequence = ['#b95535', 
                                    '#213285', 
                                    '#e79e23', 
                                    '#8d3f29', 
                                    'green', 
                                    'red', 
                                    'blue',
                                    '#33a680',
                                    '#339ca6',
                                    '#00402f'],)
        fig.update_layout(margin = dict(l = 40, r = 40, t = 40, b = 40),
                            legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=0.9,
                            title = None
                            )
                        )
            # and assign the children variable to the dcc.Graph component that contains the figure
        children = [dcc.Graph(id = 'graph1', figure = fig, config = config)]

        #Change the style of the button
        style = {
            "height": "auto",
            "padding": "12px",
            "width": "50%",
            "background-color": "#213285",
            "border-radius": "5px",
            "border": "0px",
            "color": "white",
            "text-shadow": "0 0.075em 0.075em rgb(0 0 0 / 50%)",
            "font-size": "16px"
        }

        #Display "Table view" instead of "Chart view"
        button_children = "Table view"

    # return all the 3 values for the 3 outputs
    return children, style, button_children



@app.callback(
    [Output('table2', 'children'),
     Output('button2', 'style'),
     Output('button2', 'children')],
    [Input('slider2', 'value'),
     Input('dropdown2', 'value'),
     Input('button2', 'n_clicks')]
)
def update_table_chart(date_range, regions, nclicks):
    dff = df[df['Region'].isin(regions)]
    dff = dff[['month_year', 'age_banding', 'Sex', 'work_undertaken']]
    dff = dff[(dff["month_year"] >= pd.to_datetime(main_dict[date_range[0]])) & (dff['month_year'] <= pd.to_datetime(main_dict[date_range[1]]))]
    dff['month_year'] = dff['month_year'].astype(str)
    dff['month_year'] = dff['month_year'].apply(lambda x:x[0:7])
    dff2 = dff.pivot_table(index = 'age_banding', columns = 'month_year', values='work_undertaken', aggfunc='count')
    dff2.loc['sum']= dff2.sum(numeric_only=True, axis=0)
    dff2 = dff2.reset_index(drop = False)
    dffig = dff.groupby(['age_banding', 'work_undertaken'], as_index = False).count()
    dffig = dffig.rename(columns = {'Sex': 'count'})


    if (nclicks % 2) == 0:
        children = [
            dash_table.DataTable(
                id='datatable1',
                columns=[{'name': i, 'id': i} for i in dff2.columns],
                data = dff2.to_dict('records'),
                page_action = 'none',
                
                style_as_list_view=False,
                style_table={
                            'overflowY': 'auto',
                            "width": "auto"},
                style_cell={
                    'minWidth': 100, 'maxWidth': 100, 'width': 100,
                    'font-weight': 'bold',
                    'textAlign': 'center',
                },
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'background-color': '#efefef'
                },
                style_header={
                    'backgroundColor': '#b95535',
                    'fontWeight': 'bold',
                    'color': 'white'
                },
                style_data_conditional = [
                    {
                    "if": {"state": "selected"}, 
                    "backgroundColor": "#213285",
                    "border": "1px solid green",
                    "color": "white"
                    }],
                export_format="csv",
                export_headers = 'display'
                
            ),
        ]

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
        }

        button_children = "Chart view"

    else:
        fig = px.bar(dffig, 
        x = 'age_banding', 
        y = 'count', 
        color = 'work_undertaken',
        color_discrete_sequence = ['#b95535', 
                                    '#213285', 
                                    '#e79e23', 
                                    '#8d3f29', 
                                    'green', 
                                    'red', 
                                    'blue',
                                    '#33a680',
                                    '#339ca6',
                                    '#00402f'],)
        fig.update_layout(margin = dict(l = 40, r = 40, t = 40, b = 40),
                            legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=0.9,
                            title = None
                            )
                        )
        children = [dcc.Graph(id = 'graph2', figure = fig, config = config)]

        style = {
            "height": "auto",
            "padding": "12px",
            "width": "50%",
            "background-color": "#213285",
            "border-radius": "5px",
            "border": "0px",
            "color": "white",
            "text-shadow": "0 0.075em 0.075em rgb(0 0 0 / 50%)",
            "font-size": "16px"
        }

        button_children = "Table view"

    return children, style, button_children


@app.callback(
    [Output('table3', 'children'),
     Output('button3', 'style'),
     Output('button3', 'children')],
    [Input('slider3', 'value'),
     Input('dropdown3', 'value'),
     Input('button3', 'n_clicks')]
)
def update_table_chart(date_range, regions, nclicks):
    dff = df[df['Region'].isin(regions)]
    dff = dff[['month_year', 'work_undertaken', 'age_banding',]]
    dff = dff[(dff["month_year"] >= pd.to_datetime(main_dict[date_range[0]])) & (dff['month_year'] <= pd.to_datetime(main_dict[date_range[1]]))]
    dff['month_year'] = dff['month_year'].astype(str)
    dff['month_year'] = dff['month_year'].apply(lambda x:x[0:7])
    dff2 = dff.pivot_table(index = 'work_undertaken', columns = 'month_year', values='age_banding', aggfunc='count')
    dff2.loc['sum']= dff2.sum(numeric_only=True, axis=0)
    dff2 = dff2.reset_index(drop = False)
    dffig = dff.groupby(['work_undertaken'], as_index = False).count()
    dffig = dffig.rename(columns = {"age_banding": "count"})
    
    if (nclicks % 2) == 0:
        children = [
            dash_table.DataTable(
                id='datatable1',
                columns=[{'name': i, 'id': i} for i in dff2.columns],
                data = dff2.to_dict('records'),
                page_action = 'none',
                
                style_as_list_view=False,
                style_table={
                            'overflowY': 'auto',
                            "width": "auto"},
                style_cell={
                    'minWidth': 100, 'maxWidth': 100, 'width': 100,
                    'font-weight': 'bold',
                    'textAlign': 'center',
                },
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'background-color': '#efefef'
                },
                style_header={
                    'backgroundColor': '#b95535',
                    'fontWeight': 'bold',
                    'color': 'white'
                },
                style_data_conditional = [
                    {
                    "if": {"state": "selected"}, 
                    "backgroundColor": "#213285",
                    "border": "1px solid green",
                    "color": "white"
                    }],
                export_format="csv",
                export_headers = 'display'
            ),
        ]


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
        }

        button_children = "Chart view"


    else:
        fig = px.bar(dffig, 
        x = 'work_undertaken', 
        y = 'count', 
        color = 'work_undertaken',
        color_discrete_sequence = ['#b95535', 
                                    '#213285', 
                                    '#e79e23', 
                                    '#8d3f29', 
                                    'green', 
                                    'red', 
                                    'blue',
                                    '#33a680',
                                    '#339ca6',
                                    '#00402f'],)
        fig.update_layout(margin = dict(l = 40, r = 40, t = 40, b = 40),
                            legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=0.9,
                            title = None
                            )
                        )
        children = [dcc.Graph(id = 'graph3', figure = fig, config = config)]

        style = {
            "height": "auto",
            "padding": "12px",
            "width": "50%",
            "background-color": "#213285",
            "border-radius": "5px",
            "border": "0px",
            "color": "white",
            "text-shadow": "0 0.075em 0.075em rgb(0 0 0 / 50%)",
            "font-size": "16px"
        }

        button_children = "Table view"

    return children, style, button_children



@app.callback(
    [Output('table4', 'children'),
     Output('button4', 'style'),
     Output('button4', 'children')],
    [Input('slider4', 'value'),
     Input('dropdown4', 'value'),
     Input('button4', 'n_clicks')]
)
def update_table_chart(date_range, regions, nclicks):
    dff = df[df['Region'].isin(regions)]
    dff = dff[['month_year', 'Region', 'age_banding', 'work_undertaken']]
    dff = dff[(dff["month_year"] >= pd.to_datetime(main_dict[date_range[0]])) & (dff['month_year'] <= pd.to_datetime(main_dict[date_range[1]]))]
    dff['month_year'] = dff['month_year'].astype(str)
    dff['month_year'] = dff['month_year'].apply(lambda x:x[0:7])
    dff2 = dff.pivot_table(index = 'Region', columns = 'month_year', values='age_banding', aggfunc='count')
    dff2.loc['sum']= dff2.sum(numeric_only=True, axis=0)
    dff2 = dff2.reset_index(drop = False)
    dffig = dff.groupby(['Region', 'work_undertaken'], as_index = False).count()
    dffig = dffig.rename(columns = {"age_banding": "count"})
    
    if (nclicks % 2) == 0:
        children = [
            dash_table.DataTable(
                id='datatable1',
                columns=[{'name': i[0:7], 'id': i} for i in dff2.columns],
                data = dff2.to_dict('records'),
                page_action = 'none',
                
                style_as_list_view=False,
                style_table={
                            'overflowY': 'auto',
                            "width": "auto"},
                style_cell={
                    'minWidth': 100, 'maxWidth': 100, 'width': 100,
                    'font-weight': 'bold',
                    'textAlign': 'center',
                },
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'background-color': '#efefef'
                },
                style_header={
                    'backgroundColor': '#b95535',
                    'fontWeight': 'bold',
                    'color': 'white'
                },
                style_data_conditional = [
                    {
                    "if": {"state": "selected"}, 
                    "backgroundColor": "#213285",
                    "border": "1px solid green",
                    "color": "white"
                    }],
                export_format="csv",
                export_headers= 'display'
            ),
        ]


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
        }

        button_children = "Chart view"


    else:
        fig = px.bar(dffig, 
        x = 'Region', 
        y = 'count', 
        color = 'work_undertaken',
        color_discrete_sequence = ['#b95535', 
                                    '#213285', 
                                    '#e79e23', 
                                    '#8d3f29', 
                                    'green', 
                                    'red', 
                                    'blue',
                                    '#33a680',
                                    '#339ca6',
                                    '#00402f'],)
        fig.update_layout(margin = dict(l = 40, r = 40, t = 40, b = 40),
                            legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=0.9,
                            title = None
                            )
                        )
        children = [dcc.Graph(id = 'graph3', figure = fig, config = config)]

        style = {
            "height": "auto",
            "padding": "12px",
            "width": "50%",
            "background-color": "#213285",
            "border-radius": "5px",
            "border": "0px",
            "color": "white",
            "text-shadow": "0 0.075em 0.075em rgb(0 0 0 / 50%)",
            "font-size": "16px"
        }

        button_children = "Table view"

    return children, style, button_children




# This callback is to connect the slider with the line chart
@app.callback(
Output('line-chart', 'figure'),
[Input('slider5', 'value'),]
)
def update_line_chart(date_range):
    # filter the data according the date range selected
    dff = df[(df["month_year"] >= pd.to_datetime(main_dict[date_range[0]])) & (df['month_year'] <= pd.to_datetime(main_dict[date_range[1]]))]
    dff = dff.groupby(['month_year', 'work_undertaken'], as_index = False).count()
    dff = dff.rename(columns = {'age_banding': 'count'})
    dff = dff.drop(['Unnamed: 0', 'Sex', 'Region'], axis = 1)
    dff = dff.sort_values('month_year')

    fig = px.line(dff, 
    x = "month_year", 
    y = "count", 
    color = "work_undertaken", 
    color_discrete_sequence = ['#b95535', 
                                '#213285', 
                                '#e79e23', 
                                '#8d3f29', 
                                'green', 
                                'red', 
                                'blue'],
                                markers = True)
    fig.update_layout(margin = dict(l = 10, t = 10, r = 10, b = 10),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=0.9,
        title = None
    ))
    return fig


@app.callback(
Output('map-chart', 'figure'),
[Input('slider6', 'value'),]
)
def update_map_chart(date_range):
    return make_map(date_range)



# run the app
if __name__  ==  "__main__":
    app.run_server(debug = True)