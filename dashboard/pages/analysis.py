import dash
from dash import html
import dash_mantine_components as dmc
from ..ui import pygwalker
import pandas as pd

from ..state import core
dash.register_page(__name__, path='/analysis')


df = core.build_df(benchmarks=core.benchmarks, runners=core.runners)

layout = dmc.Container([
    dmc.Title("Analysis", order=1),
    html.Div("Analysis page content will go here"),
    pygwalker(df)
])
