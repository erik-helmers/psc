import dash
from dash import html, dcc, Input, Output, State, callback, dcc
import dash_mantine_components as dmc
from ..ui import pygwalker
import pandas as pd
from core import analysis
import plotly.express as px


from ..state import core
dash.register_page(__name__, path='/analysis')



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
    html.Div(id='pyg-roc-output'),
])



@callback(
    Output('roc-output', 'children'),
    Input('roc-runner-select', 'value'),
    Input('roc-benchmark-pos-select', 'value'),
    Input('roc-benchmark-neg-select', 'value'),
    Input('roc-explore-show-toggle', 'checked'),
)
def update_roc_output(runner_id, benchmark_pos_id, benchmark_neg_id, explore):
    if not all([runner_id, benchmark_pos_id, benchmark_neg_id]):
        return dmc.Text("Please select a runner and two benchmarks.")

    runner = core.runners.by_id(runner_id)
    benchmark_pos = core.benchmarks.by_id(benchmark_pos_id)
    benchmark_neg = core.benchmarks.by_id(benchmark_neg_id)

    df_pos = core.build_df(runner, benchmark_pos)
    df_neg = core.build_df(runner, benchmark_neg)
    df_roc = analysis.confusion_df(df_pos, df_neg)

    fig = px.line(
        df_roc,
        x='threshold',
        y=['fnr', 'fpr'],
    )

    return dcc.Graph(figure=fig)




@callback(
    Output('pyg-roc-output', 'children'),
    Input('roc-runner-select', 'value'),
    Input('roc-benchmark-pos-select', 'value'),
    Input('roc-benchmark-neg-select', 'value'),
    Input('roc-explore-show-toggle', 'checked'),
)
def update_output(runner_id, benchmark_pos_id, benchmark_neg_id, explore):
    if not all([runner_id, benchmark_pos_id, benchmark_neg_id]):
        return dmc.Text("")

    runner = core.runners.by_id(runner_id)
    benchmark_pos = core.benchmarks.by_id(benchmark_pos_id)
    benchmark_neg = core.benchmarks.by_id(benchmark_neg_id)

    df_pos = core.build_df(runner, benchmark_pos)
    df_neg = core.build_df(runner, benchmark_neg)

    df_roc = analysis.confusion_df(df_pos, df_neg)

    res_spec = r"""{"config":[{"config":{"defaultAggregated":false,"geoms":["point"],"coordSystem":"generic","limit":-1,"timezoneDisplayOffset":0},"encodings":{"dimensions":[{"fid":"benchmark","name":"benchmark","basename":"benchmark","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"ref","name":"ref","basename":"ref","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"alt","name":"alt","basename":"alt","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"expect_similar","name":"expect_similar","basename":"expect_similar","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"runner","name":"runner","basename":"runner","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"gw_mea_key_fid","name":"Measure names","analyticType":"dimension","semanticType":"nominal"}],"measures":[{"fid":"distance","name":"distance","basename":"distance","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"gw_count_fid","name":"Row count","analyticType":"measure","semanticType":"quantitative","aggName":"sum","computed":true,"expression":{"op":"one","params":[],"as":"gw_count_fid"}},{"fid":"gw_mea_val_fid","name":"Measure values","analyticType":"measure","semanticType":"quantitative","aggName":"sum"}],"rows":[{"fid":"distance","name":"distance","basename":"distance","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0}],"columns":[{"fid":"benchmark","name":"benchmark","basename":"benchmark","semanticType":"nominal","analyticType":"dimension","offset":0}],"color":[{"fid":"benchmark","name":"benchmark","basename":"benchmark","semanticType":"nominal","analyticType":"dimension","offset":0}],"opacity":[],"size":[],"shape":[],"radius":[],"theta":[],"longitude":[],"latitude":[],"geoId":[],"details":[],"filters":[],"text":[]},"layout":{"showActions":false,"showTableSummary":false,"stack":"stack","interactiveScale":false,"zeroScale":true,"size":{"mode":"full","width":320,"height":200},"format":{},"geoKey":"name","resolve":{"x":false,"y":false,"color":false,"opacity":false,"shape":false,"size":false}},"visId":"gw_AydI","name":"Results"}],"chart_map":{},"workflow_list":[{"workflow":[{"type":"view","query":[{"op":"raw","fields":["benchmark","benchmark","distance"]}]}]}],"version":"0.4.9.15"}"""
    f1_spec = r"""{"config":[{"config":{"defaultAggregated":false,"geoms":["line"],"coordSystem":"generic","limit":-1,"timezoneDisplayOffset":0},"encodings":{"dimensions":[{"fid":"threshold","name":"threshold","basename":"threshold","analyticType":"dimension","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"gw_mea_key_fid","name":"Measure names","analyticType":"dimension","semanticType":"nominal"}],"measures":[{"fid":"tn","name":"tn","basename":"tn","semanticType":"quantitative","analyticType":"measure","offset":0},{"fid":"fn","name":"fn","basename":"fn","semanticType":"quantitative","analyticType":"measure","offset":0},{"fid":"tp","name":"tp","basename":"tp","semanticType":"quantitative","analyticType":"measure","offset":0},{"fid":"fp","name":"fp","basename":"fp","semanticType":"quantitative","analyticType":"measure","offset":0},{"fid":"precision","name":"precision","basename":"precision","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"error_rate","name":"error_rate","basename":"error_rate","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"detection_rate","name":"detection_rate","basename":"detection_rate","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"false_alarm_rate","name":"false_alarm_rate","basename":"false_alarm_rate","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"f_score","name":"f_score","basename":"f_score","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"tpr","name":"tpr","semanticType":"quantitative","analyticType":"measure","basename":"tpr","dragId":"GW_Gc0lT5RC"},{"fid":"fpr","name":"fpr","semanticType":"quantitative","analyticType":"measure","basename":"fpr","dragId":"GW_MgiQ7ZjO"},{"fid":"fnr","name":"fnr","semanticType":"quantitative","analyticType":"measure","basename":"fnr","dragId":"GW_MBVSxcjG"},{"fid":"tnr","name":"tnr","semanticType":"quantitative","analyticType":"measure","basename":"tnr","dragId":"GW_wpR3v2P4"},{"fid":"gw_count_fid","name":"Row count","analyticType":"measure","semanticType":"quantitative","aggName":"sum","computed":true,"expression":{"op":"one","params":[],"as":"gw_count_fid"}},{"fid":"gw_mea_val_fid","name":"Measure values","analyticType":"measure","semanticType":"quantitative","aggName":"sum"}],"rows":[{"fid":"f_score","name":"f_score","basename":"f_score","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0}],"columns":[{"fid":"threshold","name":"threshold","basename":"threshold","analyticType":"dimension","semanticType":"quantitative","aggName":"sum","offset":0}],"color":[],"opacity":[],"size":[],"shape":[],"radius":[],"theta":[],"longitude":[],"latitude":[],"geoId":[],"details":[],"filters":[],"text":[]},"layout":{"showActions":false,"showTableSummary":false,"stack":"stack","interactiveScale":false,"zeroScale":true,"size":{"mode":"full","width":320,"height":200},"format":{},"geoKey":"name","resolve":{"x":false,"y":false,"color":false,"opacity":false,"shape":false,"size":false}},"visId":"gw_lOCK","name":"F-score"},{"config":{"defaultAggregated":false,"geoms":["line"],"coordSystem":"generic","limit":-1,"timezoneDisplayOffset":0},"encodings":{"dimensions":[{"fid":"tp","name":"tp","basename":"tp","semanticType":"quantitative","analyticType":"dimension","offset":0},{"fid":"fn","name":"fn","basename":"fn","semanticType":"quantitative","analyticType":"dimension","offset":0},{"fid":"gw_mea_key_fid","name":"Measure names","analyticType":"dimension","semanticType":"nominal"}],"measures":[{"fid":"fp","name":"fp","basename":"fp","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"tn","name":"tn","basename":"tn","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"tpr","name":"tpr","basename":"tpr","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"fpr","name":"fpr","basename":"fpr","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"fnr","name":"fnr","basename":"fnr","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"tnr","name":"tnr","basename":"tnr","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"precision","name":"precision","basename":"precision","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"error_rate","name":"error_rate","basename":"error_rate","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"detection_rate","name":"detection_rate","basename":"detection_rate","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"false_alarm_rate","name":"false_alarm_rate","basename":"false_alarm_rate","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"f_score","name":"f_score","basename":"f_score","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"threshold","name":"threshold","basename":"threshold","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"gw_count_fid","name":"Row count","analyticType":"measure","semanticType":"quantitative","aggName":"sum","computed":true,"expression":{"op":"one","params":[],"as":"gw_count_fid"}},{"fid":"gw_mea_val_fid","name":"Measure values","analyticType":"measure","semanticType":"quantitative","aggName":"sum"}],"rows":[{"fid":"tpr","name":"tpr","basename":"tpr","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0}],"columns":[{"fid":"fpr","name":"fpr","basename":"fpr","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0}],"color":[],"opacity":[],"size":[],"shape":[],"radius":[],"theta":[],"longitude":[],"latitude":[],"geoId":[],"details":[{"fid":"threshold","name":"threshold","basename":"threshold","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0}],"filters":[],"text":[]},"layout":{"showActions":false,"showTableSummary":false,"stack":"stack","interactiveScale":false,"zeroScale":true,"size":{"mode":"full","width":320,"height":200},"format":{},"geoKey":"name","resolve":{"x":false,"y":false,"color":false,"opacity":false,"shape":false,"size":false}},"visId":"gw_QtQE","name":"ROC"}],"chart_map":{},"workflow_list":[{"workflow":[{"type":"view","query":[{"op":"raw","fields":["threshold","f_score"]}]}]},{"workflow":[{"type":"view","query":[{"op":"raw","fields":["fpr","tpr","threshold"]}]}]}],"version":"0.4.9.15"}"""

    return html.Div(children=[
        pygwalker(pd.concat([df_pos, df_neg]), spec=res_spec, explore=explore),
        pygwalker(df_roc, spec=f1_spec, explore=explore),
    ])

