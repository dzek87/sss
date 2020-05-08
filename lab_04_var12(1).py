# py_ver == "3.6.9"
import flask
import os


app = flask.Flask(__name__)


import requests


import json
import time


@app.route('/feedback_form')
def introduction():
    feedback = ''
    path = 'feedback.json'
    if os.path.exists(path):
        with open(path, 'r') as feedback_file:
            feedback_dict = json.loads(feedback_file.read())
            for key, value in feedback_dict.items():
                feedback += "<p><i>Анононим, %s</i>: %s</p>" % (key, value)
    return """<html>
                <title>Обратная связь</title>
                <body>
                %s
                    <form action="/save_feedback" method="post">
                        Поделитесь своим мнением: <input name="feedback" type="text" />
                        <input name="submit" type="submit" value="Отправить">
                    </form>
                </body>
            </html>
""" % feedback


@app.route('/save_feedback', methods=["GET", "POST"])
def index_page():
    if flask.request.method == 'POST':
        feedback = flask.request.form.get('feedback')
        feedback_dict = {}
        path = 'feedback.json'
        if os.path.exists(path):
            with open(path, 'r') as feedback_file:
                feedback_dict.update(json.load(feedback_file))
        feedback_dict[time.time()] = feedback
        with open(path, 'w') as feedback_file:
            json.dump(feedback_dict, feedback_file)
    return flask.redirect('/feedback_form')


@app.route('/send_proxy_request')
def send_proxy_request():
    return """
            <html>
                <title>What to GET</title>
                <body>
                    <form action="/proxy_get">
                        Enter URL: <input name="url" type="text" />
                        <input name="submit" type="submit">
                    </form>
                </body>
            </html>
"""


import requests


@app.route('/proxy_get')
def proxy_get():
    url = flask.request.args.get('url')
    if url and url.startswith(('http://', 'https://')):
        result = requests.get(url)
        return "%s" % result.text
    else:
        return flask.redirect('/send_proxy_request')


@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['X-Content-Security-Policy'] = "default-src 'self'"
    return response


if __name__ == '__main__':
    # to ensure requests' version: pip install "requests<=2.19.1"
    # but 2.19.1 had a vulnerability, so use "requests>2.19.1"
    # check internet connection is available trying to ping google
    try:
        requests.get('https://google.com')
    except (requests.ConnectionError, requests.ConnectTimeout):
        print('No connection')
    else:
        app.run()
