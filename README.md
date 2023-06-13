# RADAR: Retrieval and Analysis Driven Autonomous Researcher

## Introduction
RADAR is an autonomous research agent built with Flask, OpenAI's GPT-3.5-turbo model, Brave Search, and ScraperAPI. The application performs tasks by generating search terms, searching the web, scraping pages, and producing analytical reports. 

## Setup & Installation
1. Clone this repository.
2. Install the dependencies by running: 
    ```
    pip install -r requirements.txt
    ```
3. Setup your environment variables in a `.env` file:
    - BRAVE_SEARCH_API_KEY: Your Brave Search API key.
    - SCRAPER_API_KEY: Your ScraperAPI key.
    - OPENAI_API_KEY: Your OpenAI API key.

## Running the Application
Run the Flask application with the command:
    ```
    python app.py
    ```
Access the web application by navigating to `http://localhost:5000` on your web browser.

## Usage
1. Enter a task in the provided input field.
2. Choose an action from the drop-down menu:
    - Start: Begins a new task and stores the results.
    - Next: Continues the previous task with new rounds of research.
    - Finish: Ends the current task and provides a final report.
3. Define the number of rounds for the task.
4. Submit the form to initiate the autonomous research agent.

## Endpoints
- `/` (GET, POST): The main application interface for starting, continuing, or finishing tasks.
- `/download/<filename>` (GET): Endpoint for downloading reports.
- `/clear` (GET): Clears the current session data and redirects to the home endpoint.

## Session Management
The Flask application uses session data to persist information across requests and throughout the task lifecycle.

## Downloads
Reports can be downloaded from the application interface. Each report is saved in the `results` directory with a filename formatted as `<task>_result_round_<round_number>.txt`.

**Note:** Always use the `.env` file to securely store your API keys and other sensitive information. This file should never be included in the repository.
