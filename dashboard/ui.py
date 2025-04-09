from dash import html
import dangerously_set_inner_html
import pygwalker as pyg

def pygwalker(*args, **kwargs):
    walker = pyg.to_html(*args, **kwargs, spec_io_mode="rw")
    return html.Div([
       dangerously_set_inner_html.DangerouslySetInnerHtml(value=walker),
    ])
