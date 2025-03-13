from dash import html, dcc
import dash_bootstrap_components as dbc
import random

def generate_options(correct_answer, all_answers, num_options=3):
    options = [correct_answer]
    
    # Filter out the correct answer from potential wrong answers
    potential_wrong_answers = [a for a in all_answers if a != correct_answer]
    
    # If we don't have enough potential wrong answers, repeat some
    if len(potential_wrong_answers) < num_options - 1:
        potential_wrong_answers = potential_wrong_answers * (num_options - 1)
    
    # Add wrong options
    wrong_options = random.sample(potential_wrong_answers, num_options - 1)
    options.extend(wrong_options)
    
    # Shuffle the options
    random.shuffle(options)
    
    return options

def display_quiz_content(vocab_data, direction):
    source_lang = "french" if direction == "fr-de" else "german"
    target_lang = "german" if direction == "fr-de" else "french"
    
    all_answers = [details[target_lang] for details in vocab_data.values()]
    
    # Initialize quiz state
    quiz_state = {
        "current_index": 0,
        "correct_answers": 0,
        "total_questions": len(vocab_data),
        "all_words": list(vocab_data.items()),
        "source_lang": source_lang,
        "target_lang": target_lang,
        "answered": False
    }
    
    current_word = quiz_state["all_words"][0]
    question = current_word[0] if source_lang == "french" else current_word[1][source_lang]
    correct_answer = current_word[1][target_lang]
    options = generate_options(correct_answer, all_answers)
    
    return html.Div([
        html.H3("Quiz Mode"),
        html.Div(id="quiz-section", children=[
            html.H4("Quiz Section"),
            dbc.Card([
                dbc.CardHeader(html.H4(question, className="text-center")),
                dbc.CardBody([
                    html.Div(id="options-container", className="d-grid gap-2", children=[
                        dbc.Button(option, id={"type": "option-btn", "index": option}, color="outline-primary", className="mb-2 text-start")
                        for option in options
                    ]),
                ]),
                dbc.CardFooter([
                    html.Div(id="feedback", className="mb-2"),
                    dbc.Button("Next Question", id="next-question-btn", color="success", className="me-2"),
                    dbc.Button("← Back to Files", id="back-to-files-btn", color="secondary"),
                ]),
            ], className="mb-3"),
            dbc.Alert(id="score-display", color="info", className="text-center"),
        ]),
        dcc.Store(id="quiz-state", data=quiz_state)
    ])
