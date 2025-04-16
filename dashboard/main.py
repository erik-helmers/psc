import dash
from dash import Dash
import dash_mantine_components as dmc


APP_TITLE = "Similarity Bench Suite"

app = Dash(__package__, use_pages=True, external_stylesheets=dmc.styles.ALL,
           suppress_callback_exceptions=True # Those warnings don't work well with
           )


pages = dash.page_registry

nav_links = [
    dmc.Anchor(
        page["name"],
        href=page["relative_path"]
    )
    for page in [pages["dashboard.pages.benchmarks"],pages["dashboard.pages.runners"], pages["dashboard.pages.analysis"]]
]


header = dmc.Stack(
    [
        dmc.Anchor(APP_TITLE, href="/", underline = "never", size="xl", c="black"),

        dmc.Group(
            [
                *nav_links
            ]
        )
    ],
    align="center",
    justify="center",
    gap="xs",
    h="100%",
)





layout = dmc.AppShell(
    [
        dmc.AppShellHeader(header),
        dmc.AppShellMain(dash.page_container),
    ],
    header={"height": 80},
    padding="md",
    id="appshell",
)


app.layout = dmc.MantineProvider(layout)



def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()
