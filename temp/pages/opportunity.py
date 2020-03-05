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

oee = pd.read_csv('assets/oee.csv', low_memory=False)
oee["To Date/Time"] = pd.to_datetime(oee["To Date/Time"])
oee["From Date/Time"] = pd.to_datetime(oee["From Date/Time"])
oee["Scheduled Time"] = pd.to_timedelta(oee["Scheduled Time"])
oee["Run Time"] = pd.to_timedelta(oee["Run Time"])

opp = pd.read_csv('assets/opportunity.csv', index_col=[0,1,2,3])
annual_operating = pd.read_csv('assets/annual.csv', index_col=[0,1])
quantiles = np.arange(50,96,1)
quantiles = quantiles*.01
quantiles = np.round(quantiles, decimals=2)

# def top_main_graph(column='Net Quantity Produced',
#                    quantile=0.9,
#                    groupby='Line'):
#     df = (opp.reorder_levels([0,3,1,2]).loc[column, quantile]\
#         .groupby([groupby]).sum(axis=1) - \
#     opp.reorder_levels([0,3,1,2]).loc[column, 0.5]\
#         .groupby([groupby]).sum(axis=1))
#
#     dff = annual_operating.groupby(groupby).sum(axis=1)[column]\
#         .sort_values()
#     dff.columns = [column]
#     data = pd.merge(dff, df, left_index=True, right_index=True)
#     cols = data.columns
#     data["Total"] = data.sum(axis=1)
#     data = data.sort_values(by='Total')
#     top_3 = data[metrics].sum(axis=1).sort_values(ascending=False)[:3]
#     return top_3

def make_opportunity_pareto(column='Net Quantity Produced',
                     quantile=0.9,
                     groupby='Line',
                     clickData=None):
    if clickData != None:
        line = clickData['points'][0]['y']
    else:
        line = 'Line 94'
    if groupby == 'Line':
        df = (opp.reorder_levels([0,1,3,2]).loc[column, line, quantile]\
        - opp.reorder_levels([0,1,3,2]).loc[column, line, 0.5])
        dff = annual_operating.loc[line][column]
    else:
        df = (opp.reorder_levels([0,2,3,1]).loc[column, line, quantile]\
        - opp.reorder_levels([0,2,3,1]).loc[column, line, 0.5])
        dff = annual_operating.reorder_levels([1,0]).loc[line][column]
    dff = pd.DataFrame(dff)
    dff.columns = ['Net Quantity Produced']
    data = pd.merge(df, dff, left_index=True, right_index=True)
    cols = data.columns
    data["Total"] = data.sum(axis=1)
    data = data.sort_values(by='Total')

    bar_fig = []
    for col in cols:
        bar_fig.append(
        go.Bar(
        name=col,
        orientation="h",
        y=[str(i) for i in data.index],
        x=data[col],
        customdata=[col]
        )
    )

    figure = go.Figure(
        data=bar_fig,
        layout=dict(
            barmode="stack",
            yaxis_type="category",
            yaxis=dict(title=line),
            title="Annualized Opportunity",
            plot_bgcolor="#F9F9F9",
            paper_bgcolor="#F9F9F9"
        )
    )
    figure.update_layout({
                "plot_bgcolor": "#F9F9F9",
                "paper_bgcolor": "#F9F9F9",
    })
    return figure

def make_opportunity_plot(column='Net Quantity Produced',
                  quantile=0.9,
                  groupby='Line'):
    df = (opp.reorder_levels([0,3,1,2]).loc[column, quantile]\
        .groupby([groupby]).sum(axis=1) - \
    opp.reorder_levels([0,3,1,2]).loc[column, 0.5]\
        .groupby([groupby]).sum(axis=1))

    dff = annual_operating.groupby(groupby).sum(axis=1)[column]\
        .sort_values()
    dff.columns = [column]
    data = pd.merge(dff, df, left_index=True, right_index=True)
    cols = data.columns
    data["Total"] = data.sum(axis=1)
    data = data.sort_values(by='Total')
    bar_fig = []
    for col in cols:
        bar_fig.append(
        go.Bar(
        name=col,
        orientation="h",
        y=[str(i) for i in data.index],
        x=data[col],
        customdata=[col]
        )
    )
    figure = go.Figure(
    data=bar_fig,
    layout=dict(
        barmode="stack",
        yaxis_type="category",
        yaxis=dict(title=groupby),
        title="Annualized Opportunity",
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9"
    ),
    )
    return figure

def make_top_main_graph(column='Net Quantity Produced',
                  quantile=0.9,
                  groupby='Line'):
    df = (opp.reorder_levels([0,3,1,2]).loc[column, quantile]\
        .groupby([groupby]).sum(axis=1) - \
    opp.reorder_levels([0,3,1,2]).loc[column, 0.5]\
        .groupby([groupby]).sum(axis=1))

    dff = annual_operating.groupby(groupby).sum(axis=1)[column]\
        .sort_values()
    dff.columns = [column]
    data = pd.merge(dff, df, left_index=True, right_index=True)
    cols = data.columns
    data["Total"] = data.sum(axis=1)
    data = data.sort_values(by='Total')
    metrics = df.columns
    top = data[metrics].sum(axis=1).sort_values(ascending=False)
    top = pd.DataFrame(top)
    top.columns = [column]
    top[column] = np.round(top[column])
    top = top.reset_index()
    return generate_table(top, max_rows=5)

def make_top_pareto_plot(column='Net Quantity Produced',
                     quantile=0.9,
                     groupby='Line',
                     clickData=None):
    if clickData != None:
        line = clickData['points'][0]['y']
    else:
        line = 'Line 94'
    if groupby == 'Line':
        df = (opp.reorder_levels([0,1,3,2]).loc[column, line, quantile]\
        - opp.reorder_levels([0,1,3,2]).loc[column, line, 0.5])
        dff = annual_operating.loc[line][column]
    else:
        df = (opp.reorder_levels([0,2,3,1]).loc[column, line, quantile]\
        - opp.reorder_levels([0,2,3,1]).loc[column, line, 0.5])
        dff = annual_operating.reorder_levels([1,0]).loc[line][column]
    dff = pd.DataFrame(dff)
    dff.columns = ['Net Quantity Produced']
    data = pd.merge(df, dff, left_index=True, right_index=True)
    cols = data.columns
    data["Total"] = data.sum(axis=1)
    data = data.sort_values(by='Total')

    metrics = df.columns
    top = data[metrics].sum(axis=1).sort_values(ascending=False)
    top = pd.DataFrame(top)
    top.columns = [column]
    top[column] = np.round(top[column])
    top = top.reset_index()
    return generate_table(top, max_rows=5)

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
                                "Opportunity",
                                style={"margin-top": "0px"}
                            ),
                        ])
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
               "Annualized Opportunity Metric:"
           ),
            dcc.Dropdown(id='opportunity_metric_dropdown',
                        options=[{'label': 'Net Quantity Produced', 'value': 'Net Quantity Produced'},
                                {'label': 'Saved Run Time', 'value': 'Run Time'}],
                        value='Net Quantity Produced',
                        className="dcc_control"),
            html.Div(id='updatemode-output-container',
                    style={'margin-top': 20}
            ),
            dcc.Slider(id='opportunity_year_slider',
                        min=0.5,
                        max=0.99,
                        step=0.01,
                        value=.9,
                        included=False,
                        className="dcc_control"),
            html.P(
                "Pareto by:"
            ),
             dcc.Dropdown(id='opportunity_pareto_dropdown',
                         options=[{'label': 'Product', 'value': 'Product'},
                                 {'label': 'Line', 'value': 'Line'}],
                         value='Line',
                         className="dcc_control"),
                         ],
                         className="pretty_container four columns",
                         id='cross-filter-options'),
    html.Div([
        html.Div([get_menu()],
                      className="row container-display"),
        html.Div([
            dcc.Graph(id='opportunity_bar_plot',
                      figure=make_opportunity_plot()
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
                                    "Opportunity Drill Down"
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
            [dcc.Graph(id='opportunity_dist_plot',
                      figure=make_opportunity_pareto())],
                      className='pretty_container eight columns',
                ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [html.P(id="top_main_graph"), html.P("Top Overall")],
                            id="wells",
                            className="mini_container",
                        ),
                        html.Div(
                            [html.P(id="top_side_graph"), html.P("Top Drilldown")],
                            id="gas",
                            className="mini_container",
                        ),
                    ],
                    id="info-container",
                    className="row container-display",
                ),
            ],
                    id="right-column",
                    className="four columns",
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
