import dash
from dash import html
import dash_mantine_components as dmc
from ..state import core

dash.register_page(__name__, path='/run')

layout = dmc.Container([
    dmc.Title("Runners", order=1),
])



runner_cards = [dmc.Card(
        children=[
            dmc.CardSection(
                dmc.Image(
                    src="https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/images/bg-8.png",
                    h=160,
                    alt="Norway",
                ),
                withBorder=True
            ),
            dmc.Group(
                [
                    dmc.Text(benchmark.name, size="md"),
                    "CTPH"
                ],
                justify="space-between",
                mt="md",
                mb="xs",
            ),
            dmc.Text(
                benchmark.description,
                size="sm",
                c="dimmed",
            ),
             dmc.Anchor(dmc.Button(
                "Details",
                variant="light",
                color="blue",
                fullWidth=True,
                mt="auto",
             ), href=f"/runners/{benchmark.id}"),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
    )
    for benchmark in core.runners
]


runner_cards.append(
    dmc.Paper(
        children=[ dmc.Anchor(
            dmc.Button("+", id="create", size="96", variant="light", c="gray", fw="250", h="100%", w="100%"),
            href="/runners/create"
        )],
        withBorder=True,
        shadow="sm",
        radius="md",
        h="100%",
    )
)

layout = dmc.Container([
    dmc.SimpleGrid(
        cols=3,
        spacing="lg",
        children=runner_cards,
        styles= {"root": {"gridAutoRows": "1fr"}}
    )
])
