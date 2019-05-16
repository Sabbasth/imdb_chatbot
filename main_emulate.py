import flask
from imdb_chatbot.main import chatbot


app = flask.Flask('functions')


@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path=''):
    flask.request.path = '/' + path
    return chatbot(flask.request)


if __name__ == '__main__':
    app.run()
