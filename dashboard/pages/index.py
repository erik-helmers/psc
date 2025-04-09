import dash
from dash import html
import dash_mantine_components as dmc

dash.register_page(__name__, path='')

layout = dmc.Container([
    dmc.Title("Home", order=1),
    html.Div("TODO")
])
