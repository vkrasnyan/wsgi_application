import json
import re
import time
from wsgiref.simple_server import make_server


class WsgiApp:
    def __init__(self):
        self.routes = {}

    def route(self, path):
        def wrapper(func):
            count = re.search(r'(<)', path)
            endpoint = path[:count.start()] if count else path
            self.routes[endpoint] = func
            return func
        return wrapper

    def __call__(self, environ, start_response):
        self.environ = environ
        path = self.environ.get('PATH_INFO')
        headers = [('Content-Type', 'application/json')]
        if path == '/hello':
            status = '200 OK'
            response = self.routes[path]()
            start_response(status, headers)
            return [json.dumps(response).encode("utf-8")]
        elif path.startswith('/hello'):
            status = '200 OK'
            query = path.split('/')[2]
            response = self.routes['/hello/'](query)
            start_response(status, headers)
            return [json.dumps(response).encode("utf-8")]
        elif path.startswith('/long_task'):
            time.sleep(90)
            status = '200 OK'
            html_response = ["<!DOCTYPE html>", "<html>", "<body>", "<h1>We did it!</h1>", "</body>", "</html>"]
            start_response(status, [('Content-Type', 'text/html')])
            return [line.encode("utf-8") for line in html_response]
        else:
            status = '404 Static Files'
            html_response = ["<!DOCTYPE html>", "<html>", "<body>", "<h1>Not found</h1>",
                             '<img src="static/error-404.jpg" />', "</body>", "</html>"]
            start_response(status, [('Content-Type', 'text/html')])
            return [line.encode("utf-8") for line in html_response]


application = WsgiApp()

@application.route('/hello')
def hello():
    return {'response': 'Hello World!'}

@application.route('/hello/<name>')
def hello_name(name):
    return {'response': 'Hello {}!'.format(name)}

@application.route('/long_task')
def long_task():
    time.sleep(90)
    return {'response': 'Hello World!'}

if __name__ == '__main__':
    server = make_server('0.0.0.0', 5000, application)
    server.serve_forever()

