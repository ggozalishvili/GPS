import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import pathlib
from app import app
import dash_table
import dash
from datetime import datetime as dt
import dash_bootstrap_components as dbc
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
FONT_AWESOME = (
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
)

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

db = SQLAlchemy(app.server)


class Product(db.Model):
    __tablename__ = 'skip'


    plate = db.Column(db.String(40), nullable=False,primary_key=True)
    start_date_time = db.Column(db.Text, nullable=False)
    start_location = db.Column(db.Text, nullable=False)
    end_date_time = db.Column(db.Text, nullable=False)
    end_location = db.Column(db.Text, nullable=False)
    duration = db.Column(db.Text, nullable=False)
    milage = db.Column(db.Float, nullable=False)
    max_speed = db.Column(db.Integer, nullable=False)
    driver = db.Column(db.Text, nullable=False)
    fuel_consumed = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    service_center = db.Column(db.Text, nullable=False)
    region = db.Column(db.Text, nullable=False)

    def __init__(self, plate, start_date_time, start_location, end_date_time, end_location, duration, milage, max_speed, driver, fuel_consumed,
                 quantity, service_center, region):
        self.plate = plate
        self.start_date_time = start_date_time
        self.start_location=start_location
        self.end_date_time=end_date_time
        self.end_location=end_location
        self.duration=duration
        self.milage=milage
        self.max_speed=max_speed
        self.driver=driver
        self.fuel_consumed=fuel_consumed
        self.quantity=quantity
        self.service_center=service_center
        self.region=region



layout = dbc.Container([
    dcc.Interval(id='interval_pg3', interval=86400000*7, n_intervals=0),  # activated once/week or when page refreshed
    dbc.Row([
        dbc.Col(html.H3("?????????????????????????????????????????? ??????????????????????????? ??????????????????????????????(skip Trace)",
                        className='text-center text-primary mb-4'), width=12)
    ]),

    # dcc.Interval(id='interval_pg3', interval=86400000*7, n_intervals=0),  # activated once/week or when page refreshed

    dbc.Row([dbc.Col([
        html.Div(id='postgres_datatable3'),],align='center')

    ]),
    dbc.Row([
    # html.Button('Add Row', id='editing-rows-button3', n_clicks=0),
    html.Button('????????????????????????????????????', id='save_to_postgres3', n_clicks=0),
    ]),
    # Create notification when saving to excel
    html.Div(id='placeholder3', children=[]),
    dcc.Store(id="store3", data=0),
    dcc.Interval(id='interval3', interval=1000),
    ],fluid=True)

@app.callback(Output('postgres_datatable3', 'children'),
              [Input('interval_pg3', 'n_intervals')])
def populate_datatable(n_intervals):
    df = pd.read_sql_table('skip', con=db.engine)
    df = df.drop_duplicates()
    return [
        dash_table.DataTable(
            id='our-table3',
            columns=[{
                         'name': str(x),
                         'id': str(x),
                         'deletable': False,
                         'type': 'numeric',
                     } if x == 'start_date_time'
                     else {
                'name': str(x),
                'id': str(x),
                'deletable': True,
            }
                     for x in df.columns],
            data=df.to_dict('records'),
            editable=False,
            row_deletable=True,
            filter_action="native",
            sort_action="native",  # give user capability to sort columns
            sort_mode="single",  # sort across 'multi' or 'single' columns
            page_action='none',  # render all of the data at once. No paging.
            style_table={'height': '600px', 'overflowY': 'auto'},
            page_size=70,
            style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '100px', 'maxWidth': '100px'},
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'right'
                } for c in ['start_date_time']
            ]

        ),
    ]


@app.callback(
    [Output('placeholder3', 'children'),
     Output("store3", "data")],
    [Input('save_to_postgres3', 'n_clicks'),
     Input("interval3", "n_intervals")],
    [State('our-table3', 'data'),
     State('store3', 'data')],
    prevent_initial_call=True)
def df_to_csv(n_clicks, n_intervals, dataset, s):
    output = html.Plaintext("The data has been saved to your PostgreSQL database.",
                            style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
    no_output = html.Plaintext("", style={'margin': "0px"})

    input_triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    if input_triggered == "save_to_postgres3":
        s = 6
        pg = pd.DataFrame(dataset)
        pg.to_sql("skip", con=db.engine, if_exists='replace', index=False)
        return output, s
    elif input_triggered == 'interval3' and s > 0:
        s = s - 1
        if s > 0:
            return output, s
        else:
            return no_output, s
    elif s == 0:
        return no_output, s
