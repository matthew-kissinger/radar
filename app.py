from flask import Flask, jsonify, request, render_template, send_file, session, Response, redirect, url_for, send_from_directory
import openai
import requests
import tiktoken
import urllib.parse
from bs4 import BeautifulSoup
import openai
import requests
import tiktoken
import urllib.parse
import os
import secrets
import io
from datetime import datetime
from dotenv import load_dotenv

load_dotenv() 

BRAVE_SEARCH_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.secret_key = secrets.token_bytes(16)
current_date = datetime.now().strftime('%Y-%m-%d') 

def remove_quotes(string):
    return string.replace("\"", "")

def create_initial_search_message(task):
    return [
        {
            "role": "system",
            "content": f"As an autonomous research agent, your task is: '{task}'. The current date is {current_date}. Generate an initial search term or query related to this task. The response should only contain the search term."
        }
    ]

def create_search_message(task, response, previous_search_terms):
    return [
        {
            "role": "system",
            "content": f"As an autonomous research agent, your ongoing task is: '{task}', and the response so far is: '{response}'. The current date is {current_date}. Considering your previous search terms: {previous_search_terms}, generate a new unique search term that could add more depth to our current understanding. Remember, this new search should bring more light to our task. The response should only contain the search term."
        }
    ]

def create_task_message(task, content):
    return [
        {
            "role": "system",
            "content": f"As an autonomous research agent, your primary task is: '{task}'. The current date is {current_date}. Analyze the following web content: '{content}'. Generate a response structured as follows: The result of the task, a detailed response, and an update to your Knowledge Log with your current understanding, potential solutions, challenges, and future steps. Remember, this Knowledge Log should be carried forward for future iterations. Your result is iterated through so give it your best shot at completing the task."
        }
    ]


def create_report_update_message(task, current_report, content):
    return [
        {
            "role": "system",
            "content": f"As an autonomous research agent, your ongoing task is: '{task}'. Your previous response was: '{current_report}'. The current date is {current_date}. Analyze the new content and synthenize the complete report using previous response and new content: '{content}'. Compare the content Structure your response as follows: The updated and complete result of the task, a detailed response with updated findings, and your updated and complete knowledge log. Remember to carry forward this Knowledge Log for future iterations."
        }
    ]

def get_page_content(url):
    headers = {"apikey": SCRAPER_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=120) 
    except requests.exceptions.Timeout:
        print(f"Timeout occurred while trying to scrape {url}")
        return None
    print(f"Response status code: {response.status_code}") 
    if response.status_code == 200:
        print(f"Raw response text: {response.text[:500]}") 
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        page_content = ' '.join(soup.get_text().split())
        print(f"Extracted page content: {page_content[:100]}...") 
        tokenizer = tiktoken.get_encoding("cl100k_base")
        tokens = tokenizer.encode(page_content)
        if len(tokens) > 2000:
            excess = len(tokens) - 2000
            page_content = tokenizer.decode(tokens[:-excess])
        print(f"Page Content: {page_content[:100]}...")  
        return page_content
    else:
        return None

def search_brave(search_term):
    headers = {"Accept": "application/json", "X-Subscription-Token": BRAVE_SEARCH_API_KEY}
    query = urllib.parse.quote(search_term)
    response = requests.get(f"https://api.search.brave.com/res/v1/web/search?q={query}", headers=headers)
    print(f"Response status code from Brave API: {response.status_code}")  
    if response.status_code == 200:
        response_json = response.json()
        print(f"Response JSON from Brave API: {response_json}")  
        try:
            return response_json['web']
        except KeyError:
            return None
    else:
        return None

def autonomous_agent(task, action='next'):
    openai.api_key = OPENAI_API_KEY
    scraped_urls = session.get('scraped_urls', [])
    previous_search_terms = session.get('previous_search_terms', [])
    response_text = session.get('response_text', "")
    search_history = session.get('search_history', [])
    
    if 'research_started' not in session:
        # this is the first round
        session['research_started'] = True
        initial_search_message = create_initial_search_message(task)
        initial_search_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=initial_search_message
        )
        search_term = remove_quotes(initial_search_response.choices[0].message['content'])
    else:
        # this is a subsequent round
        search_message = create_search_message(task, response_text, previous_search_terms)
        search_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=search_message
        )


        search_term = remove_quotes(search_response.choices[0].message['content'])

    print(f"Generated search term: {search_term}")
    previous_search_terms.append(search_term)

    found_content = False
    search_results = search_brave(search_term)

    if search_results and search_results['results']:
        for result in search_results['results']:
            if result['url'] not in scraped_urls:
                scraped_urls.append(result['url'])
                page_content = get_page_content(result['url'])
                if page_content is not None:
                    if response_text == "":
                        task_message = create_task_message(task, page_content)
                        response = openai.ChatCompletion.create(
                            model="gpt-4",
                            messages=task_message
                        )
                    else:
                        report_update_message = create_report_update_message(task, response_text, page_content)
                        response = openai.ChatCompletion.create(
                            model="gpt-4",
                            messages=report_update_message
                        )
                    response_text = response.choices[0].message['content']
                    print(f"Updated report for task: {response_text}")
                    found_content = True  
                    break

    if action == 'finish':
        session.clear() 
        return response_text, search_history
    elif action == 'next' and not found_content:
        search_message = create_search_message(task, response_text, previous_search_terms)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=search_message
        )
        search_term = remove_quotes(response.choices[0].message['content'])
        print(f"Generated search term: {search_term}")
        previous_search_terms.append(search_term)

    search_history.append((search_term, scraped_urls[-1] if scraped_urls else '')) 

    session['scraped_urls'] = scraped_urls
    session['previous_search_terms'] = previous_search_terms
    session['response_text'] = response_text
    session['search_history'] = search_history

    return response_text, search_history

@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        task = request.form.get('task')
        filename_base = request.form.get('filename')
        if filename_base:  
            session['filename_base'] = filename_base
        action = request.form.get('action')
        rounds = int(request.form.get('rounds'))

        if action == 'start':
            print("Starting autonomous research agent...")
            for i in range(rounds):
                current_response, search_history = autonomous_agent(task, action=action)
                filename = f"results/{session['filename_base']}_result_round_{i+1}.txt"
                with open(filename, 'w') as f:
                    f.write(current_response)
                search_history[-1] += (url_for('download_file', filename=os.path.basename(filename)),)

        elif action == 'next':
            print("Continuing task...")
            for i in range(rounds):
                current_response, search_history = autonomous_agent(task, action=action)
                filename = f"results/{session['filename_base']}_result_round_{i+1}.txt"  # use base filename from session
                with open(filename, 'w', encoding="utf-8") as f:
                    f.write(current_response)
                search_history[-1] += (url_for('download_file', filename=os.path.basename(filename)),)

        session['task'] = task  
        session['response_text'] = current_response  
        session['search_history'] = search_history 

    else:  
        task = session.get('task', '')
        action = session.get('action', '')
        current_response = session.get('response_text', '')
        search_history = session.get('search_history', [])

    return render_template('index.html', current_response=current_response, task=task, search_history=search_history, action=action)

@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    try:
        results_dir = os.path.abspath(os.path.join(os.getcwd(), "results"))
        return send_from_directory(results_dir, filename, as_attachment=True)
    except FileNotFoundError:
        return Response("File not found", status=404)

@app.route("/clear", methods=['GET'])
def clear_session():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(port=5000, debug=True)
