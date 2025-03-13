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
        brand="French-German Vocabulary",
        brand_href="#",
        color="primary",
        dark=True,
    ),
    html.Div(id='mode-selection-container', className="mt-3 mb-3", children=[
        html.H6("Select Mode:", className="mb-2"),
        dbc.ButtonGroup([
            dbc.Button("LEARNING MODE", id="learning-mode-btn", color="primary", className="me-1"),
            dbc.Button("QUIZ MODE", id="quiz-mode-btn", color="primary")
        ])
    ], style={"textAlign": "center"}),
    html.Div(id='file-selection-container', className="mt-3 mb-3"),
    html.Div(id='option-container', className="mt-3 mb-3"),
    html.Div(id='content-container'),
    
    # Hidden stores to keep track of state
    dcc.Store(id="mode-store", data=""),
    dcc.Store(id="direction-store", data="fr-de"),
    dcc.Store(id="quiz-type-store", data="learning_quiz"),
    dcc.Store(id="file-store"),
    
    # Hidden div for storing intermediate data
    html.Div(id='hidden-div', style={'display': 'none'}),
    
    # Add hidden buttons to prevent "nonexistent object" errors
    html.Div([
        html.Button("Next", id="learn-next-btn", style={'display': 'none'}),
        html.Button("Check", id="learn-check-btn", style={'display': 'none'}),
    ], style={'display': 'none'})
])

# Callback to handle mode selection
@callback(
    [Output('mode-store', 'data'),
     Output('file-selection-container', 'children')],
    [Input('learning-mode-btn', 'n_clicks'),
     Input('quiz-mode-btn', 'n_clicks')],
    prevent_initial_call=True
)
def handle_mode_selection(learning_clicks, quiz_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    files = ["ALL"] + get_available_files()
    
    if button_id == 'learning-mode-btn':
        mode = "learning"
    else:  # quiz-mode-btn
        mode = "quiz"
    
    file_buttons = [
        dbc.Button(file, id=f"file-btn-{file}", color="secondary", 
                  size="sm", className="me-1 mb-1")
        for file in files
    ]
    
    return mode, html.Div([
        html.H6(f"Select Vocabulary File for {mode.upper()} mode:", className="mb-2"),
        html.Div(file_buttons)
    ], style={"textAlign": "center"})

# Callback for file selection - now with highlighting selected file
@callback(
    [Output('file-store', 'data'),
     Output('option-container', 'children'),
     Output('content-container', 'children'),
     Output('file-selection-container', 'children', allow_duplicate=True)],
    [Input(f"file-btn-{file}", "n_clicks") for file in ["ALL"] + get_available_files()],
    [State('mode-store', 'data'),
     State('direction-store', 'data')],
    prevent_initial_call=True
)
def handle_file_selection(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    selected_file = button_id.replace("file-btn-", "")
    
    # Get the current mode and direction (last two args)
    mode = args[-2]
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
        html.H6(f"Select Vocabulary File for {mode.upper()} mode:", className="mb-2"),
        html.Div(file_buttons)
    ], style={"textAlign": "center"})
    
    # Different handling based on mode
    if mode == "learning":
        # Learning mode - no changes here as requested
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
            html.Div(id="vocab-display", children=display_learning_content(vocab_data, direction)),
            html.Div([
                dbc.Button("Back", id="back-to-mode-btn", color="primary", className="mt-3")
            ], style={"textAlign": "center"})
        ])
        
        return selected_file, options, content, updated_file_container
    else:  # quiz mode - show quiz options (removing Learning Quiz)
        options = html.Div([
            html.Div([
                html.H6("Quiz Type:", className="mt-2 mb-2"),
                dbc.ButtonGroup([
                    dbc.Button("Multiple Choice", id="multiple-choice-btn", color="primary", className="me-1"),
                    dbc.Button("Type Word", id="type-word-btn", color="primary")
                ], className="mb-3")
            ], style={"textAlign": "center"}),
            html.Div([
                html.H6("Language Direction:", className="mt-2 mb-2"),
                dbc.ButtonGroup([
                    dbc.Button("FR → DE", id="fr-de-btn", color="success", className="me-1"),
                    dbc.Button("DE → FR", id="de-fr-btn", color="success")
                ], className="mb-3")
            ], style={"textAlign": "center"}),
            html.Div([
                dbc.Button("GO", id="start-quiz-btn", color="danger", size="lg", className="mt-2")
            ], style={"textAlign": "center"})
        ])
        
        return selected_file, options, dash.no_update, updated_file_container

# Language direction toggle callback
@callback(
    Output('direction-store', 'data'),
    [Input('fr-de-btn', 'n_clicks'),
     Input('de-fr-btn', 'n_clicks')],
    prevent_initial_call=True
)
def set_direction(fr_de_clicks, de_fr_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'fr-de-btn':
        return "fr-de"
    elif button_id == 'de-fr-btn':
        return "de-fr"
    
    return dash.no_update

# Quiz type toggle callback - modified to highlight the selected quiz type
@callback(
    [Output('quiz-type-store', 'data'),
     Output('option-container', 'children', allow_duplicate=True)],
    [Input('multiple-choice-btn', 'n_clicks'),
     Input('type-word-btn', 'n_clicks')],
    [State('file-store', 'data'),
     State('direction-store', 'data')],
    prevent_initial_call=True
)
def set_quiz_type(multiple_choice_clicks, type_word_clicks, selected_file, direction):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Set quiz type based on button clicked
    if button_id == 'multiple-choice-btn':
        quiz_type = "multiple_choice"
        multiple_color = "primary"  # Highlight selected
        type_word_color = "secondary"
    elif button_id == 'type-word-btn':
        quiz_type = "type_answer"
        multiple_color = "secondary"
        type_word_color = "primary"  # Highlight selected
    else:
        return dash.no_update, dash.no_update
    
    # Update the quiz options with highlighted buttons
    options = html.Div([
        html.Div([
            html.H6("Quiz Type:", className="mt-2 mb-2"),
            dbc.ButtonGroup([
                dbc.Button("Multiple Choice", id="multiple-choice-btn", color=multiple_color, className="me-1"),
                dbc.Button("Type Word", id="type-word-btn", color=type_word_color)
            ], className="mb-3")
        ], style={"textAlign": "center"}),
        html.Div([
            html.H6("Language Direction:", className="mt-2 mb-2"),
            dbc.ButtonGroup([
                dbc.Button("FR → DE", id="fr-de-btn", color="success", className="me-1"),
                dbc.Button("DE → FR", id="de-fr-btn", color="success")
            ], className="mb-3")
        ], style={"textAlign": "center"}),
        html.Div([
            dbc.Button("GO", id="start-quiz-btn", color="danger", size="lg", className="mt-2")
        ], style={"textAlign": "center"})
    ])
    
    return quiz_type, options

# Language direction toggle callback for learning mode
@callback(
    Output('vocab-display', 'children'),
    [Input('fr-de-btn', 'n_clicks'),
     Input('de-fr-btn', 'n_clicks')],
    [State('file-store', 'data'),
     State('mode-store', 'data')],
    prevent_initial_call=True
)
def toggle_vocab_direction(fr_de_clicks, de_fr_clicks, selected_file, mode):
    ctx = dash.callback_context
    if not ctx.triggered or mode != "learning":
        return dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Load vocabulary data
    if selected_file == "ALL" or not selected_file:
        vocab_data = load_vocabulary_data()
    else:
        vocab_data = load_vocabulary(selected_file)
    
    if button_id == 'fr-de-btn':
        return display_learning_content(vocab_data, "fr-de")
    elif button_id == 'de-fr-btn':
        return display_learning_content(vocab_data, "de-fr")
    
    return dash.no_update

# Back to mode selection button
@callback(
    [Output('content-container', 'children', allow_duplicate=True),
     Output('option-container', 'children', allow_duplicate=True)],
    [Input('back-to-mode-btn', 'n_clicks')],
    prevent_initial_call=True
)
def back_to_mode_selection(n_clicks):
    if n_clicks:
        return html.Div(), html.Div()  # Clear content and options
    return dash.no_update, dash.no_update

# Start Quiz button callback - modified to handle only multiple choice and type answer
@callback(
    Output('content-container', 'children', allow_duplicate=True),
    [Input('start-quiz-btn', 'n_clicks')],
    [State('direction-store', 'data'),
     State('quiz-type-store', 'data'),
     State('file-store', 'data')],
    prevent_initial_call=True
)
def start_quiz(n_clicks, direction, quiz_type, selected_file):
    if n_clicks:
        if selected_file == "ALL" or not selected_file:
            vocab_data = load_vocabulary_data()
        else:
            vocab_data = load_vocabulary(selected_file)
        
        # Display quiz content based on type (only multiple_choice or type_answer)
        quiz_content = display_quiz_content(vocab_data, quiz_type=quiz_type, direction=direction)
        
        # Add direction toggle within the quiz
        return html.Div([
            html.Div([
                dbc.ButtonGroup([
                    dbc.Button("FR → DE", id="fr-de-quiz-btn", color="success", className="me-1"),
                    dbc.Button("DE → FR", id="de-fr-quiz-btn", color="success")
                ], className="mb-3")
            ], style={"textAlign": "center"}),
            html.Div(id="quiz-display", children=quiz_content),
            html.Div([
                dbc.Button("Back", id="back-to-options-btn", color="primary", className="mt-3")
            ], style={"textAlign": "center"})
        ])
    
    return dash.no_update

# Quiz direction toggle callback
@callback(
    Output('quiz-display', 'children'),
    [Input('fr-de-quiz-btn', 'n_clicks'),
     Input('de-fr-quiz-btn', 'n_clicks')],
    [State('quiz-type-store', 'data'),
     State('file-store', 'data')],
    prevent_initial_call=True
)
def toggle_quiz_direction(fr_de_clicks, de_fr_clicks, quiz_type, selected_file):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Load vocabulary data
    if selected_file == "ALL" or not selected_file:
        vocab_data = load_vocabulary_data()
    else:
        vocab_data = load_vocabulary(selected_file)
    
    # Set direction based on button clicked
    if button_id == 'fr-de-quiz-btn':
        direction = "fr-de"
    elif button_id == 'de-fr-quiz-btn':
        direction = "de-fr"
    else:
        return dash.no_update
    
    # Choose the appropriate quiz type
    if quiz_type == "learning_quiz":
        return display_learning_quiz_content(vocab_data, direction)
    else:  # multiple_choice or type_answer
        return display_quiz_content(vocab_data, quiz_type=quiz_type, direction=direction)

# Back button callback
@callback(
    [Output('option-container', 'children', allow_duplicate=True),
     Output('content-container', 'children', allow_duplicate=True)],
    [Input('back-to-options-btn', 'n_clicks')],
    prevent_initial_call=True
)
def back_to_options(n_clicks):
    if n_clicks:
        return dash.no_update, html.Div()  # Clear content but keep options
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

# Next question callback for the quiz - simplified to only handle multiple_choice and type_answer
@callback(
    Output('quiz-display', 'children', allow_duplicate=True),
    [Input('learn-next-btn', 'n_clicks')],
    [State('learn-quiz-data', 'data'),
     State('file-store', 'data'),
     State('quiz-type-store', 'data')],
    prevent_initial_call=True
)
def next_learning_quiz_question(next_clicks, quiz_data, selected_file, quiz_type):
    if not next_clicks:
        return dash.no_update
    
    direction = quiz_data['direction']
    
    # Load vocabulary data based on selected file
    if selected_file == "ALL" or not selected_file:
        vocab_data = load_vocabulary_data()
    else:
        vocab_data = load_vocabulary(selected_file)
    
    # Only handle multiple_choice and type_answer quiz types
    return display_quiz_content(vocab_data, quiz_type=quiz_type, direction=direction)

# Check answer callback for quizzes - updated to work with quiz.py components
@callback(
    [Output('quiz-feedback', 'children'),
     Output('quiz-check-btn', 'style'),
     Output('quiz-next-btn', 'style')],
    [Input('quiz-check-btn', 'n_clicks')],
    [State('quiz-answer-input', 'value'),
     State('quiz-options', 'value'),
     State('quiz-data', 'data'),
     State('quiz-type-store', 'data')],
    prevent_initial_call=True
)
def check_quiz_answer(n_clicks, typed_answer, selected_option, quiz_data, quiz_type):
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update
    
    correct_answer = quiz_data.get('correct_answer', '')
    
    # Handle different quiz types
    if quiz_type == "multiple_choice":
        user_answer = selected_option
    else:  # type_answer
        user_answer = typed_answer
    
    if not user_answer:
        return html.Div("Please select/type an answer first", style={"color": "blue", "margin": "10px 0"}), dash.no_update, dash.no_update
    
    # Check if answer is correct
    if user_answer.lower().strip() == correct_answer.lower().strip():
        feedback = html.Div("Correct!", style={"color": "green", "margin": "10px 0"})
    else:
        feedback = html.Div([
            html.Span("Incorrect! ", style={"color": "red"}),
            html.Span(f"The correct answer is: {correct_answer}")
        ], style={"margin": "10px 0"})
    
    return feedback, {'display': 'none'}, {'display': 'block'}

# Next question callback for quizzes - updated to work with quiz.py components
@callback(
    Output('quiz-display', 'children', allow_duplicate=True),
    [Input('quiz-next-btn', 'n_clicks')],
    [State('quiz-data', 'data'),
     State('file-store', 'data'),
     State('quiz-type-store', 'data')],
    prevent_initial_call=True
)
def next_quiz_question(next_clicks, quiz_data, selected_file, quiz_type):
    if not next_clicks:
        return dash.no_update
    
    direction = quiz_data.get('direction', 'fr-de')
    
    # Load vocabulary data based on selected file
    if selected_file == "ALL" or not selected_file:
        vocab_data = load_vocabulary_data()
    else:
        vocab_data = load_vocabulary(selected_file)
    
    # Generate new quiz content
    return display_quiz_content(vocab_data, quiz_type=quiz_type, direction=direction)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
