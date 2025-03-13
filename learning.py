from dash import html

def display_learning_content(vocab_data, direction):
    # Determine which language goes in which column
    source_lang = "french" if direction == "fr-de" else "german"
    target_lang = "german" if direction == "fr-de" else "french"
    
    # Set column headers based on direction
    left_header = "French" if direction == "fr-de" else "German"
    right_header = "German" if direction == "fr-de" else "French"
    
    rows = []
    for i, (french, details) in enumerate(vocab_data.items()):
        row_color = "white" if i % 2 == 0 else "lightgrey"
        
        # Set left and right cell values based on direction
        if direction == "fr-de":
            left_cell = french
            right_cell = details["german"]
        else:
            left_cell = details["german"]
            right_cell = french
        
        rows.append(html.Tr([
            html.Td(left_cell), 
            html.Td(right_cell)
        ], style={"backgroundColor": row_color, "padding": "5px"}))
    
    return html.Div([
        html.H3("Learning Mode"),
        html.Table([
            html.Tr([
                html.Th(left_header), 
                html.Th(right_header)
            ], className="table-header", style={"padding": "5px"}),
            *rows
        ], className="table table-striped", style={"width": "50%", "margin": "auto"})
    ])
