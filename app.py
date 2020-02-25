# -*- coding: utf-8 -*-
import dash
import json
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
import datetime

from pages import (
    uptime,
    rate,
    fpfq,
    opportunity,
)

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Describe the layout/ UI of the app
app.layout = html.Div([
    html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
    ),
    html.Div([
                ### Uptime Objects
                dcc.Dropdown(id='uptime_category_dropdown',
                            options=[{'label': 'Stop Category', 'value': 'Stop Category'},
                                    {'label': 'Stop Reason', 'value': 'Stop Reason'}],
                            value='Stop Category',
                            className="dcc_control"),
                dcc.Input(id='uptime_occurence_filter',
                            type='number',
                            value=300,
                            className="dcc_control"),
                dcc.Dropdown(id='uptime_pareto_dropdown',
                            options=[{'label': 'Product', 'value': 'Product'},
                                    {'label': 'User', 'value': 'User'}],
                            value='User',
                            className="dcc_control"),
                dcc.RangeSlider(id='uptime_year_slider',
                             className="dcc_control"),
                dcc.Graph(id='uptime_dist_plot'),
                dcc.Graph(id='uptime_bar_plot'),
                dcc.Graph(id='uptime_user_plot'),

                ### Rate Objects
                dcc.Dropdown(id='pareto_dropdown',
                            options=[{'label': 'Product', 'value': 'Product'},
                                    {'label': 'User', 'value': 'User'}],
                            value='User',
                            className="dcc_control"),
                dcc.RangeSlider(id='year_slider',
                             className="dcc_control"),
                dcc.Graph(id='dist_plot'),
                dcc.Graph(id='bar_plot'),
                dcc.Graph(id='user_plot'),

                ### Yield Objects
                dcc.Dropdown(id='yield_pareto_dropdown',
                            options=[{'label': 'Product', 'value': 'Product'},
                                    {'label': 'User', 'value': 'User'}],
                            value='User',
                            className="dcc_control"),
                dcc.RangeSlider(id='yield_year_slider',
                             className="dcc_control"),
                dcc.Graph(id='yield_dist_plot'),
                dcc.Graph(id='yield_bar_plot'),
                dcc.Graph(id='yield_user_plot'),

                ### Opportunity Objects
                dcc.Dropdown(id='opportunity_metric_dropdown',
                            options=[{'label': 'Net Quantity Produced', 'value': 'Net Quantity Produced'},
                                    {'label': 'Saved Run Time', 'value': 'Run Time'}],
                            value='Line',
                            className="dcc_control"),
                html.Div(id='updatemode-output-container'),
                html.P(id="top_main_graph"),
                html.P(id="top_side_graph"),
                dcc.RangeSlider(id='opportunity_year_slider',
                             className="dcc_control"),
                dcc.Dropdown(id='opportunity_pareto_dropdown',
                            options=[{'label': 'Product', 'value': 'Product'},
                                    {'label': 'Line', 'value': 'Line'}],
                            value='Line',
                            className="dcc_control"),
                dcc.Graph(id='opportunity_dist_plot'),
                dcc.Graph(id='opportunity_bar_plot'),
                dcc.Graph(id='opportunity_user_plot'),



                ### Animate Objects
                dcc.Graph(id='animate_opportunity'),
                html.Pre(id='hover-data', style={'margin-top': '25px'})

        ],style={'display': 'none'})
        ])

app.config.suppress_callback_exceptions = False

# Update page
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/featherstone/rate":
        return rate.create_layout(app)
    elif pathname == "/featherstone/uptime":
        return uptime.create_layout(app)
    elif pathname == "/featherstone/yield":
        return fpfq.create_layout(app)
    elif pathname == "/featherstone/opportunity":
        return opportunity.create_layout(app)
    elif pathname == "/featherstone/opportunity":
        return (
            rate.create_layout(app),
            uptime.create_layout(app),
            fpfq.create_layout(app),
            opportunity.create_layout(app)
        )
    else:
        return uptime.create_layout(app)

### Uptime Callbacks
@app.callback(
    Output('uptime_user_plot', 'figure'),
    [Input('uptime_occurence_filter', 'value'),
    Input('uptime_category_dropdown', 'value'),
    Input('uptime_pareto_dropdown', 'value'),
    Input('uptime_year_slider', 'value'),
    Input('uptime_dist_plot', 'clickData'),
    Input('uptime_bar_plot', 'clickData')]
)
def display_hover_data(occurences, reason, groupby, year, distClickData, barClickData):
    return uptime.make_user_plot(occurences, reason, groupby, year, distClickData, barClickData)
@app.callback(
    Output('uptime_dist_plot', 'figure'),
    [Input('uptime_occurence_filter', 'value'),
    Input('uptime_category_dropdown', 'value'),
    Input('uptime_pareto_dropdown', 'value'),
    Input('uptime_year_slider', 'value'),
    Input('uptime_bar_plot', 'clickData')]
)
def display_hover_data(occurences, reason, groupby, year, clickData):
    return uptime.make_dist_plot(occurences, reason, groupby, year, clickData)
@app.callback(
    Output('uptime_bar_plot', 'figure'),
    [Input('uptime_occurence_filter', 'value'),
    Input('uptime_category_dropdown', 'value'),
    Input('uptime_year_slider', 'value')]
)
def update_bar_plot(occurences, reason, year):
    return uptime.make_bar_plot(occurences, reason, year)

### Rate Callbacks
@app.callback(
    Output('user_plot', 'figure'),
    [Input('pareto_dropdown', 'value'),
    Input('year_slider', 'value'),
    Input('dist_plot', 'clickData'),
    Input('bar_plot', 'clickData')]
)
def display_hover_data(groupby, year, distClickData, barClickData):
    return rate.make_performance_plot(groupby, year, distClickData, barClickData)
@app.callback(
    Output('dist_plot', 'figure'),
    [Input('pareto_dropdown', 'value'),
    Input('year_slider', 'value'),
    Input('bar_plot', 'clickData')]
)
def display_hover_data(groupby, year, clickData):
    return rate.make_pareto_plot(groupby, year, clickData)
@app.callback(
    Output('bar_plot', 'figure'),
    [Input('year_slider', 'value')]
)
def update_bar_plot(year):
    return rate.make_bar_plot(year)

### Yield Callbacks
@app.callback(
    Output('yield_user_plot', 'figure'),
    [Input('yield_pareto_dropdown', 'value'),
    Input('yield_year_slider', 'value'),
    Input('yield_dist_plot', 'clickData'),
    Input('yield_bar_plot', 'clickData')]
)
def display_hover_data(groupby, year, distClickData, barClickData):
    return fpfq.make_performance_plot(groupby, year, distClickData, barClickData)
@app.callback(
    Output('yield_dist_plot', 'figure'),
    [Input('yield_pareto_dropdown', 'value'),
    Input('yield_year_slider', 'value'),
    Input('yield_bar_plot', 'clickData')]
)
def display_hover_data(groupby, year, clickData):
    return fpfq.make_pareto_plot(groupby, year, clickData)
@app.callback(
    Output('yield_bar_plot', 'figure'),
    [Input('yield_year_slider', 'value')]
)
def update_bar_plot(year):
    return fpfq.make_bar_plot(year)

@app.callback(
    Output('top_side_graph', 'children'),
    [Input('opportunity_metric_dropdown', 'value'),
    Input('opportunity_year_slider', 'value'),
    Input('opportunity_pareto_dropdown', 'value'),
    Input('opportunity_bar_plot', 'clickData')]
)
def display_hover_data(column, quantile, groupby, clickData):
    return opportunity.make_top_pareto_plot(column, quantile, groupby, clickData)
@app.callback(
    Output('opportunity_dist_plot', 'figure'),
    [Input('opportunity_metric_dropdown', 'value'),
    Input('opportunity_year_slider', 'value'),
    Input('opportunity_pareto_dropdown', 'value'),
    Input('opportunity_bar_plot', 'clickData')]
)
def display_hover_data(column, quantile, groupby, clickData):
    return opportunity.make_pareto_plot(column, quantile, groupby, clickData)
@app.callback(
    Output('opportunity_bar_plot', 'figure'),
    [Input('opportunity_metric_dropdown', 'value'),
     Input('opportunity_year_slider', 'value'),
     Input('opportunity_pareto_dropdown', 'value')]
)
def update_bar_plot(column, quantile, groupby):
    return opportunity.make_bar_plot(column, quantile, groupby)

@app.callback(
     Output('top_main_graph', 'children'),
    [Input('opportunity_metric_dropdown', 'value'),
     Input('opportunity_year_slider', 'value'),
     Input('opportunity_pareto_dropdown', 'value')]
)
def update_bar_plot(column, quantile, groupby):
    return opportunity.make_top_main_graph(column, quantile, groupby)

@app.callback(Output('updatemode-output-container', 'children'),
              [Input('opportunity_year_slider', 'value')])
def display_value(value):
    return 'Performance Quantile: {}'.format(value)

# @app.callback(
#     Output('hover-data', 'children'),
#     [Input('opportunity_bar_plot', 'clickData')]
# )
# def display_hover_data(clickData):
#     return json.dumps(clickData, indent=2)


if __name__ == "__main__":
    app.run_server(debug=False)
