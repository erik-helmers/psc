from dash import html
import dangerously_set_inner_html
import pygwalker as pyg
from pandas import DataFrame

def pygwalker(df: DataFrame, *args, explore=True, **kwargs):

    gw_mode = kwargs.get("gw_mode", None) or ( "explore" if explore else "filter_renderer" )
    kwargs["gw_mode"] = gw_mode

    if "mods" in df.columns: df = df.drop(columns=["mods"])

    walker = pyg.to_html(df, *args, **kwargs, spec_io_mode="rw")
    return html.Div([
       dangerously_set_inner_html.DangerouslySetInnerHtml(value=walker),
    ])
