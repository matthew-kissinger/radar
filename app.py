from flask import Flask, request, render_template, send_file, session
import openai
import requests
import tiktoken
import urllib.parse
from bs4 import BeautifulSoup
import openai
import requests
import tiktoken
import urllib.parse
from bs4 import BeautifulSoup
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_bytes(16) 

def remove_quotes(string):
    return string.replace("\"", "")

def create_initial_search_message(task):
    return [
        {
            "role": "system",
            "content": f"Given the task: {task}, please generate a search term or query to initiate focused and reliable information gathering. It is essential to pay more attention to the topic at hand rather than relying solely on a pre-existing report, which may contain inaccurate or poorly scoped information. By conducting thorough research, we can gather up-to-date and reliable data to enhance our understanding of the subject matter."
        }
    ]

def create_search_message(task, response, previous_search_terms):
    return [
        {
            "role": "system",
            "content": f"Given the task: {task}, the response so far: {response}, and the previous search terms: {previous_search_terms}, please generate a new, unique search term that could provide additional information to help complete the task."
        }
    ]
def create_task_message(task, content):
    return [
        {
            "role": "system",
            "content": f"Your primary task is: '{task}'. The following content from the web should assist you: '{content}'. Analyze this content, generate a thoughtful response, and update your Knowledge Log. This log is a repository of your current understanding, challenges, potential solutions, and gaps requiring further investigation. Respond to the task and then update the Knowledge Log. Start with the task's result, followed by an updated knowledge log."
        }
    ]

def create_report_update_message(task, current_report, content):
    return [
        {
            "role": "system",
            "content": f"Your ongoing task is: '{task}'. So far, you've produced this result: '{current_report}'. You have received new content: '{content}'. Your priority is to respond to the task. Enhance the result using this new content, and update your Knowledge Log to reflect your current understanding, any identified challenges, potential solutions, and future steps. Start with the full result of the task, followed by an updated knowledge log."
        }
    ]

def get_page_content(url):
    headers = {"apikey": scraperapi_key}
    response = requests.get(url, headers=headers)
    print(f"Response status code: {response.status_code}")  # Add this line to check the response status code
    if response.status_code == 200:
        print(f"Raw response text: {response.text[:500]}")  # Add this line to print the raw response text (first 500 characters)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        page_content = soup.get_text(separator=' ')
        print(f"Extracted page content: {page_content[:100]}...")  # Add this line to see the first 100 characters of the page content
        tokenizer = tiktoken.get_encoding("cl100k_base")
        tokens = tokenizer.encode(page_content)
        if len(tokens) > 2000:
            excess = len(tokens) - 2000
            page_content = tokenizer.decode(tokens[:-excess])
        print(f"Page Content: {page_content[:100]}...")  # Add this line to see the first 100 characters of the processed page content
        return page_content
    else:
        return None


def search_brave(search_term):
    headers = {"Accept": "application/json", "X-Subscription-Token": brave_search_api_key}
    query = urllib.parse.quote(search_term)
    response = requests.get(f"https://api.search.brave.com/res/v1/web/search?q={query}", headers=headers)
    print(f"Response status code from Brave API: {response.status_code}")  # Added print statement
    if response.status_code == 200:
        response_json = response.json()
        print(f"Response JSON from Brave API: {response_json}")  # Added print statement
        try:
            return response_json['web']
        except KeyError:
            return None
    else:
        return None

def autonomous_agent(task, action='next'):
    openai.api_key = openai_api_key
    scraped_urls = session.get('scraped_urls', [])
    previous_search_terms = session.get('previous_search_terms', [])
    response_text = session.get('response_text', "")
    search_history = session.get('search_history', [])

    initial_search_message = create_initial_search_message(task)
    print(f"Initial search message: {initial_search_message}")  # Debug line
    initial_search_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=initial_search_message
    )
    print("Initial search response from OpenAI:", initial_search_response)  # Print the raw response
    initial_search_term = remove_quotes(initial_search_response.choices[0].message['content'])
    print(f"Initial search term: {initial_search_term}")
    previous_search_terms.append(initial_search_term)

    found_content = False
    search_results = search_brave(initial_search_term)

    if search_results and search_results['results']:
        for result in search_results['results']:
            if result['url'] not in scraped_urls:
                scraped_urls.append(result['url'])
                page_content = get_page_content(result['url'])
                if page_content is not None:
                    if response_text == "":
                        task_message = create_task_message(task, page_content)
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=task_message
                        )
                    else:
                        report_update_message = create_report_update_message(task, response_text, page_content)
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=report_update_message
                        )
                    response_text = response.choices[0].message['content']
                    print(f"Updated report for task: {response_text}")
                    found_content = True  
                    break

    if action == 'finish':
        session.clear() # Clear the session when done
        return response_text, search_history
    elif action == 'next':
        search_message = create_search_message(task, response_text, previous_search_terms)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=search_message
        )
        initial_search_term = remove_quotes(response.choices[0].message['content'])
        print(f"Generated search term: {initial_search_term}")
        previous_search_terms.append(initial_search_term)

    search_history.append((initial_search_term, scraped_urls[-1] if scraped_urls else '')) # Add this line to update search history

    # Save the variables back to the session
    session['scraped_urls'] = scraped_urls
    session['previous_search_terms'] = previous_search_terms
    session['response_text'] = response_text
    session['search_history'] = search_history

    return None, None


@app.route("/", methods=['GET', 'POST'])
def home():
    final_response = None
    search_history = None
    task = None
    action = None
    
    if request.method == 'POST':
        task = request.form.get('task')
        action = request.form.get('action')
        
        if action == 'start':
            print("Starting autonomous research agent...")
            final_response, search_history = autonomous_agent(task, action=action)
            print(f"\nFinal response for task: {final_response}")
            if final_response is not None: # Save final response only when the task is finished
                with open("final_response.txt", "w") as file:
                    file.write(final_response)
        elif action == 'next':
            print("Continuing task...")
            final_response, search_history = autonomous_agent(task, action=action)
            print(f"\nFinal response for task: {final_response}")
            if final_response is not None: # Save final response only when the task is finished
                with open("final_response.txt", "w") as file:
                    file.write(final_response)
        elif action == 'finish':
            print("Finishing task...")
            final_response, search_history = autonomous_agent(task, action=action)
            print(f"\nFinal response for task: {final_response}")
            if final_response is not None: # Save final response only when the task is finished
                with open("final_response.txt", "w") as file:
                    file.write(final_response)
    
    return render_template('index.html', final_response=final_response, task=task, search_history=search_history, action=action)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
