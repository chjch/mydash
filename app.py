from dash import Dash, html, dcc
import dash_defer_js_import as dji

# external JavaScript files
external_scripts = [
    {'src': 'https://api.tiles.mapbox.com/mapbox-gl-js/v2.6.1/mapbox-gl.js'},

]

# external CSS stylesheets
external_stylesheets = [
    {'src': 'https://api.tiles.mapbox.com/mapbox-gl-js/v2.6.1/mapbox-gl.css',
     'rel': 'stylesheet'},

]

app = Dash(
    external_scripts=external_scripts,
    external_stylesheets=external_stylesheets,
    meta_tags=[{
        'name': 'viewport',
        'content': 'width=device-width, initial-scale=1'
    }]
)

app.layout = html.Div([
    html.Div(
        className="app-header",
        children=[html.Div('Plotly Dash', className="app-header--title")]
    ),
    html.Div(
        id='map'
    ),
    html.Div(
        className='legend',
        children=[
            html.H4('Sea-level Rise Vulnerability')
        ]
    ),
    html.Article(dji.Import(src="./assets/script.js"))
])


if __name__ == '__main__':
    app.run_server()
