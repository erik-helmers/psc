import dash
from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from ..ui import pygwalker
import pandas as pd
from core import analysis

from ..state import core
dash.register_page(__name__, path='/analysis')


df = core.build_df(benchmarks=core.benchmarks, runners=core.runners)

layout = dmc.Container([
    dmc.Title("Analysis", order=1),

    # Selection of a runner, a benchmark with similar pairs and a benchmark with different pairs
    dmc.Select(
        id='roc-runner-select',
        label='Select a runner',
        data=[ #type: ignore
            {'label': runner.name, 'value': runner.id}
            for runner in core.runners
        ]
    ),

    dmc.Select(
        id='roc-benchmark-pos-select',
        label='Select a benchmark expected to be similar',
        data=[ #type: ignore
            {'label': benchmark.name, 'value': benchmark.id}
            for benchmark in core.benchmarks
        ]
    ),

    dmc.Select(
        id='roc-benchmark-neg-select',
        label='Select a benchmark with different pairs',
        data=[ #type: ignore
            {'label': benchmark.name, 'value': benchmark.id}
            for benchmark in core.benchmarks
        ]
    ),

    # Toggle between explore and show
    dmc.Switch(
        id='roc-explore-show-toggle',
        label='Explore',
        checked=False,
    ),

    html.Div(id='roc-output'),
])


@callback(
    Output('roc-output', 'children'),
    Input('roc-runner-select', 'value'),
    Input('roc-benchmark-pos-select', 'value'),
    Input('roc-benchmark-neg-select', 'value'),
    Input('roc-explore-show-toggle', 'checked'),
)
def update_output(runner_id, benchmark_pos_id, benchmark_neg_id, explore):
    if not all([runner_id, benchmark_pos_id, benchmark_neg_id]):
        return dmc.Text("Please select a runner and two benchmarks.")

    runner = core.runners.by_id(runner_id)
    benchmark_pos = core.benchmarks.by_id(benchmark_pos_id)
    benchmark_neg = core.benchmarks.by_id(benchmark_neg_id)

    df_pos = core.build_df(benchmarks = [benchmark_pos], runners = [runner])
    df_neg = core.build_df(benchmarks = [benchmark_neg], runners = [runner])

    df_roc = analysis.confusion_df(df_pos, df_neg)

    spec = r"""{"config":[{"config":{"defaultAggregated":false,"geoms":["auto"],"coordSystem":"generic","limit":-1,"timezoneDisplayOffset":0},"encodings":{"dimensions":[{"fid":"threshold","name":"threshold","basename":"threshold","analyticType":"dimension","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"gw_mea_key_fid","name":"Measure names","analyticType":"dimension","semanticType":"nominal"}],"measures":[{"fid":"tn","name":"tn","basename":"tn","semanticType":"quantitative","analyticType":"measure","offset":0},{"fid":"fn","name":"fn","basename":"fn","semanticType":"quantitative","analyticType":"measure","offset":0},{"fid":"tp","name":"tp","basename":"tp","semanticType":"quantitative","analyticType":"measure","offset":0},{"fid":"fp","name":"fp","basename":"fp","semanticType":"quantitative","analyticType":"measure","offset":0},{"fid":"precision","name":"precision","basename":"precision","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"error_rate","name":"error_rate","basename":"error_rate","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"detection_rate","name":"detection_rate","basename":"detection_rate","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"false_alarm_rate","name":"false_alarm_rate","basename":"false_alarm_rate","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"f_score","name":"f_score","basename":"f_score","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"gw_count_fid","name":"Row count","analyticType":"measure","semanticType":"quantitative","aggName":"sum","computed":true,"expression":{"op":"one","params":[],"as":"gw_count_fid"}},{"fid":"gw_mea_val_fid","name":"Measure values","analyticType":"measure","semanticType":"quantitative","aggName":"sum"}],"rows":[{"fid":"f_score","name":"f_score","basename":"f_score","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0}],"columns":[{"fid":"threshold","name":"threshold","basename":"threshold","analyticType":"dimension","semanticType":"quantitative","aggName":"sum","offset":0}],"color":[],"opacity":[],"size":[],"shape":[],"radius":[],"theta":[],"longitude":[],"latitude":[],"geoId":[],"details":[],"filters":[],"text":[]},"layout":{"showActions":false,"showTableSummary":false,"stack":"stack","interactiveScale":false,"zeroScale":true,"size":{"mode":"auto","width":320,"height":200},"format":{},"geoKey":"name","resolve":{"x":false,"y":false,"color":false,"opacity":false,"shape":false,"size":false}},"visId":"gw_lOCK","name":"F-score"}],"chart_map":{},"workflow_list":[{"workflow":[{"type":"view","query":[{"op":"raw","fields":["threshold","f_score"]}]}]}],"version":"0.4.9.15"}"""

    mode = "explore" if explore else "filter_renderer"

    return pygwalker(df_roc, spec=spec, gw_mode=mode)
