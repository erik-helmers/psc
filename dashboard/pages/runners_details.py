from os import execlpe
from pathlib import Path
import dash
from dash import html, dash_table, callback, Input, Output, State, dcc
import dash_mantine_components as dmc
import plotly.express as px
import pandas as pd
from typing import Any

from ..ui import pygwalker


from ..state import core


from .runners_create import layout as layout_create_runner

dash.register_page(__name__, path_template="/runners/<runner_id>")

def layout(*, runner_id, **kwargs):
    if runner_id == "create": return layout_create_runner
    return layout_details(runner_id, **kwargs)


def layout_details(runner_id, **kwargs):
    try: runner = core.runners.by_id(runner_id)
    except KeyError: return [dmc.Text("Runner not found")]

    return html.Div([
        dcc.Location(id="runner-id"),

        dmc.Switch(
            id='runner-explore',
            label='Explore',
            checked=False,
        ),

        html.H1(f"{runner.name} ({runner.id})"),
        dcc.Markdown(runner.description),
        html.Div(id="benchmarks")
    ])


@callback(
    Output(component_id='benchmarks', component_property='children'),
    Input(component_id='runner-id', component_property='pathname'),
    Input(component_id='runner-explore', component_property='checked'),
)
def entries_table_data(runner_id, explore):
    runner_id = runner_id[runner_id.rfind('/')+1:]

    try: runner = core.runners.by_id(runner_id)
    except KeyError: return []

    if explore:
        df = core.build_df(runner, core.benchmarks)
        return [pygwalker(df)]

    out = []

    for bench in core.benchmarks:
        children = []

        children.append(html.H2( bench.name ))
        df = core.build_df(runner, bench)

        vis_spec = r"""{"config":[{"config":{"defaultAggregated":false,"geoms":["point"],"coordSystem":"generic","limit":-1,"timezoneDisplayOffset":0},"encodings":{"dimensions":[{"fid":"benchmark","name":"benchmark","basename":"benchmark","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"ref","name":"ref","basename":"ref","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"alt","name":"alt","basename":"alt","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"expect_similar","name":"expect_similar","basename":"expect_similar","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"mods","name":"mods","basename":"mods","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"runner","name":"runner","basename":"runner","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"suffix","name":"suffix","basename":"suffix","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"nb_swaps","name":"nb_swaps","basename":"nb_swaps","semanticType":"quantitative","analyticType":"dimension","offset":0},{"fid":"gw_mea_key_fid","name":"Measure names","analyticType":"dimension","semanticType":"nominal"}],"measures":[{"fid":"distance","name":"distance","basename":"distance","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"rel_size","name":"rel_size","basename":"rel_size","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"gw_count_fid","name":"Row count","analyticType":"measure","semanticType":"quantitative","aggName":"sum","computed":true,"expression":{"op":"one","params":[],"as":"gw_count_fid"}},{"fid":"gw_mea_val_fid","name":"Measure values","analyticType":"measure","semanticType":"quantitative","aggName":"sum"}],"rows":[{"fid":"distance","name":"distance","basename":"distance","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0}],"columns":[{"fid":"ref","name":"ref","basename":"ref","semanticType":"nominal","analyticType":"dimension","offset":0}],"color":[],"opacity":[],"size":[],"shape":[],"radius":[],"theta":[],"longitude":[],"latitude":[],"geoId":[],"details":[],"filters":[],"text":[]},"layout":{"showActions":false,"showTableSummary":false,"stack":"stack","interactiveScale":false,"zeroScale":true,"size":{"mode":"full","width":320,"height":200},"format":{},"geoKey":"name","resolve":{"x":false,"y":false,"color":false,"opacity":false,"shape":false,"size":false}},"visId":"gw_5XPA","name":"Distances"}],"chart_map":{},"workflow_list":[{"workflow":[{"type":"view","query":[{"op":"raw","fields":["ref","distance"]}]}]}],"version":"0.4.9.15"}"""

        print(explore)
        children.append(pygwalker(df, spec=vis_spec, explore=explore))

        out.append(html.Div(children))

    return out
