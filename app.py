import yaml
import dash

import dash_bootstrap_components as dbc
import plotly.express as px
import numpy as np

from dash import Dash, dcc, html, Input, Output, dash_table, ALL

from catadata.data.data import get_cata_data, get_cata_parcels, get_fresh_cata_data

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

with open("./config.yaml") as fp:
    config = yaml.load(fp, Loader=yaml.FullLoader)

cover_cols_list = list(filter(lambda c: "%cover" in c, list(get_cata_data().columns)))

parcel_id_list = html.Datalist(
    id="list-suggested-parcel-ids",
    children=[html.Option(value=str(parcel_id)) for parcel_id in get_cata_data().fid],
)

alt_parcel_id_list = html.Datalist(
    id="list-suggested-altparno",
    children=[html.Option(value=str(altparno_id)) for altparno_id in get_cata_data().ALTPARNO],
)


def cover_details(cover_column):
    if cover_column == "%cover11":
        return "Open Water"
    elif cover_column == "%cover21":
        return "Developed, Open Space"
    elif cover_column == "%cover22":
        return "Developed, Low Intensity"
    elif cover_column == "%cover23":
        return "Developed, Medium Intensity"
    elif cover_column == "%cover24":
        return "Developed, High Intensity"
    elif cover_column == "%cover31":
        return "Barren Land (Rock/Sand/Clay)"
    elif cover_column == "%cover41":
        return "Deciduous Forest"
    elif cover_column == "%cover42":
        return "Evergreen Forest"
    elif cover_column == "%cover43":
        return "Mixed Forest"
    elif cover_column == "%cover52":
        return "Shrub/Scrub"
    elif cover_column == "%cover71":
        return "Grassland/Herbaceous"
    elif cover_column == "%cover81":
        return "Pasture/Hay"
    elif cover_column == "%cover82":
        return "Cultivated Crops"
    elif cover_column == "%cover90":
        return "Woody Wetlands"
    elif cover_column == "%cover95":
        return "Emergent Herbaceous Wetlands"


form = dbc.Col(
    [
        dbc.Form(
            [
                html.H4("Parcel Info", className="form-header"),
                parcel_id_list,
                dbc.Label("Parcel ID (fid)"),
                parcel_id := dbc.Input(id="parcel_id", list="list-suggested-parcel-ids"),
                dbc.FormText("The ID of the parcel."),
                switches := dbc.Checklist(
                    options=[dict(label="Center On Parcel", value=1)],
                    value=[1],
                    id="switches-input",
                    switch=True,
                ),
                alt_parcel_id_list,
                dbc.Label("Alternate Parcel #"),
                alt_par_no := dbc.Input(id="alt-par-no", list="list-suggested-altparno"),
                dbc.FormText("The ALTPARNO of the parcel."),
                html.H4("% Cover Adjustments", className="form-header"),
                reset_button := dbc.Button("reset", id="reset-cover"),
                *[
                    html.Div(
                        [
                            dbc.Label(cover_col),
                            dbc.FormText(cover_details(cover_col)),
                            dcc.Slider(
                                id={"type": "cover-slider", "index": cover_col},
                                min=0,
                                max=1,
                                step=0.2,
                            ),
                        ],
                        className="slider-container",
                    )
                    for cover_col in cover_cols_list
                ],
            ],
        )
    ],
    width=2,
    style={"overflowY": "scroll", "height": "90vh"},
)

map_options = dbc.Row(
    [
        html.H4("Map Options", className="form-header"),
        dbc.Col(
            [
                dbc.Label("Map Style"),
                map_style := dcc.Dropdown(
                    id="map-style-select",
                    value="carto-positron",
                    options=[
                        dict(
                            label="open-street-map",
                            value="open-street-map",
                        ),
                        dict(label="carto-positron", value="carto-positron"),
                        dict(
                            label="carto-darkmatter",
                            value="carto-darkmatter",
                        ),
                        dict(label="stamen-terrain", value="stamen-terrain"),
                        dict(label="stamen-toner", value="stamen-toner"),
                        dict(
                            label="stamen-watercolor",
                            value="stamen-watercolor",
                        ),
                    ],
                ),
            ]
        ),
        dbc.Col(
            [
                dbc.Label("Colorscale"),
                color_scale := dcc.Dropdown(
                    id="color-scale-select",
                    value="reds",
                    options=[
                        dict(label=colorscale, value=colorscale)
                        for colorscale in px.colors.named_colorscales()
                    ],
                ),
            ]
        ),
    ]
)

app.layout = dbc.Container(
    fluid=True,
    children=[
        memory_storage := dcc.Store(id="memory"),
        local_storage := dcc.Store(id="local", storage_type="local"),
        session_storage := dcc.Store(id="session", storage_type="session"),
        dbc.Row(children=[html.H1("Catawba River Analysis", style={"textAlign": "center"})]),
        dbc.Row(
            [
                form,
                dbc.Col(
                    [
                        map_options,
                        dbc.Row(
                            [
                                html.H4("Selected Parcel", className="form-header"),
                                dash_table.DataTable(
                                    id="parcel-info", style_table={"overflowX": "auto"}
                                ),
                            ]
                        ),
                        dcc.Graph(id="map"),
                    ],
                    width=10,
                ),
            ]
        ),
    ],
)


@app.callback(
    Output({"type": "cover-slider", "index": ALL}, "value"),
    [Input(reset_button, "n_clicks"), Input(parcel_id, "value")],
)
def reset_covers(reset, parcel_id):
    print(f"click {reset}")
    print(f"parcel_id {parcel_id}")

    if parcel_id != None:
        cata_data = get_cata_data()
        parcel = cata_data[cata_data.fid == int(parcel_id)].iloc[0]
        values = [parcel[cover_col] for cover_col in cover_cols_list]

        return values

    return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


@app.callback(
    Output("parcel-info", "data"),
    Output("map", "figure"),
    [
        Input(parcel_id, "value"),
        Input({"type": "cover-slider", "index": ALL}, "value"),
        Input(map_style, "value"),
        Input(color_scale, "value"),
        Input(switches, "value"),
    ],
)
def parcel_info(parcel_id, slider_values, map_style, color_scale, switch_values):

    center_on_parcel = True if 1 in switch_values else False

    # Zip the list of cover columns and the slider values
    # Looks like [(%cover11, 0.6), ...]
    cover_values = zip(cover_cols_list, slider_values)

    cover_config = config["cover_columns"]
    cata_parcels = get_cata_parcels()
    cata_data = get_cata_data()

    # Update Cover Values based on sliders
    for cover in cover_values:
        cover_col, slider_value = cover

        if slider_value:
            cata_data.loc[cata_data.fid == int(parcel_id), cover_col] = slider_value

    # Calculate risk of %cover* based on cover_config in config.yaml
    for cover in cover_config:
        # get %cover column
        df_col = cata_data[cover["column"]]

        # Create a condition list
        # looks something like [df.%cover22 < 0.2, df.%cover22 < 0.4, df.%cover22 < 0.6]
        condlist = [df_col < threshold["check"] for threshold in cover["thresholds"]]

        # Create a choice list
        # Looks something like [0, 1, 2, 3]
        choicelist = [threshold["value"] for threshold in cover["thresholds"]]

        # Assign risk
        cata_data[cover["new_column"]] = np.select(condlist, choicelist, default=cover["default"])

    # Get a list of all risk* columns
    risk_columns = list(filter(lambda c: "risk" in c, cata_data.columns))

    # Calculate Cumulutive Risk
    cata_data["cum_risk"] = cata_data[risk_columns].sum(axis=1)

    # Normalize cumulutive risk
    cata_data["cum_risk_normalized"] = (cata_data.cum_risk - cata_data.cum_risk.min()) / (
        cata_data.cum_risk.max() - cata_data.cum_risk.min()
    )

    # Get the Latitude and Longitude of the centroid of the selected parcel
    center = None
    zoom = None
    if parcel_id and center_on_parcel:
        parcel = cata_parcels[cata_parcels.fid == parcel_id]
        centroid = parcel.iloc[0].geometry.centroid
        center = {"lat": centroid.y, "lon": centroid.x}
        zoom = 15
    else:
        center = {"lat": 35.666930, "lon": -82.097059}
        zoom = 11

    # Set Mapbox Token
    # px.set_mapbox_access_token(mapbox_access_token)

    # Create geo plot
    fig = px.choropleth_mapbox(
        cata_data,
        geojson=cata_parcels,
        locations="fid",
        featureidkey="properties.fid",
        color="cum_risk_normalized",
        color_continuous_scale=color_scale,
        range_color=(0, 1),
        labels={"cum_risk_normalized": "risk"},
        mapbox_style=map_style,
        opacity=0.5,
        zoom=zoom,
        center=center,
        # height=900,
        hover_data=["ALTPARNO"],
    )

    if not parcel_id:
        return [], fig

    return (
        cata_data[cata_data.fid == int(parcel_id)][["fid"] + cover_cols_list].to_dict("records"),
        fig,
    )


if __name__ == "__main__":
    app.run_server(debug=True)
