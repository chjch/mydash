from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output
import dash_deck
import pydeck as pdk
import pandas as pd
import json

mapbox_api_token = open('./mapbox_token.txt', mode='r').read()

DATA_URL = r"./data/building/ov_bldg.geojson"

# external CSS stylesheets
external_stylesheets = [
    {'src': 'https://api.tiles.mapbox.com/mapbox-gl-js/v2.6.1/mapbox-gl.css',
     'rel': 'stylesheet'},

]

INITIAL_VIEW_STATE = pdk.ViewState(
    latitude=27.4400739, longitude=-80.2840917, zoom=15, max_zoom=22, pitch=50, bearing=10
)

geojson_data = json.load(open(DATA_URL))

df = pd.json_normalize(geojson_data['features'])
df = df[[clm for clm in df.columns if clm.startswith('properties')]]
df.rename(
    columns=dict(zip(
        df.columns,
        [_[len('properties.'):] for _ in df.columns]
    )),
    inplace=True
)

geojson = pdk.Layer(
    "GeoJsonLayer",
    geojson_data,
    id='geojson',
    opacity=0.7,
    stroked=False,
    filled=True,
    extruded=True,
    wireframe=True,
    get_elevation="properties.NumStory * 10",
    get_fill_color=[200, 200, 200],
    get_line_color=[128, 128, 128],
    pickable=True,
    material=False,
    tooltip=True
)

# lighting = pdk.LightSettings(
#     number_of_lights=1
# )

# Add sunlight shadow to the polygons
sunlight = {
    "@@type": "_SunLight",
    "timestamp": 1564696800000,  # Date.UTC(2019, 7, 1, 22),
    "color": [255, 255, 255],
    "intensity": 1,
    "_shadow": True,
}

# ambient_light = {"@@type": "AmbientLight", "color": [255, 255, 255], "intensity": 1}
#
# lighting_effect = {
#     "@@type": "LightingEffect",
#     "shadowColor": [0, 0, 0, 0.5],
#     "ambientLight": ambient_light,
#     "directionalLights": [sunlight],
# }

r = pdk.Deck(
    layers=[geojson],
    initial_view_state=INITIAL_VIEW_STATE,
    map_provider='mapbox',
    map_style='mapbox://styles/chjch/cl5sbhze0000614k2u1v1fo3g',
    api_keys={'mapbox': mapbox_api_token},
    # effects=[lighting_effect]
    # views=[map_view]
)


def flatten_geojson_property(
        json_dict: dict, key: str, add_comma: bool = False
) -> dict:
    for feature in json_dict['features']:
        if add_comma:
            feature[f'property_{key}'] = f"{feature['properties'][key]:,}"
        else:
            feature[f'property_{key}'] = feature['properties'][key]
    return json_dict


flatten_geojson_property(geojson_data, 'bldg_cat')
flatten_geojson_property(geojson_data, 'CamaPID')
flatten_geojson_property(geojson_data, 'NumStory')
flatten_geojson_property(geojson_data, 'marketval', add_comma=True)

tooltip_html = '''
    <table> 
        <tr>
            <td><strong>Parcel ID</strong></td>
            <td>{property_CamaPID}</td>
        </tr>
        <tr>
            <td><strong>Market Value</strong></td>
            <td>{property_marketval}</td>
        </tr>
        <tr>
            <td><strong>Building Type</strong></td>
            <td>{property_bldg_cat}</td>
        </tr>
        <tr>
            <td><strong>Number Story</strong></td>
            <td>{property_NumStory}</td>
        </tr>
    </table>
'''

tooltip_style = {
    "font-size": "14px",
    "backgroundColor": "white",
    "color": "black"
}

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.Div(
        className='app-header',
        children=[
            html.Div('Ocean Village Community', className="app-header--title")
        ]
    ),
    dash_table.DataTable(
        id='buildings-datatable',
        columns=[
            {"name": _, "id": _, "deletable": True,
             "selectable": True, "hideable": True}
            if _ in ["FID", "CamaPID"]
            else {"name": _, "id": _, "deletable": True, "selectable": True}
            for _ in df.columns
        ],
        data=df.to_dict('records'),  # the contents of the table
        editable=True,               # allow editing of data inside all cells
        filter_action="native",      # allow filtering of data by user ('native') or not ('none')
        sort_action="native",        # enables data to be sorted per-column by user or not ('none')
        sort_mode="single",          # sort across 'multi' or 'single' columns
        column_selectable="multi",   # allow users to select 'multi' or 'single' columns
        row_selectable="multi",      # allow users to select 'multi' or 'single' rows
        row_deletable=True,          # choose if user can delete a row (True) or not (False)
        selected_columns=[],         # ids of columns that user selects
        selected_rows=[],            # indices of rows that user selects
        page_action="native",        # all data is passed to the table up-front or not ('none')
        page_current=0,              # page number that user is on
        page_size=10,                # number of rows visible per page
        style_cell={                 # ensure adequate header width when text is shorter than cell's text
            'minWidth': 95, 'maxWidth': 95, 'width': 95
        },
        style_cell_conditional=[     # align text columns to left. By default, they are aligned to right
            {
                'if': {'column_id': _},
                'textAlign': 'left'
            } for _ in ['CamaPID', 'bldg_cat', 'RiskLevel']
        ],
        style_data={                 # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height': 'auto'
        }
    ),
    html.Div(
        dash_deck.DeckGL(
            r.to_json(), id="deck-gl", mapboxKey=mapbox_api_token,
            tooltip={"html": tooltip_html, "style": tooltip_style},
            style={'left': 'inherit', 'top': 'inherit',
                   'height': 'inherit', 'width': 'inherit'}
        ),
        style={'width': '55%', 'height': '75%', 'display': 'inline'}
    )
])


# -------------------------------------------------------------------------------------
# Highlight selected column
@app.callback(
    Output('buildings-datatable', 'style_data_conditional'),
    [Input('buildings-datatable', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]


if __name__ == "__main__":
    app.run_server(debug=False)
