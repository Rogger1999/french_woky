import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import json
import os
from pathlib import Path
from flask import Flask
from learning import display_learning_content

# Initialize the Flask server
server = Flask(__name__)

# Initialize the Dash app
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "French-German Vocabulary Learning"
app.config.suppress_callback_exceptions = True

# Define the data directory
DATA_DIR = Path("data")

# Function to load all vocabulary files
def get_available_files():
    return sorted([f.stem for f in DATA_DIR.glob("voca*.json")])

# Function to load vocabulary data from a specific file
def load_vocabulary(filename):
    with open(DATA_DIR / f"{filename}.json", 'r', encoding='utf-8') as file:
        return json.load(file)

# Function to load all vocabulary data
def load_vocabulary_data():
    vocab_data = {}
    for file in get_available_files():
        vocab_data.update(load_vocabulary(file))
    return vocab_data

# Layout of the app
app.layout = html.Div([
    dbc.NavbarSimple(
        brand="French-German Vocabulary Learning",
        brand_href="#",
        color="primary",
        dark=True,
    ),
    html.Div(id='file-selection-container', className="mt-3 mb-3", children=[
        html.H6("Select Vocabulary File:", className="mb-2"),
        html.Div([
            dbc.Button(file, id=f"file-btn-{file}", color="secondary", 
                      size="sm", className="me-1 mb-1")
            for file in ["ALL"] + get_available_files()
        ])
    ], style={"textAlign": "center"}),
    html.Div(id='option-container', className="mt-3 mb-3"),
    html.Div(id='content-container'),
    
    # Hidden stores to keep track of state
    dcc.Store(id="direction-store", data="fr-de"),
    dcc.Store(id="file-store"),
    
    # Hidden div for storing intermediate data
    html.Div(id='hidden-div', style={'display': 'none'})
])

# Callback for file selection - with highlighting selected file
@callback(
    [Output('file-store', 'data'),
     Output('option-container', 'children'),
     Output('content-container', 'children'),
     Output('file-selection-container', 'children')],
    [Input(f"file-btn-{file}", "n_clicks") for file in ["ALL"] + get_available_files()],
    [State('direction-store', 'data')],
    prevent_initial_call=True
)
def handle_file_selection(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    selected_file = button_id.replace("file-btn-", "")
    
    # Get the current direction (last arg)
    direction = args[-1]
    
    # Load vocabulary data
    if selected_file == "ALL":
        vocab_data = load_vocabulary_data()
    else:
        vocab_data = load_vocabulary(selected_file)
    
    # Create file buttons with selected one highlighted
    files = ["ALL"] + get_available_files()
    file_buttons = []
    for file in files:
        if file == selected_file:
            file_buttons.append(
                dbc.Button(file, id=f"file-btn-{file}", color="primary", 
                          size="sm", className="me-1 mb-1")
            )
        else:
            file_buttons.append(
                dbc.Button(file, id=f"file-btn-{file}", color="secondary", 
                          size="sm", className="me-1 mb-1")
            )
    
    updated_file_container = html.Div([
        html.H6("Select Vocabulary File:", className="mb-2"),
        html.Div(file_buttons)
    ], style={"textAlign": "center"})
    
    # Learning mode - direction options
    options = html.Div([
        html.Div([
            html.H6("Language Direction:", className="mt-2 mb-2"),
            dbc.ButtonGroup([
                dbc.Button("FR → DE", id="fr-de-btn", color="success", className="me-1"),
                dbc.Button("DE → FR", id="de-fr-btn", color="success")
            ], className="mb-3")
        ], style={"textAlign": "center"})
    ])
    
    # Display vocabulary content directly
    content = html.Div([
        html.Div(id="vocab-display", children=display_learning_content(vocab_data, direction))
    ])
    
    return selected_file, options, content, updated_file_container

# Language direction toggle callback
@callback(
    [Output('direction-store', 'data'),
     Output('vocab-display', 'children')],
    [Input('fr-de-btn', 'n_clicks'),
     Input('de-fr-btn', 'n_clicks')],
    [State('file-store', 'data')],
    prevent_initial_call=True
)
def toggle_vocab_direction(fr_de_clicks, de_fr_clicks, selected_file):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Load vocabulary data
    if selected_file == "ALL" or not selected_file:
        vocab_data = load_vocabulary_data()
    else:
        vocab_data = load_vocabulary(selected_file)
    
    if button_id == 'fr-de-btn':
        direction = "fr-de"
    elif button_id == 'de-fr-btn':
        direction = "de-fr"
    else:
        return dash.no_update, dash.no_update
    
    return direction, display_learning_content(vocab_data, direction)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
