from pathlib import Path
import dash
from dash import html, dash_table, callback, Input, Output, State, dcc
import dash_mantine_components as dmc
import plotly.express as px
import pandas as pd
from typing import Any


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
        return file_viz(path)

    cells = cells or []
    return [div for cell in cells if (div := viz(**cell)) is not None]



def file_viz(path):
    path = core.bench_path / path
    if path.suffix in ['.txt']:
        return file_viz_txt(path)
    elif path.suffix in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
        return file_viz_img(path)


def ngrams(_bytes, n=2, with_repr=False):
    from sklearn.feature_extraction.text import CountVectorizer

    columns : Any = ["count", "x","y","z"][:n+1]

    if len(_bytes) < n: return pd.DataFrame(columns=(columns + ["repr"]) if with_repr else columns)

    vectorizer = CountVectorizer(
        analyzer='char',
        ngram_range=(n, n),
        # We just want an encoding without illegal byte sequences
        encoding="iso-8859-1",
        # We don't want any modifications on the content, especially
        # if the bytes are not text
        lowercase=False,
    )

    arr = vectorizer.fit_transform([_bytes]).toarray()[0]

    data = ([arr[v]] + [ord(c) for c in k] for k, v in vectorizer.vocabulary_.items())
    counts = pd.DataFrame(data, columns=columns)

    if with_repr:
        counts["repr"] = counts.apply(lambda x: " ".join([repr(chr(v)) for v in x[1:]]), axis=1)

    return counts



def file_viz_txt(path):
    _bytes = open(path, 'rb').read()
    # content = _bytes.decode("utf8")

    bigrams = ngrams(_bytes, with_repr=True)
    bigrams = px.scatter(bigrams, x="x", y="y", size="count", color="count", height=800, width=800, custom_data=[bigrams["repr"]])
    bigrams.update_traces(hovertemplate='%{x} %{y} <br>%{customdata[0]}')
    bigrams.update_xaxes(range=(0,255))
    bigrams.update_yaxes(range=(0,255))

    trigrams = ngrams(_bytes, n=3, with_repr=True)
    trigrams = px.scatter_3d(trigrams, x="x", y="y", z="z", size="count", color="count", height=800, width=800, custom_data=[trigrams["repr"]])
    trigrams.update_traces(hovertemplate='%{x} %{y} <br>%{customdata[0]}')

    return dmc.Stack(children=[
        dmc.Textarea(value = str(_bytes), minRows=8, maxRows=8, autosize=True),
        dcc.Graph(figure=bigrams),
        dcc.Graph(figure=trigrams),

    ])



def file_viz_img(path):
    import base64
    _bytes = open(path, 'rb').read()

    encoded_image = base64.b64encode(_bytes).decode('utf-8')

    bigrams = ngrams(_bytes, n=2, with_repr=False)
    bigrams = px.scatter(bigrams, x="x", y="y", size="count", color="count", height=800, width=800)
    bigrams.update_xaxes(range=(0,255))
    bigrams.update_yaxes(range=(0,255))

    trigrams = ngrams(_bytes, n=3, with_repr=False)
    trigrams = px.scatter_3d(trigrams, x="x", y="y", z="z", size="count", color="count", height=800, width=800)

    return dmc.Stack(children=[
        html.Img(src=f'data:image/png;base64,{encoded_image}'),
        dcc.Graph(figure=bigrams),
        dcc.Graph(figure=trigrams),
    ])
