# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from matplotlib import cm
import plotly.express as px
from utils import *

import pandas as pd
import numpy as np
import datetime

import dash_html_components as html
import json
from textwrap import dedent as d

oee = pd.read_csv('assets/featherstone_oee_with_user.csv', low_memory=False)
oee["To Date/Time"] = pd.to_datetime(oee["To Date/Time"])
oee["From Date/Time"] = pd.to_datetime(oee["From Date/Time"])
oee["Scheduled Time"] = pd.to_timedelta(oee["Scheduled Time"])
oee["Run Time"] = pd.to_timedelta(oee["Run Time"])

oee["Rate"] = oee["Net Quantity Produced"] / (oee["Run Time"].dt.total_seconds()/60/60)
oee["Yield"] = oee["Quantity Good"] / oee["Net Quantity Produced"]
oee["Utilization"] = oee["Scheduled Time"] / datetime.timedelta(hours=1)
oee["Uptime"] = oee["Run Time"] / oee["Scheduled Time"]
metric_cols = ["Rate", "Yield", "Uptime", "Utilization"]

# filters
oee.loc[(oee["Rate"] == np.inf) |
        (oee["Rate"] == 0), "Rate"] = np.nan # rates bounded: 0 < rate < inf
oee.loc[(oee["Yield"] == 0) |
        (oee["Yield"] > 1), "Yield"] = np.nan # yield bounded: 0 < yield < 1
oee.Uptime.fillna(inplace=True, value=0)

def select_data(df, year=[2017,2020]):
    new_df = df.loc[(~df["User"].isin(["[None]"])) & (df["Rate"] < 2.5*1e4)]
    new_df = new_df.loc[(new_df["To Date/Time"].dt.year >= year[0]) &
                        (new_df["From Date/Time"].dt.year <= year[1])]
    new_df = new_df.loc[~(new_df["Line"].isin(['Line 95', 'Line 96', 'Line 97']))]
    return new_df

def make_pareto_plot(groupby='User',
                    year=[2017,2020],
                    clickData=None):
    if clickData != None:
        line_index = clickData['points'][0]['curveNumber']
        line = oee["Line"].unique()[line_index]
    else:
        line = 'Line 32'
    data = select_data(oee, year)
    data = data.loc[(data["Line"] == line)]
    figure = px.histogram(data,
                        x="Yield",
                        y="Yield",
                        color=groupby,
                        title="{}, Production by {}".format(line, groupby),
                        hover_data=data.columns)
    figure.update_layout({
                "plot_bgcolor": "#F9F9F9",
                "paper_bgcolor": "#F9F9F9",
    })
    return figure

def make_performance_plot(groupby='User',
                    year=[2017,2020],
                    distClickData=None, barClickData=None):
    if (distClickData != None) & (barClickData != None):
        item_index = distClickData['points'][0]['curveNumber']
        line_index = barClickData['points'][0]['curveNumber']
        line = oee["Line"].unique()[line_index]
    else:
        reason_index = 0
        user_index = 0
        line = 'Line 32'
        groupby = 'User'
        item_index= 0
    data = select_data(oee, year)
    item = data.loc[(data["Line"] == line)][groupby].unique()[item_index]
    if groupby == 'Product':
        color='User'
    else:
        color='Product'
    data = data.loc[(data[groupby] == item)]
    figure = px.box(data,
                        x="Line",
                        y="Yield",
                        color=color,
                        title="Yield Profile for {}".format(item),
                        points=False,
                        hover_data=data.columns)
    figure.update_layout({
                "plot_bgcolor": "#F9F9F9",
                "paper_bgcolor": "#F9F9F9",
    })
    return figure

def make_bar_plot(year=[2017,2020]):
    data = select_data(oee, year)
    figure = px.histogram(data,
                        x="Yield",
                        y="Yield",
                        color='Line',
                        hover_data=data.columns)
    figure.update_layout({
                "plot_bgcolor": "#F9F9F9",
                "paper_bgcolor": "#F9F9F9",
    })
    return figure

def create_layout(app):
    return html.Div([
    html.Div([
        html.Div([
            html.Div([
                            html.H3(
                                "Asset Capability",
                                style={"margin-bottom": "0px"},
                            ),
                            html.H5(
                                "Yield",
                                style={"margin-top": "0px"}
                            ),
                        ]
                    )
                ],
                className="twelve columns",
                id="title",
            ),
            ],
            className="row flex-display",
            ),
    html.Div([
        html.Div([
           html.P(
               "Pareto by:"
           ),
            dcc.Dropdown(id='yield_pareto_dropdown',
                        options=[{'label': 'Product', 'value': 'Product'},
                                {'label': 'User', 'value': 'User'}],
                        value='User',
                        className="dcc_control"),
            html.P(
                "Year filter:"
            ),
            dcc.RangeSlider(id='yield_year_slider',
                        min=min(oee["From Date/Time"]).year,
                        max=max(oee["To Date/Time"]).year,
                        value=[min(oee["From Date/Time"]).year,
                            max(oee["To Date/Time"]).year],
                        marks={'{}'.format(i): '{}'.format(i) for i in\
                         oee["From Date/Time"].dt.year.unique()},
                         className="dcc_control")
                         ],
                         className="pretty_container four columns",
                         id='cross-filter-options'),
    html.Div([
        html.Div([get_menu()],
                      className="row container-display"),
        html.Div([
            dcc.Graph(id='yield_bar_plot',
                      figure=make_bar_plot()
                      )
                      ],
                      className="pretty_container")
                  ],
                  className='eight columns',
                  ),
                  ],
                  className='row flex-display'
                  ),
    html.Div([
        html.Div(
                    [
                        html.Div(
                            [
                                html.H5(
                                    "Yield Drill Down"
                                ),
                            ]
                        )
                    ],
                    className="twelve columns",
                    id="subtitle",
                ),
                ],
                className="row flex-display",
                ),
    html.Div([
        html.Div(
            [dcc.Graph(id='yield_dist_plot',
                      figure=make_pareto_plot())],
                      className='pretty_container six columns',
                ),
        html.Div(
        [dcc.Graph(id='yield_user_plot',
                      figure=make_performance_plot())],
                      className='pretty_container six columns',
                ),
                      ],
            className='row flex-display',
            ),
    # html.Div([
    # dcc.Markdown(d("""
    #         **Hover Data**
    #
    #         Mouse over values in the graph.
    #     """)),
    #     html.Pre(id='hover-data', style={'margin-top': '25px'})
    # ],
    # style={'width': '48%',
    #             'display': 'inline-block',
    #             'margin-left': '25px',
    #             'max-width': '400px'})
])

if __name__ == '__main__':
    app.run_server(debug=True)
