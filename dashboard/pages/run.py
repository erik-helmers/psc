import dash
from dash import html
import dash_mantine_components as dmc

dash.register_page(__name__, path='/run')

layout = dmc.Container([
    dmc.Title("Run", order=1),
    html.Div("Run page content will go here")
])
