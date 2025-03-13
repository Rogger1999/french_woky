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

def display_quiz_content(vocab_data, quiz_type="multiple_choice", direction="fr-de", feedback_message=None, feedback_color=None):
    """
    Display quiz content based on quiz type and direction.
    
    Args:
        vocab_data: Dictionary of vocabulary data
        quiz_type: Either "multiple_choice" or "type_answer"
        direction: Either "fr-de" or "de-fr"
        feedback_message: Optional feedback message to display
        feedback_color: Optional color for the feedback message
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
    
    # Create feedback component if needed
    feedback_component = html.Div() # Empty div by default
    if feedback_message:
        if feedback_color == "red":
            feedback_component = html.Div([
                html.Span("Incorrect! ", style={"color": "red", "font-weight": "bold"}),
                html.Span(f"The correct answer is: {correct_answer}")
            ], style={"margin": "10px 0"})
        elif feedback_color == "green":
            feedback_component = html.Div(
                "Correct!", 
                style={"color": "green", "margin": "10px 0", "font-weight": "bold"}
            )
        else:
            feedback_component = html.Div(
                feedback_message, 
                style={"color": feedback_color or "blue", "margin": "10px 0"}
            )
    
    # Buttons for checking and next question
    button_styles = {
        'check': {'display': 'inline-block', 'margin-right': '10px'},
        'next': {'display': 'none'} if not feedback_message else {'display': 'inline-block'}
    }
    
    if quiz_type == "multiple_choice":
        # Generate options with correct answer included
        all_answers = []
        for key in vocab_data:
            if source_lang == "french":
                all_answers.append(vocab_data[key]["german"])
            else:
                all_answers.append(key)
        
        options = generate_options(correct_answer, all_answers)
        
        # Create radio items for multiple choice
        quiz_content = html.Div([
            html.H3("Quiz Mode - Multiple Choice"),
            html.H4(f"Translate: {question_word}"),
            dcc.RadioItems(
                id='quiz-options',
                options=[{'label': opt, 'value': opt} for opt in options],
                labelStyle={'display': 'block', 'margin': '10px'},
                value=None  # Ensure it's uncontrolled on initial render
            ),
            feedback_component,
            html.Div([
                html.Button("Check", id="check-btn", style=button_styles['check']),
                html.Button("Next", id="next-btn", style=button_styles['next'])
            ], style={'margin-top': '15px'}),
            # Store correct answer and other data
            dcc.Store(id='quiz-data', data={
                'correct_answer': correct_answer,
                'question_word': question_word,
                'direction': direction,
                'quiz_type': quiz_type
            })
        ])
    else:  # type_answer
        quiz_content = html.Div([
            html.H3("Quiz Mode - Type Answer"),
            html.H4(f"Translate: {question_word}"),
            dcc.Input(
                id='answer-input',  # Match the ID expected in app.py
                type='text',
                placeholder='Type your answer',
                value='',  # Initialize with empty string to make it controlled
            ),
            feedback_component,
            html.Div([
                html.Button("Check", id="check-btn", style=button_styles['check']),
                html.Button("Next", id="next-btn", style=button_styles['next'])
            ], style={'margin-top': '15px'}),
            # Store correct answer and other data
            dcc.Store(id='quiz-data', data={
                'correct_answer': correct_answer,
                'question_word': question_word,
                'direction': direction,
                'quiz_type': quiz_type
            })
        ])
    
    return quiz_content

# Callbacks for the quiz functionality will be in app.py or here depending on your structure
