import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import pathlib
import sqlalchemy
from sqlalchemy import create_engine, MetaData, select, Table
from app import app
import dash_table
import dash
from datetime import datetime as dt
import dash_bootstrap_components as dbc

# app requires "pip install psycopg2" as well

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
FONT_AWESOME = (
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
)

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()



def read_data():

    engine = sqlalchemy.create_engine('postgresql://postgres:123456@localhost:5432/geogps')
    metadata = MetaData()
    connection = engine.connect()

    #reisebi query
    reisebi_table = Table('reis', metadata, autoload=True,
                          autoload_with=engine)
    stmt_reisebi = select([reisebi_table])
    results_reisebi = connection.execute(stmt_reisebi).fetchall()
    reisebi = pd.DataFrame(results_reisebi)
    reisebi.columns = ['id', 'plate', 'start_date_time', 'start_location', 'end_date_time', 'end_location', 'duration', 'milage',
                       'max_speed',
                       'driver', 'fuel_consumed', 'quantity']
    del reisebi['id']


    #skip query
    skip_table = Table('skip', metadata, autoload=True,
                          autoload_with=engine)
    stmt_skip = select([skip_table.columns.plate,skip_table.columns.start_date_time])
    results_skip = connection.execute(stmt_skip).fetchall()
    skip = pd.DataFrame(results_skip)
    skip.columns = ['plate', 'start_date_time']

    # sc mapping
    sc_mapping_table = Table('sc_mapping', metadata, autoload=True,
                       autoload_with=engine)
    stmt_sc_mapping = select([sc_mapping_table])
    results_sc_mapping = connection.execute(stmt_sc_mapping).fetchall()
    sc_mapping = pd.DataFrame(results_sc_mapping)
    sc_mapping.columns = ['plate', 'service_center','region']


    reisebi['end_date_time'] = pd.to_datetime(reisebi['end_date_time'], format='%d.%m.%Y %H:%M:%S')
    reisebi['start_date_time'] = pd.to_datetime(reisebi['start_date_time'], format='%d.%m.%Y %H:%M:%S')
    # eco['start_date_time'] = pd.to_datetime(reisebi['start_date_time'], format='%d.%m.%Y %H:%M:%S')
    skip['start_date_time'] = pd.to_datetime(skip['start_date_time'], format='%Y.%m.%dT%H:%M:%S')
    reisebi_ag_data = reisebi.merge(sc_mapping, on='plate', how='left')


    skipped = skip.drop_duplicates()

    data_reisebi = (
        reisebi_ag_data.merge(skipped,
                      on=['plate', 'start_date_time'],
                      how='left',
                      indicator=True)
            .query('_merge == "left_only"')
            .drop(columns='_merge')
    )
    reisebi_final_data = data_reisebi.merge(sc_mapping, on='plate', how='left')
    reisebi_final_data['id'] = reisebi_final_data['plate']
    reisebi_final_data.set_index('id', inplace=True, drop=False)
    return data_reisebi, skipped



def update_read():
    global reisebi_data, skip_trace
    reisebi_data, skip_trace = read_data()
    print("reading done")


reisebi_data, skip_trace = read_data()


layout = dbc.Container([
    dcc.Interval(id='interval_pg', interval=86400000*7, n_intervals=0),  # activated once/week or when page refreshed
    html.Br(),
    dbc.Row([
        dbc.Col([dcc.DatePickerRange(
                id='my-date-picker-range',  # ID to be used for callback
                calendar_orientation='horizontal',  # vertical or horizontal
                day_size=39,  # size of calendar image. Default is 39
                end_date_placeholder_text="Return",  # text that appears when no end date chosen
                with_portal=False,  # if True calendar will open in a full screen overlay portal
                first_day_of_week=0,  # Display of calendar when open (0 = Sunday)
                reopen_calendar_on_clear=True,
                is_RTL=False,  # True or False for direction of calendar
                clearable=True,  # whether or not the user can clear the dropdown
                number_of_months_shown=1,  # number of months shown when calendar is open
                min_date_allowed=dt(2021, 6, 1),  # minimum date allowed on the DatePickerRange component
                max_date_allowed=dt(2021, 6, 30),  # maximum date allowed on the DatePickerRange component
                initial_visible_month=dt(2021, 6, 1),  # the month initially presented when the user opens the calendar
                start_date=dt(2021, 7, 1).date(),
                end_date=dt(2021, 8, 30).date(),
                display_format='MMM Do, YY',  # how selected dates are displayed in the DatePickerRange component.
                month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
                minimum_nights=2,  # minimum number of days between start and end date
                persistence=True,
                persisted_props=['start_date'],
                persistence_type='session',  # session, local, or memory. Default is 'local'
                updatemode='singledate'  # singledate or bothdates. Determines when callback is triggered
            ),
        html.Br(),
        dcc.Dropdown(
                id='region_dropdown',
                options=[{'label': s, 'value': s} for s in sorted(reisebi_data['region'].dropna().unique())],
                # multi=True,
                value='???????????????',
                clearable=False
                    ),
        dcc.Dropdown(id='sc_dropdown', options=[], multi=True)
            ]
            ,width={'size':2,'offset':0}),


        ],no_gutters=False,justify='left',style={'marginBottom': '2em'}),
html.Br(),
dbc.Row([

dbc.Col([
            html.Br(),
            html.H3("???????????????????????? ?????????????????????????????? ???????????????????????????????????? ???????????????????????? ",
                        className='text-center text-primary mb-4'),
            html.Br(),
            dash_table.DataTable(
                id='cars_details_table',
                columns=[
                    {"name": i, "id": i, "deletable": False, "selectable": False, "hideable": False}
                    if i == "plate" or i == "start_date_time" or i == "service_center"
                    else {"name": i, "id": i, "deletable": True, "selectable": False}
                    for i in reisebi_data.columns
                ],
                # data=reisebi_ag_data.to_dict('records'),  # the contents of the table
                editable=False,  # allow editing of data inside all cells
                cell_selectable="False",
                filter_action="none",  # allow filtering of data by user ('native') or not ('none')
                sort_action="none",  # enables data to be sorted per-column by user or not ('none')
                sort_mode="single",  # sort across 'multi' or 'single' columns
                # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                row_selectable="multi",  # allow users to select 'multi' or 'single' rows
                row_deletable=True,  # choose if user can delete a row (True) or not (False)
                selected_columns=[],  # ids of columns that user selects
                selected_rows=[],  # indices of rows that user selects
                page_action="native",  # all data is passed to the table up-front or not ('none')
                fixed_rows={'headers': True},
                page_current=0,  # page number that user is on
                style_table={'height': '500px', 'overflowY': 'auto'},
                page_size=70,  # number of rows visible per page
                style_cell={  # ensure adequate header width when text is shorter than cell's text
                    'minWidth': 95, 'maxWidth': 105, 'width': 105
                },
                style_cell_conditional=[  # align text columns to left. By default they are aligned to right
                    {
                        'if': {'column_id': c},
                        'textAlign': 'left'
                    } for c in ['start_location', 'end_location']
                ],
                style_data={  # overflow cells' content into multiple lines
                    'whiteSpace': 'normal',
                    'height': 'auto'
                }
            )
        ],align='center')

    ]),
    dbc.Row([
        html.Button('????????????????????????????????????', id='save_to_csv', n_clicks=0),
        html.A(html.Button('???????????????????????????'), href='/apps/main'),
        # Create notification when saving to excel
        html.Div(id='placeholder', children=[]),
        dcc.Store(id="store", data=0),
        dcc.Interval(id='interval', interval=1000)
    ], style={'marginBottom': '3em'}),

    ],fluid=True)


@app.callback(
    Output('sc_dropdown', 'options'),
    Input('region_dropdown', 'value'),
)
def get_sc_options(region_dropdown):
    region_un = reisebi_data[reisebi_data['region'] == region_dropdown]
    return [{'label':i, 'value':i} for i in sorted(region_un.service_center.unique())]


@app.callback(
    Output('sc_dropdown', 'value'),
    Input('sc_dropdown', 'options'),
)
def get_sc(sc_drop):
    return [x['value'] for x in sc_drop]

@app.callback(
    Output(component_id='cars_details_table', component_property='data'),
    Input(component_id='region_dropdown', component_property='value'),
    Input(component_id='sc_dropdown', component_property='value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input('interval_pg', 'n_intervals')
)
def update_rows(selected_region, selected_sc, start, end,n_intervals):
    data = reisebi_data[(reisebi_data.region == selected_region) & (reisebi_data.service_center.isin(selected_sc)) & ((reisebi_data.start_date_time >= start) & (reisebi_data.start_date_time <= end))]
    return data.to_dict('records')

@app.callback(
    [Output('placeholder', 'children'),
     Output("store", "data")],
    [Input('save_to_csv', 'n_clicks'),
     Input("interval", "n_intervals"),
    Input('cars_details_table', 'derived_virtual_selected_rows')],
    [State('cars_details_table', 'data'),
     State('store', 'data')],
)
def df_to_csv(n_clicks, n_intervals,slctd_row_indices, dataset, s):
    output = html.Plaintext("The data has been saved.Please refresh the page to see changes",
                            style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
    no_output = html.Plaintext("", style={'margin': "0px"})
    input_triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if input_triggered == "save_to_csv":
        a = slctd_row_indices
        b = dataset
        c = [b[i] for i in a]
        df = pd.DataFrame(c)
        s = 20
        skip_trace = df[["plate", "start_date_time",'start_location', 'end_date_time', 'end_location', 'duration', 'milage',
                       'max_speed',
                       'driver', 'fuel_consumed', 'quantity','service_center','region']]
        # skip_trace.to_csv("skip_trace.csv", mode='a', header=False)
        #SQL connection
        engine = sqlalchemy.create_engine('postgresql://postgres:123456@localhost:5432/geogps')
        metadata = MetaData()
        connection = engine.connect()
        skip_trace.to_sql('skip', engine, if_exists='append', index=False)
        update_read()
        return output, s
    elif input_triggered == 'interval' and s > 0:
        s = s-1
        if s > 0:
            return output, s
        else:
            return no_output, s
    elif s == 0:
        return no_output, s





