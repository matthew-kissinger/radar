from datetime import datetime

current_date = datetime.now().strftime('%Y-%m-%d') 

def remove_quotes(string):
    return string.replace("\"", "")

def create_initial_search_message(task):
    return [
        {
            "role": "system",
            "content": f"As an autonomous research agent, your task is: '{task}'. The current date is {current_date}. Generate an initial search URL related to this task. The response should be in the format: 'URL: \"<url>\"'. Use the Brave Web Search API endpoint (https://api.search.brave.com/res/v1/web/search). Essential parameters include 'q' for query (max 400 chars, 50 words) and 'freshness' for time period ('pd' for last 24 hours, 'pw' for last 7 days, 'pm' for last month, 'py' for last year, or specific date range in 'YYYY-MM-DDtoYYYY-MM-DD' format). The freshness parameter is optional and may or may not be needed."
        }
    ]

def create_search_message(task, response, previous_search_terms):
    return [
        {
            "role": "system",
            "content": f"As an autonomous research agent, your ongoing task is: '{task}', and the response so far is: '{response}'. The current date is {current_date}. Considering your previous searches: {previous_search_terms}, generate a search URL related to this task. The response should be in the format: 'URL: \"<url>\"'. Use the Brave Web Search API endpoint (https://api.search.brave.com/res/v1/web/search). Essential parameters include 'q' for query (max 400 chars, 50 words)and 'freshness' for time period ('pd' for last 24 hours, 'pw' for last 7 days, 'pm' for last month, 'py' for last year, or specific date range in 'YYYY-MM-DDtoYYYY-MM-DD' format). The freshness parameter is optional and may or may not be needed."
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
            "content": f"As an autonomous research agent, your ongoing task is: '{task}'. Your previous response was: '{current_report}'. The current date is {current_date}. Analyze the new content and synthesize the complete report using previous response and new content: '{content}'. Compare the content. Structure your response as follows: The updated and complete result of the task, a detailed response with updated findings, and your updated and complete knowledge log. Remember to carry forward this Knowledge Log for future iterations."
        }
    ]
