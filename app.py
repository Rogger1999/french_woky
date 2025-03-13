import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import json
import os
from pathlib import Path
from flask import Flask
from learning import display_learning_content
from lear_quiz import display_learning_quiz_content
from quiz import display_quiz_content

# Initialize the Flask server
server = Flask(__name__)

# Initialize the Dash app
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "French-German Vocabulary Learning"

# Define the data directory
DATA_DIR = Path("data")

# Function to load all vocabulary files
def get_available_files():
    return sorted([f.stem for f in DATA_DIR.glob("voca*.json")])

# Function to load vocabulary data from a specific file
def load_vocabulary(filename):
    with open(DATA_DIR / f"{filename}.json", 'r', encoding='utf-8') as file:
        return json.load(file)

# Layout of the app
app.layout = html.Div([
    dbc.Container([
        html.H1("French-German Vocabulary Learning", className="text-center my-4"),
        
        # Language direction toggle
        html.Div([
            dbc.Button("FR → DE", id="toggle-direction-btn", color="primary", className="mb-4"),
        ], className="text-center"),
        
        # Main menu buttons
        html.Div([
            dbc.Button("LEARNING", id="learning-btn", color="primary", className="me-2"),
            dbc.Button("LEARNING & QUIZ", id="learning-quiz-btn", color="primary", className="me-2"),
            dbc.Button("QUIZ", id="quiz-btn", color="primary"),
        ], className="text-center mb-4"),
        
        # Sub-menu buttons (initially hidden)
        html.Div(id="submenu-buttons", className="text-center mb-4", style={"display": "none"}),
        
        # Content section
        html.Div(id="content-section", className="text-center"),
        
        # Store components for app state
        dcc.Store(id="direction-store", data="fr-de"),  # 'fr-de' or 'de-fr'
        dcc.Store(id="mode-store"),       # 'learning', 'learning-quiz', or 'quiz'
        dcc.Store(id="file-store"),       # Currently selected file
        dcc.Store(id="vocab-store"),      # Loaded vocabulary data
        dcc.Store(id="quiz-state"),       # Current quiz state (current question, score, etc.)
        
    ], className="py-4")
])

# Callback for language direction toggle
@app.callback(
    Output("toggle-direction-btn", "children"),
    Output("direction-store", "data"),
    Input("toggle-direction-btn", "n_clicks"),
    State("direction-store", "data"),
    prevent_initial_call=True
)
def toggle_direction(n_clicks, direction):
    if direction == "fr-de":
        return "DE → FR", "de-fr"
    else:
        return "FR → DE", "fr-de"

# Callback for main menu buttons
@app.callback(
    Output("submenu-buttons", "children"),
    Output("submenu-buttons", "style"),
    Output("mode-store", "data"),
    Input("learning-btn", "n_clicks"),
    Input("learning-quiz-btn", "n_clicks"),
    Input("quiz-btn", "n_clicks"),
    prevent_initial_call=True
)
def show_submenu(learning_clicks, learning_quiz_clicks, quiz_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, {"display": "none"}, None
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "learning-btn":
        mode = "learning"
    elif button_id == "learning-quiz-btn":
        mode = "learning-quiz"
    else:
        mode = "quiz"
    
    # Create sub-menu buttons
    files = get_available_files()
    sub_buttons = [dbc.Button("All", id={"type": "sub-btn", "index": "all"}, color="primary", className="me-2 mb-2")]
    for file in files:
        sub_buttons.append(
            dbc.Button(file, id={"type": "sub-btn", "index": file}, color="primary", className="me-2 mb-2")
        )
    
    return sub_buttons, {"display": "block"}, mode

# Callback for sub-menu buttons
@app.callback(
    Output("content-section", "children"),
    Output("file-store", "data"),
    Output("vocab-store", "data"),
    Input({"type": "sub-btn", "index": dash.dependencies.ALL}, "n_clicks"),
    State("mode-store", "data"),
    State("direction-store", "data"),
    prevent_initial_call=True
)
def display_content(sub_clicks, mode, direction):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, None, None
    
    # Get selected file
    button_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    file_name = button_id["index"]
    
    # Load vocabulary
    if file_name == "all":
        vocab_data = {}
        for file in get_available_files():
            vocab_data.update(load_vocabulary(file))
    else:
        vocab_data = load_vocabulary(file_name)
    
    # Display content based on mode
    if mode == "learning":
        content = display_learning_content(vocab_data, direction)
    elif mode == "learning-quiz":
        content = display_learning_quiz_content(vocab_data, direction)
    else:
        content = display_quiz_content(vocab_data, direction)
    
    return content, file_name, vocab_data

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
