import dash
import dash_bootstrap_components as dbc
import dash_auth

# meta_tags are required for the app layout to be mobile responsive
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
server = app.server

app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# for your home PostgreSQL test table
app.server.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:123456@localhost:5432/geogps"

# auth = dash_auth.BasicAuth(
#     app,
#     {'bugsbunny': 'topsecret',
#      'pajaroloco': 'unsecreto'}
# )
