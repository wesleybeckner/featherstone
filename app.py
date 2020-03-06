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

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

oee = pd.read_csv('data/oee.csv', low_memory=False)
oee["To Date/Time"] = pd.to_datetime(oee["To Date/Time"])
oee["From Date/Time"] = pd.to_datetime(oee["From Date/Time"])
oee["Scheduled Time"] = pd.to_timedelta(oee["Scheduled Time"])
oee["Run Time"] = pd.to_timedelta(oee["Run Time"])
metric_cols = ["Rate", "Yield", "Uptime", "Utilization"]

master = pd.read_csv('data/downtimes.csv', low_memory=False)
master["From Date/Time"] = pd.to_datetime(master["From Date/Time"])
master["To Date/Time"] = pd.to_datetime(master["To Date/Time"])

opp = pd.read_csv('data/opportunity.csv', index_col=[0,1,2,3])
annual_operating = pd.read_csv('data/annual.csv')
quantiles = np.arange(50,96,1)
quantiles = quantiles*.01
quantiles = np.round(quantiles, decimals=2)
dataset = opp.sort_index()
lines = opp.index.get_level_values(1).unique()

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

def select_data(df,
                year=[2018,2020]):
    if "Rate" in df.columns:
        new_df = df.loc[(~df["User"].isin(["[None]"])) & (df["Rate"] < 2.5*1e4)]
    else:
        new_df = df
    new_df = new_df.loc[(new_df["To Date/Time"].dt.year >= year[0]) &
                        (new_df["From Date/Time"].dt.year <= year[1])]
    return new_df

def make_pareto_plot(groupby='User',
                    year=[2018,2020],
                    metric='Rate',
                    clickData=None):
    if clickData != None:
        index = clickData['points'][0]['curveNumber']
        if metric == 'Uptime':
            line = clickData['points'][0]['y']
        else:
            line = oee["Line"].unique()[index]
    else:
        index=3
        line = 'Line 64'
    if metric == 'Uptime':
        data = select_data(master, year)
        reason_col = pd.Series(data.groupby(['Line','Stop Category'], sort=True)\
        ["Duration"].sum().unstack().columns)[index]
        data = data.loc[(data['Stop Category'] == reason_col) &
                (data["Line"] == line) &
                (data["Duration"] < 5)]
        metric = 'Duration'
        metricx = reason_col
    else:
        data = select_data(oee, year)
        data = data.loc[(data["Line"] == line)]
        metricx= metric
    figure = px.histogram(data,
                        x=metric,
                        y=metric,
                        color=groupby,
                        title="{}, {} by {}".format(line, metricx, groupby),
                        hover_data=data.columns)
    figure.update_layout({
                "plot_bgcolor": "#F9F9F9",
                "paper_bgcolor": "#F9F9F9",
    })
    return figure

def make_performance_plot(groupby='User',
                    year=[2018,2020],
                    metric='Rate',
                    distClickData=None, barClickData=None):
    data = select_data(oee, year)
    if (distClickData != None) & (barClickData != None):
        index = barClickData['points'][0]['curveNumber']
        item_index = distClickData['points'][0]['curveNumber']
        if metric == 'Uptime':
            line = barClickData['points'][0]['y']
        else:
            line = oee["Line"].unique()[index]
            item = data.loc[(data["Line"] == line)][groupby].unique()[item_index]

    else:
        index = 3
        user_index = 0
        line = 'Line 64'
        groupby = 'User'
        item_index= 0
        item = data[groupby].unique()[item_index]
    if metric == 'Uptime':
        data = select_data(master, year)
        reason_col = pd.Series(data.groupby(['Line','Stop Category'], sort=True)\
        ["Duration"].sum().unstack().columns)[index]
        data2 = data.loc[(data['Stop Category'] == reason_col) &
                (data["Line"] == line) &
                (data["Duration"] < 5)]
        item = data2[groupby].unique()[item_index]
        data = data.loc[(data["Duration"] < 5)]
        metricx = 'Duration'
        x='Stop Category'
    else:
        x='Line'
        metricx=metric
    data = data.loc[(data[groupby] == item)]
    if groupby == 'Product':
        color='User'
    else:
        color='Product'

    figure = px.box(data,
                        x=x,
                        y=metricx,
                        color=color,
                        title="{} Profile for {}".format(metric, item),
                        points=False,
                        hover_data=data.columns)
    figure.update_layout({
                "plot_bgcolor": "#F9F9F9",
                "paper_bgcolor": "#F9F9F9",
    })
    return figure

def make_bar_plot(year=[2018,2020],
                    metric='Rate'):
    if metric == 'Uptime':
        data = select_data(master, year)
        new_df = data.groupby(['Line','Stop Category'], sort=True)["Duration"]\
            .sum().unstack()
        cols = new_df.columns
        new_df["Total"] = new_df.sum(axis=1)
        new_df.sort_values(by='Total', inplace=True)
        new_df = new_df[cols]
        bar_fig = []
        for Line in new_df.columns:
            bar_fig.append(
            go.Bar(
            name=Line,
            orientation="h",
            y=[str(i) for i in new_df.index],
            x=new_df[Line],
            customdata=[Line]
            )
        )
        figure = go.Figure(
        data=bar_fig,
        layout=dict(
            barmode="stack",
            yaxis_type="category",
            yaxis=dict(title="Stop Category"),
            title="Downtime Events",
            plot_bgcolor="#F9F9F9",
            paper_bgcolor="#F9F9F9"
        ),
        )
    else:
        data = select_data(oee, year)
        figure = px.histogram(data,
                            x=metric,
                            y=metric,
                            color='Line',
                            hover_data=data.columns)
        figure.update_layout({
                    "plot_bgcolor": "#F9F9F9",
                    "paper_bgcolor": "#F9F9F9",
        })
    return figure

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H4(
                    "Asset Capability",
                    style={"margin-bottom": "0px"},
                        ),
                    ],
                    ),
                ],
                className="twelve columns",
                id="title",
            ),
            ],
            className="row flex-display",
            ),
    html.Div([
        html.Div([
            html.Div([
                html.Div(id='updatemode-output-container',
                        style={'margin-top': 20}),
                dcc.Slider(id='opportunity_year_slider',
                            min=0.5,
                            max=0.99,
                            step=0.01,
                            value=.9,
                            included=False,
                            className="dcc_control"),
                dcc.Graph(id='opportunity_bar_plot',
                          figure=make_opportunity_plot()),
                  ],
                  className="pretty_container"
                  ),
              ],
              className='twelve columns',
              ),
          ],
          className='row flex-display'
          ),
    html.Div([
        html.Div([
            html.P(
                "Valuation Metric:"),
            dcc.Dropdown(id='metric_dropdown',
                         options=[{'label': 'Rate', 'value': 'Rate'},
                                 {'label': 'Yield', 'value': 'Yield'},
                                 {'label': 'Uptime', 'value': 'Uptime'}],
                         value='Rate',
                         className="dcc_control"),
                ],
                className='mini_container',
                id='control1',
                ),
       html.Div([
           html.P(
               "Pareto by:"),
               dcc.Dropdown(id='pareto_dropdown',
                        options=[{'label': 'Product', 'value': 'Product'},
                                {'label': 'User', 'value': 'User'}],
                        value='User',
                        className="dcc_control"),
                ],
                className='mini_container',
                id='control2',
                ),
        html.Div([
            html.P(
                "Filter time:"),
            dcc.RangeSlider(id='year_slider',
                        min=min(oee["From Date/Time"]).year,
                        max=max(oee["To Date/Time"]).year,
                        value=[min(oee["From Date/Time"]).year,
                            max(oee["To Date/Time"]).year],
                        marks={'{}'.format(i): '{}'.format(i) for i in\
                         oee["From Date/Time"].dt.year.unique()},
                         className="dcc_control"),
                 ],
                 className="mini_container",
                 id='control3'
                 ),
            ],
            className='row container-display',
            id='control options',
            ),
    html.Div([
        dcc.Graph(id='bar_plot',
                  figure=make_bar_plot())
              ],
              className="pretty_container"
              ),
    html.Div([
        html.Div([
            dcc.Graph(id='dist_plot',
                      figure=make_pareto_plot()),
                      ],
                      className='pretty_container six columns',
                      ),
        html.Div([
            dcc.Graph(id='user_plot',
                      figure=make_performance_plot()),
              ],
              className='pretty_container six columns',
              ),
        ],
        className='row flex-display',
        ),
    ],
    className='pretty container'
    )

### Metric Callbacks
@app.callback(
    Output('user_plot', 'figure'),
    [Input('pareto_dropdown', 'value'),
    Input('year_slider', 'value'),
    Input('metric_dropdown', 'value'),
    Input('dist_plot', 'clickData'),
    Input('bar_plot', 'clickData')]
)
def display_hover_data(groupby, year, metric, distClickData, barClickData):
    return make_performance_plot(groupby, year, metric, distClickData, barClickData)
@app.callback(
    Output('dist_plot', 'figure'),
    [Input('pareto_dropdown', 'value'),
    Input('year_slider', 'value'),
    Input('metric_dropdown', 'value'),
    Input('bar_plot', 'clickData')]
)
def display_hover_data(groupby, year, metric, clickData):
    return make_pareto_plot(groupby, year, metric, clickData)
@app.callback(
    Output('bar_plot', 'figure'),
    [Input('year_slider', 'value'),
    Input('metric_dropdown', 'value'),]
)
def update_bar_plot(year, metric):
    return make_bar_plot(year, metric)

### Opportunity Callbacks
@app.callback(
    Output('opportunity_bar_plot', 'figure'),
    [Input('opportunity_year_slider', 'value')]
)
def update_bar_plot(quantile):
    return make_opportunity_plot(quantile=quantile)

@app.callback(Output('updatemode-output-container', 'children'),
              [Input('opportunity_year_slider', 'value')])
def display_value(value):
    return 'Performance Quantile: {}'.format(value)

if __name__ == '__main__':
    app.run_server(debug=True)
