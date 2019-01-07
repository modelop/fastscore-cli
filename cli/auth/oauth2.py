import yaml
import json
import requests
import sys
import webbrowser

from fastscore.suite import Connect
from os.path import expanduser
from ..colors import tcol
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.clients import WebApplicationClient
from os import environ

if sys.version_info >= (3, 0):
    from http.server import HTTPServer, BaseHTTPRequestHandler
else:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

CONFIG_PATH = expanduser('~/.fastscore.oauth2')
DEFAULT_CONFIG = {
    'client-id': None,
    'requires-client-secret': True,
    'client-secret': None,
    'has-discovery-endpoint': False,
    'discovery-endpoint': None,
    'authorization-url': None,
    'token-url': None,
    'scope': 'email'
}
REDIRECT_URI = 'http://localhost:1234/auth_callback'

def read_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.load(f)
    except IOError:
        return DEFAULT_CONFIG

def update_config(new_config):
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(new_config, stream=f)

def login_oauth2(connect, verbose, discover_endpoint=None, client_id=None, client_secret=None):
    conf = read_config()
    if discover_endpoint is not None:
        conf["discover-endpoint"] = discover_endpoint
        if verbose:
            print "Using Discover Endpoint: " + discover_endpoint
    if client_id is not None:
        conf["client-id"] = client_id
        if verbose:
            print "Using Client ID: " + client_id
    if client_secret is not None:
        conf["client-secret"] = client_secret
        if verbose:
            print "Using Client Secret: " + client_secret

    if discover_endpoint is not None and client_id is not None:
        conf["requires-client-secret"] = False
        conf["has-discovery-endpoint"] = True
        if verbose:
            print "Fetching authorization_url, token_url, scope from discovery endpoint"
        conf["authorization-url"], conf["token-url"], conf["scope"] = fetch_discovery_endpoint(conf["discovery-endpoint"])
        if verbose:
            print "Got authorization-url: " + conf["authorization-url"]
            print "Got token-url: " + conf["token-url"]
            print "Got scope: " + conf["scope"]
    else:
        if verbose and (discover_endpoint is not None and client_id is None):
            print tcol.WARNING + "Additional config needed: client_id not provided" + tcol.ENDC
        if verbose and (client_id is not None and discover_endpoint is None) is not None:
            print tcol.WARNING + "Additional config needed: discover_endpoint not provided" + tcol.ENDC

        conf = prompt_info(conf, verbose)

    update_config(conf)

    token = get_token(conf["client-id"], conf["client-secret"], conf["authorization-url"], conf["token-url"], conf["scope"])

    connect.set_oauth_secret(token['access_token'])
    connect.dump('.fastscore')

    print tcol.OKGREEN + 'Authentication successful' + tcol.ENDC


def fetch_discovery_endpoint(discovery_endpoint):
    try:
        ds = json.loads(requests.get(discovery_endpoint, verify=False).text)
        authorization_url = ds["authorization_endpoint"]
        token_url = ds["token_endpoint"]
        scope = ds["scopes_supported"][0] # Take any valid scope
        return authorization_url, token_url, scope
    except Exception as e:
        print tcol.FAIL + "Unable to fetch config from discovery endpoint" + tcol.ENDC
        sys.exit(1)


def prompt_info(conf, verbose):
    def prompt(item, old_value):
        i = raw_input(item + ' [' + str(old_value) + ']:')
        return i if i else old_value
    print "Please make sure http://localhost:1234/auth_callback is a whitelisted redirect_uri in your OAuth provider settings."
    conf["client-id"] = prompt("Client ID", conf["client-id"])

    conf["requires-client-secret"] = prompt("Does your OAuth provider require a Client Secret to perform an Authorization Code Grant Flow? [Y/N]", "Y" if conf["requires-client-secret"] else "N")
    while conf["requires-client-secret"] not in ["Y", "N"]:
        conf["requires-client-secret"] = prompt("Invalid input. Please enter \"Y\" or \"N\"", "")
    conf["requires-client-secret"] = conf["requires-client-secret"] == "Y"

    if conf["requires-client-secret"]:
        conf["client-secret"] = prompt("Client Secret", conf["client-secret"])
    
    conf["has-discovery-endpoint"] = prompt("Does your OAuth provider have a discovery endpoint? [Y/N]", "Y" if conf["has-discovery-endpoint"] else "N")
    while conf["has-discovery-endpoint"] not in ["Y", "N"]:
        conf["has-discovery-endpoint"] = prompt("Invalid input. Please enter \"Y\" or \"N\"", "")
    conf["has-discovery-endpoint"] = conf["has-discovery-endpoint"] == "Y"

    if conf["has-discovery-endpoint"]:
        conf["discovery-endpoint"] = prompt("Discovery Endpoint", conf["discovery-endpoint"])
        if verbose:
            print "Fetching authorization_url, token_url, scope from discovery endpoint"
        conf["authorization-url"], conf["token-url"], conf["scope"] = fetch_discovery_endpoint(conf["discovery-endpoint"])
        if verbose:
            print "Got authorization-url: " + conf["authorization-url"]
            print "Got token-url: " + conf["token-url"]
            print "Got scope: " + conf["scope"]
    else:
        print """
Since your OAuth provider does not have a discovery endpoint,
you will need to provide the following information manually."""
        conf["authorization-url"] = prompt("Authorization Endpoint", conf["authorization-url"])
        conf["token-url"] = prompt("Token Endpoint", conf["token-url"])
        conf["scope"] = prompt("Authorization Sope", conf["scope"])
    return conf


TOKEN=None

class Handler(BaseHTTPRequestHandler, object):
        def __init__(self, *args, **kwargs):
            super(Handler, self).__init__(*args, **kwargs)

        def do_GET(self):
            global TOKEN
            if self.path == "/":
                # Redirect to Authorization URL
                self.send_response(302)
                self.send_header('Location', self.authorization_url)
                self.end_headers()
            elif self.path.startswith("/auth_callback"):
                # Retrieve Auth token
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write('Authentication successful. You may now close this tab'.encode('utf-8'))
                TOKEN = self.provider.fetch_token(self.token_url, client_secret=self.client_secret, client_id=self.client_id, authorization_response=self.path, verify=False, auth=False, headers={'Cookie': self.headers.get('Cookie')})
            else:
                self.send_error(404, 'Unexpected path, please login at http://localhost:1234')
            self.finish()
        
        def log_message(self, format, *args):
            return

def get_token(
        client_id=None,
        client_secret=None,
        authorization_url=None,
        token_url=None,
        scope='email'
    ):
    Handler.client_id = client_id
    Handler.client_secret = client_secret
    Handler.token_url = token_url

    environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    Handler.provider = OAuth2Session(client_id, redirect_uri=REDIRECT_URI, scope=[scope])
    Handler.authorization_url, Handler.oauth_state = Handler.provider.authorization_url(authorization_url)

    server = HTTPServer(('0.0.0.0', 1234), Handler)
    print "Please open http://localhost:1234/ in your browser to authenticate."
    webbrowser.open("http://localhost:1234/")

    while TOKEN is None:
        server.handle_request()
    server.server_close()

    return TOKEN