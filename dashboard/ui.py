from dash import html
import dangerously_set_inner_html
import pygwalker as pyg

def pygwalker(*args, explore=True, **kwargs):

    gw_mode = kwargs.get("gw_mode", None) or ( "explore" if explore else "filter_renderer" )
    kwargs["gw_mode"] = gw_mode


    walker = pyg.to_html(*args, **kwargs, spec_io_mode="rw")
    return html.Div([
       dangerously_set_inner_html.DangerouslySetInnerHtml(value=walker),
    ])
