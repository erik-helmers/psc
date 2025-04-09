import dash
from dash import html, dash_table, callback, Input, Output, State, dcc
import dash_mantine_components as dmc


from ..state import core

from .benchmarks_create import layout as layout_create_benchmark

dash.register_page(__name__, path_template="/benchmarks/<bench_id>")

def layout(*, bench_id, **kwargs):
    if bench_id == "create": return layout_create_benchmark
    return layout_details(bench_id, **kwargs)


def layout_details(bench_id, **kwargs):
    bench = core.benchmarks[0]

    return html.Div([
        dcc.Store("bench-id", storage_type="session", data=bench.id),
        html.H1(f"Benchmark {bench.id}"),
        html.P("- aperçu des fichiers et diverses analyses"),
        html.P("- aperçu des resultats selon les différents runners"),

        html.P(f"{bench.name}: {bench.description}"),
        entries_table(bench),
        html.Div(id="cell-viz")
    ])


def entries_table(bench):
    return html.Div([
        dmc.MultiSelect(
            id="entries-runner-cols",
            placeholder="Runners",
            value=[],
            data=[{"value": r.id, "label": r.name} for r in core.runners], #type: ignore
        ),
        dash_table.DataTable(
            id = "entries-table",
            sort_action='native',

            page_action='native',
            page_current= 0,
            page_size= 10,
        )
    ])

@callback(
    Output(component_id='entries-table', component_property='columns'),
    Output(component_id='entries-table', component_property='data'),
    Input(component_id='entries-runner-cols', component_property='value'),
    State(component_id='bench-id', component_property='data'),
)
def entries_table_data(runners, bench_id):
    bench = core.benchmarks.by_id(bench_id)
    runners = core.runners.by_ids(runners)
    df = core.build_df(entries=bench.entries, runners=runners)

    print(runners)
    if "runner" in df.columns:
        df = df.pivot(index=["ref", "alt"], columns="runner", values="distance").reset_index()

    df["id"] = df.index
    df.set_index('id', inplace=True, drop=False)
    data = df.to_dict('records')
    columns =[{"name": i, "id": i} for i in df.columns if i != "id"]

    return columns, data


@callback(
    Output(component_id='cell-viz', component_property='children'),
    Input(component_id='entries-table', component_property='selected_cells'),
    State(component_id='bench-id', component_property='data'),
)
def cell_viz(cells, bench_id):
    bench = core.benchmarks.by_id(bench_id)

    def viz(row_id, column_id, **kwargs):
        if column_id not in ["ref", "alt"]:
            return html.Div(f"{column_id}: {row_id}")
        path = getattr(bench.entries[row_id], column_id)
        return html.P(f"{path}")


    cells = cells or []
    return [div for cell in cells if (div := viz(**cell)) is not None]
