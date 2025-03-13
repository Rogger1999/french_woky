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
app.config.suppress_callback_exceptions = True  # Add this to suppress the error

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
        children=[
            dbc.NavItem(dbc.NavLink("LEARNING", id="learning-link", href="#")),
            dbc.NavItem(dbc.NavLink("QUIZ", id="quiz-link", href="#")),
        ],
        brand="French-German Vocabulary",
        brand_href="#",
        color="primary",
        dark=True,
    ),
    html.Div(id='file-selection-container', className="mt-3 mb-3"),
    html.Div(id='submenu-container'),
    html.Div(id='content-container'),
    
    # Hidden stores to keep track of state
    dcc.Store(id="direction-store", data="fr-de"),
    dcc.Store(id="mode-store"),
    dcc.Store(id="file-store"),
    dcc.Store(id="vocab-store"),
    
    # Hidden div for storing intermediate data
    html.Div(id='hidden-div', style={'display': 'none'}),
    
    # Add hidden buttons to prevent "nonexistent object" errors
    html.Div([
        dbc.Button("Multiple Choice", id="multiple-choice-btn", style={'display': 'none'}),
        dbc.Button("Type Answer", id="type-answer-btn", style={'display': 'none'}),
        html.Button("Start Quiz", id="start-quiz-btn", style={'display': 'none'}),
        dbc.Button("FR-DE", id="fr-de-quiz-btn", style={'display': 'none'}),
        dbc.Button("DE-FR", id="de-fr-quiz-btn", style={'display': 'none'}),
        dbc.Button("FR-DE", id="fr-de-learn-quiz-btn", style={'display': 'none'}),
        dbc.Button("DE-FR", id="de-fr-learn-quiz-btn", style={'display': 'none'}),
        html.Button("Next", id="learn-next-btn", style={'display': 'none'}),
        html.Button("Back to Learning", id="back-to-learning-btn", style={'display': 'none'}),
        html.Button("Check", id="learn-check-btn", style={'display': 'none'}),
    ], style={'display': 'none'})
])

# Callback to initialize file selection buttons
@callback(
    Output('file-selection-container', 'children'),
    Input('hidden-div', 'children')
)
def initialize_file_buttons(_):
    files = ["ALL"] + get_available_files()
    buttons = [
        dbc.Button(file, id=f"file-btn-{file}", color="secondary", 
                  size="sm", className="me-1 mb-1")
        for file in files
    ]
    return html.Div([
        html.H6("Select Vocabulary File:", className="mb-2"),
        html.Div(buttons)
    ], style={"textAlign": "center"})

# Callback to show the appropriate submenu when a main menu item is clicked
@callback(
    Output('submenu-container', 'children'),
    [Input('learning-link', 'n_clicks'),
     Input('quiz-link', 'n_clicks')],
    prevent_initial_call=True
)
def show_submenu(learning_clicks, quiz_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return html.Div()
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'learning-link':
        return html.Div([
            html.H6("Select Direction:", className="mt-3 mb-2", style={"textAlign": "center"}),
            dbc.ButtonGroup([
                dbc.Button("FR-DE", id="fr-de-learn-btn", color="primary", className="me-1"),
                dbc.Button("DE-FR", id="de-fr-learn-btn", color="primary")
            ], className="d-flex justify-content-center")
        ])
    elif button_id == 'quiz-link':
        return html.Div([
            html.H6("Select Quiz Type:", className="mt-3 mb-2", style={"textAlign": "center"}),
            dbc.ButtonGroup([
                dbc.Button("Multiple Choice", id="multiple-choice-btn", color="primary", className="me-1"),
                dbc.Button("Type Answer", id="type-answer-btn", color="primary")
            ], className="d-flex justify-content-center")
        ])
    return html.Div()

# Callback for file selection
@callback(
    [Output('file-store', 'data'),
     Output('content-container', 'children', allow_duplicate=True)],
    [Input(f"file-btn-{file}", "n_clicks") for file in ["ALL"] + get_available_files()],
    [State('mode-store', 'data'), 
     State('direction-store', 'data')],
    prevent_initial_call=True
)
def handle_file_selection(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    selected_file = button_id.replace("file-btn-", "")
    
    # Get the current mode and direction
    mode = args[-2]  # mode-store data
    direction = args[-1]  # direction-store data
    
    # Load appropriate vocabulary data
    if selected_file == "ALL":
        vocab_data = load_vocabulary_data()
    else:
        vocab_data = load_vocabulary(selected_file)
    
    # Update the display based on current mode and direction
    if mode == "learning" and direction:
        return selected_file, display_learning_content(vocab_data, direction)
    elif mode == "learning_quiz" and direction:
        return selected_file, display_learning_quiz_content(vocab_data, direction)
    elif mode == "quiz" and direction:
        quiz_type = "multiple_choice"  # Default
        return selected_file, display_quiz_content(vocab_data, quiz_type=quiz_type, direction=direction)
    
    # If no mode or direction selected yet, just update the file store
    return selected_file, dash.no_update

# Modified callback to display vocabulary or quiz based on submenu selection
@callback(
    [Output('content-container', 'children'),
     Output('mode-store', 'data')],
    [Input('fr-de-learn-btn', 'n_clicks'),
     Input('de-fr-learn-btn', 'n_clicks'),
     Input('multiple-choice-btn', 'n_clicks'),
     Input('type-answer-btn', 'n_clicks')],
    [State('file-store', 'data')],
    prevent_initial_call=True
)
def update_content(fr_de_learn, de_fr_learn, multiple_choice, type_answer, selected_file):
    ctx = dash.callback_context
    if not ctx.triggered:
        return html.Div(), dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Load vocabulary data based on selected file
    if selected_file == "ALL" or not selected_file:
        vocab_data = load_vocabulary_data()
    else:
        vocab_data = load_vocabulary(selected_file)
    
    if button_id == 'fr-de-learn-btn':
        content = display_learning_content(vocab_data, "fr-de")
        return html.Div([
            content,
            html.Button("Start Quiz", id="start-quiz-btn", n_clicks=0)
        ]), "learning"
    elif button_id == 'de-fr-learn-btn':
        content = display_learning_content(vocab_data, "de-fr")
        return html.Div([
            content,
            html.Button("Start Quiz", id="start-quiz-btn", n_clicks=0)
        ]), "learning"
    elif button_id == 'multiple-choice-btn':
        return display_quiz_content(vocab_data, quiz_type="multiple_choice", direction="fr-de"), "quiz"
    elif button_id == 'type-answer-btn':
        return display_quiz_content(vocab_data, quiz_type="type_answer", direction="fr-de"), "quiz"
    
    return html.Div(), dash.no_update

# Start Quiz button callback
@callback(
    [Output('content-container', 'children', allow_duplicate=True),
     Output('mode-store', 'data', allow_duplicate=True)],
    [Input('start-quiz-btn', 'n_clicks')],
    [State('direction-store', 'data'),
     State('file-store', 'data')],
    prevent_initial_call=True
)
def start_quiz(n_clicks, direction, selected_file):
    if n_clicks:
        if selected_file == "ALL" or not selected_file:
            vocab_data = load_vocabulary_data()
        else:
            vocab_data = load_vocabulary(selected_file)
        
        return display_learning_quiz_content(vocab_data, direction), "learning_quiz"
    return dash.no_update, dash.no_update

# Check answer callback for the learning quiz
@callback(
    [Output('learn-quiz-feedback', 'children'),
     Output('learn-check-btn', 'style'),
     Output('learn-next-btn', 'style')],
    [Input('learn-check-btn', 'n_clicks')],
    [State('learn-quiz-options', 'value'),
     State('learn-quiz-data', 'data')],
    prevent_initial_call=True
)
def check_learning_quiz_answer(n_clicks, selected_option, quiz_data):
    if not n_clicks or not selected_option:
        return dash.no_update, dash.no_update, dash.no_update
    
    correct_answer = quiz_data['correct_answer']
    
    if selected_option == correct_answer:
        feedback = html.Div("Correct!", style={"color": "green", "margin": "10px 0"})
    else:
        feedback = html.Div([
            html.Span("Incorrect! ", style={"color": "red"}),
            html.Span(f"The correct answer is: {correct_answer}")
        ], style={"margin": "10px 0"})
    
    return feedback, {'display': 'none'}, {'display': 'block'}

# Next question callback for the learning quiz
@callback(
    Output('content-container', 'children', allow_duplicate=True),
    [Input('learn-next-btn', 'n_clicks'),
     Input('back-to-learning-btn', 'n_clicks')],
    [State('learn-quiz-data', 'data')],
    prevent_initial_call=True
)
def next_learning_quiz_question(next_clicks, back_clicks, quiz_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    direction = quiz_data['direction']
    vocab_data = load_vocabulary_data()
    
    if button_id == 'learn-next-btn':
        return display_learning_quiz_content(vocab_data, direction)
    else:  # back-to-learning-btn
        return display_learning_content(vocab_data, direction)

# Direction toggle callbacks - modified to include file selection
@callback(
    [Output('content-container', 'children', allow_duplicate=True),
     Output('direction-store', 'data'),
     Output('mode-store', 'data', allow_duplicate=True)],
    [Input('fr-de-learn-quiz-btn', 'n_clicks'),
     Input('de-fr-learn-quiz-btn', 'n_clicks'),
     Input('fr-de-quiz-btn', 'n_clicks'),
     Input('de-fr-quiz-btn', 'n_clicks')],
    [State('file-store', 'data')],
    prevent_initial_call=True
)
def toggle_direction_buttons(fr_de_learn_quiz, de_fr_learn_quiz, fr_de_quiz, de_fr_quiz, selected_file):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Load vocabulary data based on selected file
    if selected_file == "ALL" or not selected_file:
        vocab_data = load_vocabulary_data()
    else:
        vocab_data = load_vocabulary(selected_file)
    
    if button_id == 'fr-de-learn-quiz-btn':
        direction = "fr-de"
        return display_learning_quiz_content(vocab_data, direction), direction, "learning_quiz"
    elif button_id == 'de-fr-learn-quiz-btn':
        direction = "de-fr"
        return display_learning_quiz_content(vocab_data, direction), direction, "learning_quiz"
    elif button_id == 'fr-de-quiz-btn':
        direction = "fr-de"
        quiz_type = "multiple_choice"
        return display_quiz_content(vocab_data, quiz_type=quiz_type, direction=direction), direction, "quiz"
    elif button_id == 'de-fr-quiz-btn':
        direction = "de-fr"
        quiz_type = "multiple_choice"
        return display_quiz_content(vocab_data, quiz_type=quiz_type, direction=direction), direction, "quiz"
    
    return dash.no_update, dash.no_update, dash.no_update

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
