from fastscore.suite import Connect
from getpass import getpass

def login_ldap(connect, verbose, username=None, password=None):
    if username is None:
        username = raw_input("Username:")
    if password is None:
        password = getpass("Password:")
    connect.ldap_login(username, password)