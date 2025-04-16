import dash
from dash import html
import dash_mantine_components as dmc

dash.register_page(__name__, path='/runners/create')

layout = dmc.Container([
    dmc.Title("Create a benchmark", order=1),
    html.Div("Run page content will go here")
])
