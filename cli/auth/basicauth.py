from fastscore.suite import Connect
from fastscore.errors import FastScoreError
from base64 import b64encode
from six.moves.urllib.parse import quote
from getpass import getpass


def encode(username, password):
    """Returns an HTTP basic authentication encrypted string given a valid
    username and password.
    """
    if ':' in username:
        raise FastScoreError('invalid username')

    username_password = '%s:%s' % (quote(username), quote(password))
    return 'Basic ' + b64encode(username_password.encode()).decode()

def login_basicauth(connect, verbose, username=None, password=None):
    if username is None:
        username = raw_input("Username:")
    if password is None:
        password = getpass("Password:")
    connect.set_basic_auth_secret(encode(username, password))