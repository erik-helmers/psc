from pathlib import Path
import dash
from dash import html, dash_table, callback, Input, Output, State, dcc
import dash_mantine_components as dmc
import plotly.express as px
import pandas as pd
from typing import Any


from ..state import core


from .runners_create import layout as layout_create_runner

dash.register_page(__name__, path_template="/runners/<runner_id>")

def layout(*, runner_id, **kwargs):
    if runner_id == "create": return layout_create_runner
    return layout_details(runner_id, **kwargs)


def layout_details(runner_id, **kwargs):
    runner = core.runners.by_id(runner_id)

    return html.Div([
        dcc.Location(id="runner-id"),
        html.H1(f"Runner {runner.id}"),

        html.P(f"{runner.name}: {runner.description}"),
    ])
