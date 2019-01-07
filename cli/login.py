from fastscore.suite import Connect
from .version import BUILD_DATE
from . import __version__
from .colors import tcol

from .auth.oauth2 import login_oauth2
from .auth.ldap import login_ldap
from .auth.sessioncookie import login_sessioncookie
from .auth.basicauth import login_basicauth

def login(connect, mode, verbose=False, username=None, password=None, discover_endpoint=None, client_id=None, client_secret=None, login_url=None, **kwargs):
    if mode == "oauth2":
        login_oauth2(connect, verbose, discover_endpoint, client_id, client_secret)
    elif mode == "sessioncookie":
        login_sessioncookie(connect, verbose, login_url)
    elif mode == "ldap":
        login_ldap(connect, verbose, username, password)
    elif mode == "basicauth":
        login_basicauth(connect, verbose, username, password)
    else:
        print tcol.FAIL + "Unknown authentication mode: " + mode + tcol.ENDC
