# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
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

opp = pd.read_csv('assets/opportunity.csv', index_col=[0,1,2,3])
annual_operating = pd.read_csv('assets/annual.csv')
quantiles = np.arange(50,96,1)
quantiles = quantiles*.01
quantiles = np.round(quantiles, decimals=2)
dataset = opp.sort_index()
lines = opp.index.get_level_values(1).unique()

# app = dash.Dash(
#     __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
#      external_stylesheets=[dbc.themes.BOOTSTRAP]
# )
# server = app.server

def make_animate_opportunity():
    # make figure
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }
    duration_bench = 150

    # fill in most of layout
    fig_dict["layout"]["plot_bgcolor"]="#F9F9F9"
    # fig_dict["layout"]["paper_bgcolor"]="#F9F9F9"
    fig_dict["layout"]["barmode"] = "stack"
    fig_dict["layout"]["xaxis"] = {"title": "Production"}
    fig_dict["layout"]["yaxis"] = {"title": "Line"}
    fig_dict["layout"]["hovermode"] = "closest"
    fig_dict["layout"]["sliders"] = {
        "args": [
            "transition", {
                "duration": duration_bench,
                "easing": "cubic-in-out"
            }
        ],
        "initialValue": str(quantiles[0]),
        "plotlycommand": "animate",
        "values": quantiles,
        "visible": True
    }

    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": duration_bench + 100, "redraw": False},
                                    "fromcurrent": True, "transition": {"duration": duration_bench - 100,
                                                                        "easing": "quadratic-in-out"}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                      "mode": "immediate",
                                      "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }
    ]

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "performance quantile:",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": duration_bench - 100, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    # make data
    column='Net Quantity Produced'
    quantile = 0.9
    groupby = 'Line'
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
        data_dict = {
            "x":data[col],
            "y":[str(i) for i in data.index],
            "name": col,
            "orientation": "h",

        }
        fig_dict["data"].append(go.Bar(data_dict))

    # make frames
    for quantile in quantiles:
        frame = {"data": [], "name": str(quantile)}
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
            data_dict = {
                "x":data[col],
                "y":[str(i) for i in data.index],
                "name": col,
                "orientation": "h",

            }
            frame["data"].append(go.Bar(data_dict))

        fig_dict["frames"].append(frame)
        slider_step = {"args": [
            [quantile],
            {"frame": {"duration": duration_bench - 100, "redraw": False},
             "mode": "immediate",
             "transition": {"duration": duration_bench - 100}}
        ],
            "label": quantile,
            "method": "animate"}
        sliders_dict["steps"].append(slider_step)


    fig_dict["layout"]["sliders"] = [sliders_dict]

    fig = go.Figure(fig_dict)
    return fig

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Link", href="#")),
        dbc.DropdownMenu(
            nav=True,
            in_navbar=True,
            label="Menu",
            children=[
                dbc.DropdownMenuItem("Entry 1"),
                dbc.DropdownMenuItem("Entry 2"),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Entry 3"),
            ],
        ),
    ],
    brand="MFG Analytic",
    brand_href="http://mfganalytic.com",
    sticky="top",
)

body = html.Div([
    html.Div([get_menu()],
                  className="row container-display"),
dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2("The Hidden Factory"),
                        dcc.Markdown(
                            """\

**Key Questions:**
+ What hidden production is available with improvements in rate, yield and
downtime?
+ What are reasonable performance goals for the given lines and product
portfolio?


Additional capacity is computed from historic performance metrics. Ex: the
annualized production capacity for p75 (opperating at
75% performance) represents 164M additional units of production; or a 7.9%
increase in production from current opperating performance."""
                        ),
                        dbc.Button("View details", color="secondary",
                                    href="http://featherstone.herokuapp.com"),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        # html.H2("Graph"),
                        dcc.Graph(id='animate_opportunity',
                                  figure=make_animate_opportunity())],

                        # dcc.Graph(
                        #     figure={"data": [{"x": [1, 2, 3], "y": [1, 4, 9]}]}
                        # ),

                ),
            ],

        )
    ],
    className="mt-5",

)],
className="pretty_container",
style={'horizontal-align': 'middle'},)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def create_layout(app):
    return html.Div([body])

# app.layout = create_layout(app)

if __name__=="__main__":
    app.run_server(debug=True)
