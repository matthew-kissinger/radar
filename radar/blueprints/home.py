from flask import Blueprint, render_template, request, session, url_for, send_from_directory, Response, redirect
from radar.services.openai_service import autonomous_agent
import os

home_blueprint = Blueprint('home', __name__)

@home_blueprint.route("/", methods=['GET', 'POST'])
def home():
    filename = None
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
                highest_round = session.get('highest_round', 0)  # Retrieve the updated highest_round value from the session
                filename = f"{session['filename_base']}_result_round_{highest_round}.txt"  # Use highest_round in the filename
                print(f"DEBUG: Filename is {filename}")  # Debug print
                with open("results/" + filename, 'w') as f:
                    f.write(current_response)
                search_history[-1] += (url_for('home.download_file', filename=filename),)

        elif action == 'next':
            print("Continuing task...")
            for i in range(rounds):
                current_response, search_history = autonomous_agent(task, action=action)
                highest_round = session.get('highest_round', 0)  # Retrieve the updated highest_round value from the session
                filename = f"{session['filename_base']}_result_round_{highest_round}.txt"  # Use highest_round in the filename
                print(f"DEBUG: Filename is {filename}")  # Debug print
                with open("results/" + filename, 'w', encoding="utf-8") as f:
                    f.write(current_response)
                search_history[-1] = search_history[-1][:2] + (url_for('home.download_file', filename=filename),)
                print(f"DEBUG: Download URL is {search_history[-1][-1]}")  # Debug print

        session['task'] = task  
        session['response_text'] = current_response  
        session['search_history'] = search_history 

    else:  
        task = session.get('task', '')
        action = session.get('action', '')
        current_response = session.get('response_text', '')
        search_history = session.get('search_history', [])
        filename = session.get('filename', '')  # Add this line to get the filename from the session

    return render_template('index.html', current_response=current_response, task=task, search_history=search_history, action=action, filename=filename)

import os

@home_blueprint.route("/download/<path:filename>", methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(os.path.join(os.getcwd(), 'results'), filename, as_attachment=True)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return Response("File not found", status=404)


@home_blueprint.route("/clear", methods=['GET'])
def clear_session():
    session.clear()
    return redirect(url_for('home.home'))
