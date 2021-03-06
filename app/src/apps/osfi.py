import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd

import plotly.graph_objects as go

from app import app
from utils.organization_chart import oc
from utils.osfi_handler import oh
from dash.dependencies import Input, Output

from components.html_components import build_figure_container, build_table_container


def get_pie(data, column):
    fig = go.Figure(data=[go.Pie(labels=data["Nom du bien"], values=data[column], hole=0.3)])
    fig.update_layout(plot_bgcolor="white", template="plotly_white", margin={"t": 30, "r": 30, "l": 30})
    return fig


def get_emissions_timeseries(data, column):
    biens = data["Nom du bien"].unique()
    fig = go.Figure()
    for bien in biens:
        plot_data = data.loc[data["Nom du bien"] == bien]
        fig.add_trace(
            go.Scatter(
                name=bien,
                x=plot_data["Date"].astype(str),
                y=plot_data[column].values,
                mode="lines+markers",
                line=dict(width=3),
            )
        )
    fig.update_layout(
        plot_bgcolor="white", template="plotly_white", margin={"t": 30, "r": 30, "l": 30}  # , xaxis=xaxis_format
    )
    return fig


layout = html.Div(
    [
        dbc.Row(
            dbc.Col(
                build_table_container(title="Liste de biens", id="osfi-all-data-table", footer="Explications..."),
                width=12,
                style={"textAlign": "left"},
            )
        ),
        dbc.Row(
            dbc.Col(
                build_figure_container(
                    title="Emission electricité par batiment", id="emission-electricity-pie", footer="Explications..."
                ),
                width=12,
            )
        ),
        dbc.Row(
            dbc.Col(
                build_figure_container(
                    title="Emission gaz par batiment", id="emission-gas-pie", footer="Explications..."
                ),
                width=12,
            )
        ),
        dbc.Row(
            dbc.Col(
                build_figure_container(
                    title="Évolution temporelles des émissions (électricité)",
                    id="electricity_time_series",
                    footer="Explications...",
                ),
                width=12,
            )
        ),
        dbc.Row(
            dbc.Col(
                build_figure_container(
                    title="Évolution temporelles des émissions (gaz)", id="gaz_time_series", footer="Explications..."
                ),
                width=12,
            )
        ),
    ]
)


@app.callback(
    [
        Output("osfi-all-data-table", "columns"),
        Output("osfi-all-data-table", "row_selectable"),
        Output("osfi-all-data-table", "data"),
    ],
    [Input("dashboard-selected-entity", "children")],
)
def fill_dash_table_with_buildings(selected_entity):
    service = oc.get_entity_by_id(selected_entity)
    data = oh.get_structure_data(service.code_osfi)
    columns_to_keep = ["Nom du bien", "Building type", "Adresse", "Code postal", "Ville", "Departement"]
    columns = [{"name": i, "id": i} for i in columns_to_keep]
    row_selectable = "multi"
    buildings = data[columns_to_keep].drop_duplicates()
    data_to_return = buildings.to_dict("records")
    return columns, row_selectable, data_to_return


@app.callback(
    [
        Output("emission-electricity-pie", "figure"),
        Output("emission-gas-pie", "figure"),
        Output("electricity_time_series", "figure"),
        Output("gaz_time_series", "figure"),
    ],
    [
        Input("dashboard-selected-entity", "children"),
        Input("osfi-all-data-table", "selected_rows"),
        Input("osfi-all-data-table", "data"),
    ],
)
def update_graphs_selected(selected_entity, selected_rows, buildings):
    entity = oc.get_entity_by_id(selected_entity)
    data = oh.get_structure_data(entity.code_osfi)
    # If no rows are selected, we are displaying all of them
    # Might seem a bit conter intuitive.
    if selected_rows is None or len(selected_rows) == 0:
        data_to_display = pd.DataFrame(data)
    else:
        biens = [buildings[int(i)] for i in selected_rows]
        biens = pd.DataFrame(biens)
        codes = biens["Nom du bien"]
        data_to_display = data[data["Nom du bien"].isin(codes)]
        data_to_display = pd.DataFrame(data_to_display)
    electricity_pie_graph = get_pie(data_to_display, "emission_electricity")
    gas_pie_graph = get_pie(data_to_display, "emission_gaz")
    electricity_time_series = get_emissions_timeseries(data_to_display, "emission_electricity")
    gaz_time_series = get_emissions_timeseries(data_to_display, "emission_gaz")
    return electricity_pie_graph, gas_pie_graph, electricity_time_series, gaz_time_series
