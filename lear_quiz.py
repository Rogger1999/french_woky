from dash import html, dcc
import dash_bootstrap_components as dbc

def display_learning_quiz_content(vocab_data, direction):
    source_lang = "french" if direction == "fr-de" else "german"
    target_lang = "german" if direction == "fr-de" else "french"
    
    return html.Div([
        html.H3("Learning & Quiz Mode"),
        html.Div(id="learning-section", children=[
            html.Table([
                html.Tr([html.Th("French"), html.Th("German")], className="table-header"),
                *[
                    html.Tr([html.Td(french), html.Td(details["german"])], className="table-row")
                    for i, (french, details) in enumerate(vocab_data.items())
                ]
            ], className="table table-striped"),
            dbc.Button("Next", id="next-to-quiz-btn", color="success", className="mt-3")
        ]),
        html.Div(id="quiz-section", style={"display": "none"}, children=[
            html.H4("Quiz Section"),
            # ...additional content for quiz section...
        ])
    ])
