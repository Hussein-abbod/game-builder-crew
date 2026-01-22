# Game Builder Crew

**Author:** ASIM IYAD OMER MUSTAFA  
**Email:** asimiyad@gmail.com

## Overview
This project uses AI agents (CrewAI) to design and build Python games using Pygame.

## Prerequisites
- Python 3.10, 3.11, or 3.12 (Recommend 3.11)

## Installation

1.  **Navigate to the project directory:**
    Open your terminal or command prompt and change to the project folder:
    ```bash
    cd "path/to/game-builder-crew"
    ```

2.  **Install Dependencies:**
    Run the following command to install all required libraries:
    ```bash
    pip install -r requirements.txt
    ```
    *Alternatively, if you are using poetry:*
    ```bash
    poetry install
    ```

## API Key Setup

This project requires Google Gemini API keys to function.

1.  **Get your API Keys:**
    Visit [Google AI Studio](https://aistudio.google.com/) and create **4** separate API keys.

2.  **Configure Environment Variables:**
    Create a file named `.env` in the root folder (same folder as this README) if it doesn't already exist.
    
    Add your keys to the `.env` file in the following format:

    ```env
    # .env file
    GOOGLE_API_KEY_DESIGNER="your_first_key_here"
    GOOGLE_API_KEY_SENIOR="your_second_key_here"
    GOOGLE_API_KEY_QA="your_third_key_here"
    GOOGLE_API_KEY_CHIEF="your_fourth_key_here"
    ```
    *(Replace `your_..._key_here` with the actual keys you generated).*

## How to Run

1.  **Run the Crew:**
    To start the AI crew and generate a game, run:
    ```bash
    python -m src.game_builder_crew.main
    ```
    *Note: Depending on your python setup, you might need to use `python3` instead of `python`.*

    **Running via Poetry:**
    ```bash
    poetry run game_builder_crew
    ```

2.  **Output:**
    The crew will design and code the game. The final code will be displayed in the console or saved as specified in the configuration.

## Troubleshooting

-   **"Module not found" error:** Ensure you have installed the dependencies using `pip install -r requirements.txt`.
-   **API Key errors:** Double-check that your `.env` file is named correctly (start with a dot) and contains valid keys without extra spaces or quotes issues.
