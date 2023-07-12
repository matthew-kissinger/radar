import openai
from flask import current_app, session
from tenacity import retry, stop_after_attempt, wait_random
from .scraping_service import get_page_content
from .search_service import search_brave
from radar.utils.helpers import remove_quotes, create_initial_search_message, create_search_message, create_task_message, create_report_update_message

@retry(stop=stop_after_attempt(5), wait=wait_random(min=5, max=60))
def call_openai_chat_model(model, messages):
    return openai.ChatCompletion.create(model=model, messages=messages)

def autonomous_agent(task, action='next'):
    openai.api_key = current_app.config["OPENAI_API_KEY"]
    scraped_urls = session.get('scraped_urls', [])
    previous_search_terms = session.get('previous_search_terms', [])
    response_text = session.get('response_text', "")
    search_history = session.get('search_history', [])
    highest_round = session.get('highest_round', 0)

    if 'research_started' not in session:
        session['research_started'] = True
        initial_search_message = create_initial_search_message(task)
        initial_search_response = call_openai_chat_model("gpt-4", initial_search_message)
        search_term = remove_quotes(initial_search_response.choices[0].message['content'])
    else:
        search_message = create_search_message(task, response_text, previous_search_terms)
        search_response = call_openai_chat_model("gpt-3.5-turbo-16k", search_message)
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
                        response = call_openai_chat_model("gpt-4", task_message)
                    else:
                        report_update_message = create_report_update_message(task, response_text, page_content)
                        response = call_openai_chat_model("gpt-3.5-turbo-16k", report_update_message)
                    response_text = response.choices[0].message['content']
                    print(f"Updated report for task: {response_text}")
                    found_content = True  
                    break

    if action == 'finish':
        return response_text, search_history
    elif action == 'next' and not found_content:
        search_message = create_search_message(task, response_text, previous_search_terms)
        response = call_openai_chat_model("gpt-3.5-turbo-16k", search_message)
        search_term = remove_quotes(response.choices[0].message['content'])
        print(f"Generated search term: {search_term}")
        previous_search_terms.append(search_term)

    search_history.append((search_term, scraped_urls[-1] if scraped_urls else '', None)) 
    highest_round += 1

    session['scraped_urls'] = scraped_urls
    session['previous_search_terms'] = previous_search_terms
    session['response_text'] = response_text
    session['search_history'] = search_history
    session['highest_round'] = highest_round

    return response_text, search_history
