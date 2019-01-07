import yaml
import json
import requests
import sys
import webbrowser

from fastscore.suite import Connect
from os.path import expanduser
from ..colors import tcol
from os import environ

try:
    from urllib import urlencode, unquote
    from urlparse import urlparse, parse_qsl, ParseResult
except ImportError:
    # Python 3
    from urllib.parse import (
        urlencode, unquote, urlparse, parse_qsl, ParseResult
    )

if sys.version_info >= (3, 0):
    from http.server import HTTPServer, BaseHTTPRequestHandler
else:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

CONFIG_PATH = expanduser('~/.fastscore.sessioncookie')
DEFAULT_CONFIG = {
    'login-url': None,
}
REDIRECT_URI = 'http://localhost:1234/auth_callback'
REDIRECT_URI_QUERYPARAMS = [
    'redirect_uri',
    'redirect_url',
    'url',
    'redirect'
]

def read_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.load(f)
    except IOError:
        return DEFAULT_CONFIG

def update_config(new_config):
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(new_config, stream=f)

def login_sessioncookie(connect, verbose, login_url=None):
    def prompt(item, old_value):
        i = raw_input(item + ' [' + str(old_value) + ']:')
        return i if i else old_value

    conf = read_config()
    if login_url is not None:
        conf["login-url"] = login_url
        if verbose:
            print "Using Login URL: " + login_url
    else:
        print "Please make sure that %s is a whitelisted redirect_uri." % REDIRECT_URI 
        conf["login-url"] = prompt("Login URL", conf["login-url"])
    
    conf["login-url"] = add_url_params(conf["login-url"], { p: REDIRECT_URI for p in REDIRECT_URI_QUERYPARAMS})
    if verbose:
        print "Full login url: " + conf["login-url"]

    update_config(conf)

    cookie = get_session_cookie(conf["login-url"])

    connect.set_session_cookie(cookie)
    connect.dump('.fastscore')

    print tcol.OKGREEN + 'Authentication successful' + tcol.ENDC

def add_url_params(url, params):
    # Unquoting URL first so we don't loose existing args
    url = unquote(url)
    # Extracting url info
    parsed_url = urlparse(url)
    # Extracting URL arguments from parsed URL
    get_args = parsed_url.query
    # Converting URL arguments to dict
    parsed_get_args = dict(parse_qsl(get_args))
    # Merging URL arguments dict with new params
    parsed_get_args.update(params)

    # Bool and Dict values should be converted to json-friendly values
    parsed_get_args.update(
        {k: json.dumps(v) for k, v in parsed_get_args.items()
         if isinstance(v, (bool, dict))}
    )

    # Converting URL argument to proper query string
    encoded_get_args = urlencode(parsed_get_args, doseq=True)
    # Creating new parsed result object based on provided with new
    # URL arguments. Same thing happens inside of urlparse.
    new_url = ParseResult(
        parsed_url.scheme, parsed_url.netloc, parsed_url.path,
        parsed_url.params, encoded_get_args, parsed_url.fragment
    ).geturl()

    return new_url

COOKIE=None

class Handler(BaseHTTPRequestHandler, object):
        def __init__(self, *args, **kwargs):
            super(Handler, self).__init__(*args, **kwargs)

        def do_GET(self):
            global COOKIE
            if self.path == "/":
                # Redirect to Authorization URL
                self.send_response(302)
                self.send_header('Location', self.login_url)
                self.end_headers()
            elif self.path.startswith("/auth_callback"):
                # Retrieve Auth token
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write('Authentication successful. You may now close this tab'.encode('utf-8'))
                COOKIE = self.headers.get('Cookie')
            else:
                self.send_error(404, 'Unexpected path, please login at http://localhost:1234')
            self.finish()
        
        def log_message(self, format, *args):
            return

def get_session_cookie(login_url):
    Handler.login_url = login_url

    server = HTTPServer(('0.0.0.0', 1234), Handler)
    print "Please open http://localhost:1234/ in your browser to authenticate."
    webbrowser.open("http://localhost:1234/")

    while COOKIE is None:
        server.handle_request()
    server.server_close()

    return COOKIE