# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from matplotlib import cm
import plotly.express as px

import pandas as pd
import numpy as np

from utils import *
import dash_html_components as html
import json
from textwrap import dedent as d

#from app import app

master = pd.read_csv('assets/downtimes.csv', low_memory=False)
master["From Date/Time"] = pd.to_datetime(master["From Date/Time"])
master["To Date/Time"] = pd.to_datetime(master["To Date/Time"])
# master["Duration"] = (master["To Date/Time"] - \
# master["From Date/Time"]).dt.total_seconds()/60/60

def select_data(df,
                occurences=300,
                reason='Stop Category',
                year=[2018,2020]):
    new_df = df.loc[(~df["Stop Category"].isin(["[None]", "Planned"]))]\
    .groupby(['Line','Stop Category'], sort=True).filter(lambda x :
     (x['Duration'].count()>=occurences).any())
    new_df = new_df.loc[(new_df["From Date/Time"].dt.year >= year[0]) &
                        (new_df["To Date/Time"].dt.year <= year[1])]
    # new_df = new_df.loc[~(new_df["Line"].isin(['Line 94', 'Line 96', 'Line 97']))]
    return new_df

def make_dist_plot(occurences=300, reason='Stop Category', groupby='User',
                    year=[2018,2020],
                    clickData=None):
    if clickData != None:
        reason_index = clickData['points'][0]['curveNumber']
        line = clickData['points'][0]['y']
    else:
        reason_index = 1
        line = 'Line 94'
    new_df = select_data(master,
                        occurences=occurences,
                        reason=reason,
                        year=year)
    reason_col = pd.Series(new_df.groupby(['Line',reason], sort=True)\
    ["Duration"].sum().unstack().columns)[reason_index]
    print(reason, reason_col, line, groupby)
    table = new_df.loc[(new_df[reason] == reason_col) &
            (new_df["Line"] == line)]\
       .groupby(groupby)\
        .filter(lambda x : (x['Duration'].count()>=10).any())\
        .groupby(groupby).filter(lambda x : (x['Duration'] < 5).all())
    print(table)
    figure = px.histogram(table,
                        x="Duration",
                        y="Duration",
                        color=groupby,
                        title="{}, {}".format(line, reason_col),
                        hover_data=table.columns)
    figure.update_layout({
                "plot_bgcolor": "#F9F9F9",
                "paper_bgcolor": "#F9F9F9",
    })
    return figure

def make_user_plot(occurences=300, reason='Stop Category', groupby='User',
                    year=[2018,2020],
                    distClickData=None, barClickData=None):
    if (distClickData != None) & (barClickData != None):
        reason_index = barClickData['points'][0]['curveNumber']
        line = barClickData['points'][0]['y']
        user_index = distClickData['points'][0]['curveNumber']
    else:
        reason_index = 0
        user_index = 0
        line = 'Line 94'
        groupby = 'User'
    new_df = select_data(master,
                        occurences=occurences,
                        reason=reason,
                        year=year)
    reason_col = pd.Series(new_df.groupby(['Line',reason], sort=True)\
    ["Duration"].sum().unstack().columns)[reason_index]
    table = new_df.loc[(new_df[reason] == reason_col) &
       (new_df["Line"] == line)].groupby(groupby)\
        .filter(lambda x : (x['Duration'].count()>=10).any())\
        .groupby(groupby).filter(lambda x : (x['Duration'] < 5).all())
    user = table[groupby].unique()[user_index]
    data = new_df.loc[new_df[groupby] == user]
    data2 = new_df.loc[~(new_df[groupby] == user) &
                       (new_df[reason].isin(data[reason].unique())) &
                       (new_df['Line'].isin(data['Line'].unique()))]
    data2.iloc[:][groupby] = "All"
    data = pd.concat([data, data2])
    figure = px.box(data,
                        x=reason,
                        y="Duration",
                        color=groupby,
                        title="Downtime Profile for {}".format(user),
                        points=False,
                        hover_data=data.columns)
    figure.update_layout({
                "plot_bgcolor": "#F9F9F9",
                "paper_bgcolor": "#F9F9F9",
    })
    return figure

def make_bar_plot(occurences=300, reason='Stop Category', year=[2018,2020]):
    new_df = select_data(master,
                        occurences=occurences,
                        reason=reason,
                        year=year)
    new_df = new_df.groupby(['Line',reason], sort=True)["Duration"].sum().unstack()
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
    return figure


def create_layout(app):
    # Page layouts
    return  html.Div([
    html.Div([
        html.Div([
                html.Div(
                            [
                                html.H3(
                                    "Asset Capability",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Uptime",
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
                "Downtime category or reason:"
            ),
            dcc.Dropdown(id='uptime_category_dropdown',
                        options=[{'label': 'Stop Category', 'value': 'Stop Category'},
                                {'label': 'Stop Reason', 'value': 'Stop Reason'}],
                        value='Stop Category',
                        className="dcc_control"),

            html.P(
                "Minimum number of downtimes:"
            ),
            dcc.Input(id='uptime_occurence_filter',
                        type='number',
                        value=300,
                        className="dcc_control"),
           html.P(
               "Pareto by:"
           ),
            dcc.Dropdown(id='uptime_pareto_dropdown',
                        options=[{'label': 'Product', 'value': 'Product'},
                                {'label': 'User', 'value': 'User'}],
                        value='User',
                        className="dcc_control"),
            html.P(
                "Year filter:"
            ),
            dcc.RangeSlider(id='uptime_year_slider',
                        min=min(master["From Date/Time"]).year,
                        max=max(master["To Date/Time"]).year,
                        value=[min(master["From Date/Time"]).year,
                            max(master["To Date/Time"]).year],
                        marks={'{}'.format(i): '{}'.format(i) for i in\
                         master["From Date/Time"].dt.year.unique()},
                         className="dcc_control")
                         ],
                         className="pretty_container four columns",
                         id='cross-filter-options'),
        html.Div([
            html.Div([get_menu()],
                      # className="row container-display"
                      ),
            html.Div([
            dcc.Graph(id='uptime_bar_plot',
                      figure=make_bar_plot()
                      )
                      ],
                      className="pretty_container")
                      ],
                      className='eight columns'
                      )
                  ],
                  className='row flex-display',
                  ),
    html.Div([
        html.Div(
                    [
                        html.Div(
                            [
                                html.H5(
                                    "Uptime Drill Down"
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
            [dcc.Graph(id='uptime_dist_plot',
                      figure=make_dist_plot())],
                      className='pretty_container six columns',
                ),
        html.Div(
        [dcc.Graph(id='uptime_user_plot',
                      figure=make_user_plot())],
                      className='pretty_container six columns',
                ),
                      ],
            className='row flex-display',
            ),
            ])

if __name__ == '__main__':
    app.run_server(debug=True)
