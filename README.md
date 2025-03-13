# French-German Vocabulary Learning App

A web application for learning and practicing French-German vocabulary using interactive learning modes and quizzes.

## Features

- **Learning Mode**: Browse vocabulary lists with translations
- **Quiz Mode**: Test your knowledge with multiple choice questions or by typing answers
- **Language Direction**: Practice both French→German and German→French translations
- **File Selection**: Choose specific vocabulary files or use all available vocabularies

## Installation

1. Clone this repository
2. Install required packages:
   ```
   pip install dash dash-bootstrap-components flask
   ```
3. Make sure you have vocabulary files in JSON format in the `/data` directory

## Usage

1. Run the application:
   ```
   python app.py
   ```
2. Open your browser and navigate to http://localhost:8080

## How to Use

### Learning Mode
1. Click "LEARNING MODE"
2. Select a vocabulary file
3. View the vocabulary list
4. Toggle between FR→DE and DE→FR using the direction buttons

### Quiz Mode
1. Click "QUIZ MODE"
2. Select a vocabulary file
3. Choose quiz type: Multiple Choice or Type Word
4. Select language direction (FR→DE or DE→FR)
5. Click "GO" to start the quiz
6. Answer questions and check your progress

## Data Format

Vocabulary files should be stored in the `/data` directory with filenames starting with "voca" and ending with ".json".
Each file should contain JSON data in the following format:

```json
{
  "word1": {
    "fr": "French word",
    "de": "German translation"
  },
  "word2": {
    "fr": "Another French word",
    "de": "Another German translation"
  }
}
```

## Project Structure

- `app.py`: Main application file with all UI components and callbacks
- `learning.py`: Functions for displaying vocabulary in learning mode
- `lear_quiz.py`: Functions for creating learning quizzes
- `quiz.py`: Functions for creating multiple choice and typing quizzes
- `/data`: Directory containing vocabulary JSON files

## License

This project is open source and available for personal use.
