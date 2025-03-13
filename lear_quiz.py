from dash import html, dcc
import dash_bootstrap_components as dbc
import random

def display_learning_quiz_content(vocab_data, direction="fr-de"):
    """
    Display a simpler quiz immediately after learning the vocabulary.
    """
    # Determine source and target languages
    source_lang = "french" if direction == "fr-de" else "german"
    target_lang = "german" if direction == "fr-de" else "french"
    
    # Select a random word to quiz
    word_keys = list(vocab_data.keys())
    random_word_key = random.choice(word_keys)
    
    if source_lang == "french":
        question_word = random_word_key
        correct_answer = vocab_data[random_word_key]["german"]
    else:
        correct_answer = random_word_key
        question_word = vocab_data[random_word_key]["german"]
    
    # Create direction toggle buttons
    direction_toggle = dbc.ButtonGroup([
        dbc.Button("FR-DE", id="fr-de-learn-quiz-btn", color="primary", className="me-1", 
                  active=direction=="fr-de"),
        dbc.Button("DE-FR", id="de-fr-learn-quiz-btn", color="primary", 
                  active=direction=="de-fr")
    ])
    
    # Generate 3 options, including the correct one
    options = [correct_answer]
    while len(options) < 3:
        random_option_key = random.choice(word_keys)
        if source_lang == "french":
            option = vocab_data[random_option_key]["german"]
        else:
            option = random_option_key
        
        if option not in options:
            options.append(option)
    
    # Shuffle options
    random.shuffle(options)
    
    # Create quiz content
    quiz_content = html.Div([
        direction_toggle,
        html.H3("Learning Quiz"),
        html.Div([
            html.H4(f"Translate: {question_word}"),
            dcc.RadioItems(
                id='learn-quiz-options',
                options=[{'label': opt, 'value': opt} for opt in options],
                labelStyle={'display': 'block', 'margin': '10px'}
            ),
            html.Div(id='learn-quiz-feedback'),
            html.Button("Check Answer", id="learn-check-btn"),
            html.Button("Next Question", id="learn-next-btn", style={'display': 'none'}),
            html.Button("Back to Learning", id="back-to-learning-btn"),
            # Store correct answer and other data
            dcc.Store(id='learn-quiz-data', data={
                'correct_answer': correct_answer,
                'question_word': question_word,
                'direction': direction
            })
        ])
    ])
    
    return quiz_content

# Add quiz check answer callback in app.py
