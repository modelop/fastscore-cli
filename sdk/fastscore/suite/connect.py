
from ..v1 import configuration
from ..v2 import configuration as configuration2
from ..v1 import ConnectApi
from ..v2 import ConnectApi as ConnectApi2
from ..v1 import LoginApi
from ..v1.rest import ApiException

from .instance import InstanceBase
from .model_manage import ModelManage
from .engine import Engine
from ..errors import FastScoreError

from ..pneumo import PneumoSock
import six
if six.PY2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse
import yaml

#configuration.debug = True

if six.PY2:
    from urllib import quote, unquote
else:
    from urllib.parse import quote, unquote

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def set_basicauth_secret(basicauth_secret, client1, client2):
    client1.set_default_header('Authorization', basicauth_secret)
    client2.set_default_header('Authorization', basicauth_secret)

def set_auth_cookie(auth_secret, client1, client2):
    cookie = 'connect.sid=' + quote(auth_secret)
    client1.cookie = cookie
    client2.cookie = cookie

def unset_auth_cookie(client1, client2):
    client1.cookie = None
    client2.cookie = None

class Connect(InstanceBase):
    """An instance of a Connect service.

    Typically, an interaction with FastScore starts with:

    >>> from fastscore.suite import Connect
    >>> connect = Connect("https://localhost:8000")

    Afterwards, you can use 'connect' to access other FastScore instances.
    For example:

    >>> engine = connect.lookup('engine')

    """

    def __init__(self, proxy_prefix, auth_secret=None, basicauth_secret=None):
        """
        :param proxy_prefix: URL of the FastScore proxy endpoint
        """

        if not '://' in proxy_prefix:
            raise FastScoreError("Proxy prefix must be an URL, e.g. https://dashboard:8000")

        if not proxy_prefix.startswith('https:'):
            raise FastScoreError("Proxy prefix must use HTTPS scheme")

        # https://localhost:8000/api/1/service
        x = urlparse(configuration.host)
        base_path = x.path
        configuration.host = proxy_prefix + base_path
        configuration.verify_ssl = False

        # REST API v2
        x = urlparse(configuration2.host)
        base_path = x.path
        configuration2.host = proxy_prefix + base_path
        configuration2.verify_ssl = False

        super(Connect, self).__init__('connect', 'connect', ConnectApi(), ConnectApi2())
        self._proxy_prefix = proxy_prefix
        self._resolved = {}
        self._preferred = {}
        self._target = None
        self._auth_secret = auth_secret
        self._basicauth_secret = basicauth_secret
        if auth_secret:
            set_auth_cookie(auth_secret, self.swg.api_client, self.swg2.api_client)
        if basicauth_secret:
            set_basicauth_secret(basicauth_secret, self.swg.api_client, self.swg2.api_client)
        self._pneumo =  Connect.PneumoProxy(self)

    @property
    def target(self):
        """
        Gets/Sets the target instance. When set, the target instance also
        becomes the preferred instance of the service it represents.

        >>> engine = connect.get('engine-3')
        >>> connect.target = engine

        """
        return self._target

    @target.setter
    def target(self, instance):
        self.prefer(instance.api, instance.name)
        self._target = instance

    class PneumoProxy(object):
        def __init__(self, connect):
            self._connect = connect

        def socket(self, **kwargs):
            try:
                return PneumoSock(self._connect._proxy_prefix, basicauth_secret=self._connect._basicauth_secret, **kwargs)
            except Exception as e:
                raise FastScoreError("Unable to open Pneumo socket", caused_by=e)

        def history(self, asjson=False, **kwargs):
            try:
                history = self._connect.swg2.pneumo_get(self._connect.name, **kwargs)
                if asjson:
                    return history
                else:
                    return map(PneumoSock.makemsg, history)
            except Exception as e:
                raise FastScoreError("Unable to retrieve Pneumo history", caused_by=e)

    @property
    def pneumo(self):
        """
        Access Pneumo messages.

        >>> pneumo = connect.pneumo.socket()
        >>> pneumo.recv()
        >>> pneumo.close()

        >>> connect.pneumo.history()

        """
        return self._pneumo

    def lookup(self, sname):
        """
        Retrieves an preferred/default instance of a named service.

        >>> engine = connect.lookup('engine')
        >>> engine.name
        'engine-1'

        :param sname: a FastScore service name, e.g. 'model-manage'.
        :returns: a FastScore instance object.
        """
        if sname in self._preferred:
            return self.get(self._preferred[sname])
        try:
            xx = self.swg.connect_get(self.name, api=sname)
        except Exception as e:
            raise FastScoreError("Cannot retrieve fleet info", caused_by=e)
        for x in xx:
            if x.health == 'ok':
                return self.get(x.name)
        if len(xx) == 0:
            m = "No instances of service '%s' configured" % sname
        elif len(xx) == 1:
            m = "'%s' instance is unhealthy" % xx[0].name
        else:
            m = "All %d instances of service '%s' are unhealthy" % len(xx)
        raise FastScoreError(m)

    def get(self, name):
        """
        Retrieves a (cached) reference to the named instance.

        >>> mm = connect.get('model-manage-1')
        >>> mm.name
        'model-manage-1'

        :param name: a FastScore instance name.
        :returns: a FastScore instance object.
        """
        if name == 'connect':
            return self
        if name in self._resolved:
            return self._resolved[name]
        try:
            xx = self.swg.connect_get(self.name, name=name)
        except Exception as e:
            raise FastScoreError("Cannot retrieve '%s' instance info" % name, caused_by=e)
        if len(xx) > 0 and xx[0].health == 'ok':
            x = xx[0]
            instance = Connect.make_instance(x.api, name)
            self._resolved[name] = instance
            return instance
        if len(xx) == 0:
            m = "Instance '%s' not found" % name
        else:
            m = "Instance '%s' is unhealthy" % name
        raise FastScoreError(m)

    def prefer(self, sname, name):
        """
        Marks the named instance as preferred for a given service.

        >>> connect.prefer('engine', 'engine-3')
        >>> engine = connect.lookup('engine')
        >>> engine.name
        'engine-3'

        :param sname: a FastScore service name, e.g. 'model-manage'.
        :param name: the name of preferred instance of the given service.
        """
        self._preferred[sname] = name

    def login(self, username, password):
        """
        Login to FastScore.

        :param username: a user name.
        :param password: a password.
        """
        save = self.swg.api_client.host
        try:
            unset_auth_cookie(self.swg.api_client, self.swg2.api_client)
            login_api = LoginApi()
            login_api.api_client.host = self._proxy_prefix
            (_,_,headers) = login_api.login_post_with_http_info(username, password)
            cookie = headers['set-cookie']
            # connect.sid=s%3A_co96d1eLi2Iwu2JJATxPbhBlVaFSGV4.G53EHnUrubrL87LFEKiSArJ%2BIN05FbwRVRGGkGS6ysM;
            auth_secret = unquote(cookie.split(';')[0].split('=')[1])
            self.swg.api_client.host = save
            self._auth_secret = auth_secret
            set_auth_cookie(auth_secret, self.swg.api_client, self.swg2.api_client)
        except Exception as e:
            self.swg.api_client.host = save
            raise FastScoreError("Access denied", caused_by=e)

    def configure(self, config):
        """
        Sets the FastScore configuration.

        >>> with open('config.yaml') as f:
        >>>   connect.configure(yaml.load(f))
        False

        :param config: a dict describing a FastScore configuration.
        :returns: True, if an existing configuration has been replaced and False,
            otherwise.
        """

        if not isinstance(config, dict):
            raise FastScoreError("Configuration must be a dictionary")

        try:
            (_,status,_) = self.swg.config_put_with_http_info(self.name, \
                config=yaml.dump(config), \
                content_type='application/x-yaml')
            return status == 204
        except Exception as e:
            raise FastScoreError("Unable to set FastScore configuration", caused_by=e)

    def get_config(self, section=None):
        """
        Retrieves the current FastScore configuration.

        >>> connect.config('db')
        {
          'username': 'root',
          'host': 'database',
          'password': 'root',
          'type': 'mysql',
          'port': 3306
        }

        :param section: gets only the named section of the configuration
        :returns: a dict with the FastScore configuration.
        """

        try:
            if section:
                # Swagger does not check parameter type
                if not isinstance(section, str):
                    raise TypeError("Section must be a string")
                conf = self.swg.config_get(self.name, \
                    q=section, \
                    accept='application/x-yaml')
            else:
                conf = self.swg.config_get(self.name, \
                    accept='application/x-yaml')
            return conf
        except Exception as e:
            if isinstance(e, ApiException) and e.status == 404:
                return None ## not yet configured
            raise FastScoreError("Cannot retrieve configuration", caused_by=e)

    def fleet(self):
        """
        Retrieves metadata for all running instances.

        :returns: an array of dicts describing running FastScore instances. Each
            dict contains the following fields:

            * **id**: the internal instance id (do not use)
            * **api**: the service name, e.g. 'model-manage'
            * **release**: the instance release, e.g '1.5'
            * **built_on**: the human-readable build date and time
            * **host**: the host name of the instance REST API
            * **port**: the port of the instance REST API
            * **health**: the current health status of the instance.
        """
        try:
            return self.swg.connect_get(self.name)
        except Exception as e:
            raise FastScoreError("Cannot retrieve fleet info", caused_by=e)

    @staticmethod
    def make_instance(api, name):
        if api == 'model-manage':
            return ModelManage(name)
        else:
            assert api == 'engine'
            return Engine(name)

    def dump(self, savefile):
        """
        Saves the Connect parameters to a file.

        >>> connect.dump(".fastscore")

        """
        try:
            cap = {
                'proxy-prefix': self._proxy_prefix,
                'preferred':    self._preferred,
                'target-name':  self.target.name if self.target else None,
                'auth-secret':  self._auth_secret,
                'basicauth-secret': self._basicauth_secret,
            }
            with open(savefile, "w") as f:
                yaml.dump(cap, stream = f)
        except Exception as e:
            raise FastScoreError("Unable to save Connect info", caused_by=e)

    @staticmethod
    def load(savefile):
        """
        Recreates a Connect instance from a file.

        >>> connect = Connect.load(".fastscore")

        """
        try:
            with open(savefile, "r") as f:
                cap = yaml.load(f)
                auth_secret = cap['auth-secret'] if 'auth-secret' in cap else None
                basicauth_secret = cap['basicauth-secret'] if 'basicauth-secret' in cap else None
                connect = Connect(cap['proxy-prefix'], auth_secret, basicauth_secret)
                connect._preferred = cap['preferred']
                if cap['target-name']:
                    try:
                        connect.target = connect.get(cap['target-name'])
                    except:
                        pass
                return connect
        except Exception as e:
            raise FastScoreError("Unable to recreate a Connect instance", caused_by=e)
