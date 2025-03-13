from dash import html

def display_learning_content(vocab_data, direction):
    source_lang = "french" if direction == "fr-de" else "german"
    target_lang = "german" if direction == "fr-de" else "french"
    
    return html.Div([
        html.H3("Learning Mode"),
        html.Table([
            html.Tr([html.Th("French"), html.Th("German")], className="table-header"),
            *[
                html.Tr([html.Td(french), html.Td(details["german"])], className="table-row")
                for i, (french, details) in enumerate(vocab_data.items())
            ]
        ], className="table table-striped")
    ])
