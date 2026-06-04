# RADAR — Retrieval and Analysis Driven Autonomous Researcher

> **Frozen reference artifact.** Built June–August 2023, in the AutoGPT / BabyAGI
> window. Public since then; now flagged read-only. Not maintained — preserved
> as a dated snapshot of an early autonomous-agent design.

RADAR is an autonomous research agent (Flask). Given a task and a number of
rounds, it runs itself: an LLM plans a web search, Brave Search + ScraperAPI
fetch a page, and the model synthesizes a running report — then iterates.

## The idea, and why it reads differently from its peers

The dominant 2023 pattern was the **chain in a loop** — a fixed sequence of steps
with append-only memory (a growing task queue or a buffer of prior outputs piped
forward). RADAR does something else: each round it **rebuilds its own context
structure** rather than extending a chain. The agent re-synthesizes a single
evolving representation — a running report plus a structured **Knowledge Log**
(current understanding / potential solutions / challenges / next steps) — *whole*,
every iteration. It owns and rewrites the structure it reasons inside, instead of
stacking artifacts. State it maintains, not a pipeline it flows through.

## Also notable for its date (mid-2023)

- **Multi-model routing by cognitive load** — gpt-4 for heavy planning and first
  analysis; gpt-3.5-turbo-16k for the cheaper iterative steps.
- **Hand-rolled tool use** — the model emits a search URL as text, parsed with a
  regex. Built the week OpenAI shipped function-calling (June 2023), so the tool
  layer is prompt-and-parse, not function calls.

A surviving example run (`results/LK99research_result_round_5.txt`) is a 5-round
synthesis of the LK-99 superconductor story — the viral science moment of that
summer.

---

## Setup & Installation
1. Clone this repository.
2. Install the dependencies by running:
    ```
    pip install -r requirements.txt
    ```
3. Set up your environment variables in a `.env` file:
    - `BRAVE_SEARCH_API_KEY`: Your Brave Search API key.
    - `SCRAPER_API_KEY`: Your ScraperAPI key.
    - `OPENAI_API_KEY`: Your OpenAI API key.

## Running the Application
Run the Flask application with:
    ```
    python run.py
    ```
Then open `http://localhost:5000` in your browser.

## Usage
1. Enter a task in the input field.
2. Define the number of rounds for the task.
3. Submit the form to start the autonomous research agent.

## Endpoints
- `/` (GET, POST): Main interface for starting, continuing, or finishing tasks.
- `/download/<filename>` (GET): Download a generated report.
- `/clear` (GET): Clear the current session and redirect home.

## Session Management
The app uses Flask session data to persist the task, running report, Knowledge
Log, scraped URLs, and search history across requests and rounds.

## Downloads
Each round is saved to `results/` as `<task>_result_round_<round_number>.txt` and
can be downloaded from the interface.

## License
Licensed under the terms of the [MIT License](./LICENSE).
