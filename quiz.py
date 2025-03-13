from dash import html, dcc, callback, Input, Output, State
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

def display_quiz_content(vocab_data, quiz_type="multiple_choice", direction="fr-de"):
    """
    Display quiz content based on quiz type and direction.
    
    Args:
        vocab_data: Dictionary of vocabulary data
        quiz_type: Either "multiple_choice" or "type_answer"
        direction: Either "fr-de" or "de-fr"
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
        dbc.Button("FR-DE", id="fr-de-quiz-btn", color="primary", className="me-1", 
                  active=direction=="fr-de"),
        dbc.Button("DE-FR", id="de-fr-quiz-btn", color="primary", 
                  active=direction=="de-fr")
    ])
    
    if quiz_type == "multiple_choice":
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
        
        # Create radio items for multiple choice
        quiz_content = html.Div([
            direction_toggle,
            html.H3("Quiz Mode - Multiple Choice"),
            html.Div([
                html.H4(f"Translate: {question_word}"),
                dcc.RadioItems(
                    id='quiz-options',
                    options=[{'label': opt, 'value': opt} for opt in options],
                    labelStyle={'display': 'block', 'margin': '10px'}
                ),
                html.Div(id='quiz-feedback'),
                html.Button("Check Answer", id="check-answer-btn"),
                html.Button("Next Question", id="next-question-btn", style={'display': 'none'}),
                # Store correct answer and other data
                dcc.Store(id='quiz-data', data={
                    'correct_answer': correct_answer,
                    'question_word': question_word,
                    'direction': direction,
                    'quiz_type': quiz_type
                })
            ])
        ])
    else:  # type_answer
        quiz_content = html.Div([
            direction_toggle,
            html.H3("Quiz Mode - Type Answer"),
            html.Div([
                html.H4(f"Translate: {question_word}"),
                dcc.Input(id='quiz-input', type='text', placeholder='Type your answer'),
                html.Div(id='quiz-feedback'),
                html.Button("Check Answer", id="check-answer-btn"),
                html.Button("Next Question", id="next-question-btn", style={'display': 'none'}),
                # Store correct answer and other data
                dcc.Store(id='quiz-data', data={
                    'correct_answer': correct_answer,
                    'question_word': question_word,
                    'direction': direction,
                    'quiz_type': quiz_type
                })
            ])
        ])
    
    return quiz_content

# Callbacks for the quiz functionality will be in app.py or here depending on your structure
