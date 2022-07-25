import dash
import dash_leaflet as dl
import dash_html_components as html

from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

MAP_ID = "map-id"
POLYLINE_ID = "polyline-id"
POLYGON_ID = "polygon-id"

dummy_pos = [0, 0]
dlatlon2 = 1e-6  # Controls tolerance of closing click

app = dash.Dash()
app.layout = html.Div([
    dl.Map(id=MAP_ID, center=[57.671667, 11.980833], zoom=16, children=[
        dl.TileLayer(),  # Map tiles, defaults to OSM
        dl.Polyline(id=POLYLINE_ID, positions=[dummy_pos]),  # Create a polyline, cannot be empty at the moment
        dl.Polygon(id=POLYGON_ID, positions=[dummy_pos]),  # Create a polygon, cannot be empty at the moment
    ], style={'width': '1000px', 'height': '500px'}),
])


@app.callback([Output(POLYLINE_ID, "positions"), Output(POLYGON_ID, "positions")],
              [Input(MAP_ID, "click_lat_lng")],
              [State(POLYLINE_ID, "positions")])
def update_polyline_and_polygon(click_lat_lng, positions):
    if click_lat_lng is None or positions is None:
        raise PreventUpdate()
    # On first click, reset the polyline.
    if len(positions) == 1 and positions[0] == dummy_pos:
        return [click_lat_lng], [dummy_pos]
    # If the click is close to the first point, close the polygon.
    dist2 = (positions[0][0] - click_lat_lng[0]) ** 2 + (positions[0][1] - click_lat_lng[1]) ** 2
    if dist2 < dlatlon2:
        return [dummy_pos], positions
    # Otherwise, append the click position.
    positions.append(click_lat_lng)
    return positions, [dummy_pos]


if __name__ == '__main__':
    app.run_server(debug=True)