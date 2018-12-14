
import random
import six

if six.PY2:
    from urllib import unquote
else:
    from urllib.parse import unquote
from base64 import b64encode

from fastscore.errors import FastScoreError

LITERAL_EXAMPLES = {
    "http": "https://myhost.com/mydata.json",
    "https": "https://myhost.com/mydata.json",
    "kafka": "kafka:mybroker:9092/topic.json",
    "rest": "rest:",
    "rest-chunked": "rest-chunked:",
    "file": "file:/path/to/mydata.json",
    "tcp": "tcp:myhost.com:1234",
    "udp": "udp:10.0.0.1:124",
    "exec": "exec:myscript.sh",
    "inline": "inline:1,2,3",
    "inline-chunked": "inline-chunked:%06abc",
    "discard": "discard:",
}

class StreamMetadata(object):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

class Stream(object):
    """
    A FastScore stream. A stream can be created directly:

    >>> stream = Stream('stream-1')
    >>> stream.desc = {'Transport':...}

    Or, retrieved from a Model Manage instance:

    >>> mm = connect.lookup('model-manage')
    >>> stream = mm.streams['stream-1']

    """

    def __init__(self, name, desc=None, model_manage=None):
        self._name = name
        self.desc = desc
        self._mm = model_manage

    @property
    def name(self):
        """
        A stream name.
        """
        return self._name

    @property
    def desc(self):
        """
        A stream descriptor (a dict).

        >>> stream = mm.streams['stream-1']
        >>> stream.desc
        {'Transport': {'Type': 'discard'}, 'Encoding': 'json'}

        """
        return self._desc

    @desc.setter
    def desc(self, desc):
        self._desc = desc

    def sample(self, engine, n=None):
        """
        Retrieves a few sample records from the stream.

        :param engine: An Engine instance to use.
        :param n: A number of records to retrieve (default: 10).
        :returns: An array of base64-encoded records.

        """
        return engine.sample_stream(self, n)

    def rate(self, engine):
        """
        Measures the stream throughput outside of a data pipeline.

        :param engine: An Engine instance to use.

        """
        return engine.rate_stream(self)

    def update(self, model_manage=None):
        """
        Saves the stream to Model Manage.

        :param model_manage: The Model Manage instance to use. If None, the Model Manage instance
            must have been provided when then stream was created.

        """
        if model_manage == None and self._mm == None:
            raise FastScore("Stream '%s' not associated with Model Manage" % self.name)
        if self._mm == None:
            self._mm = model_manage
        return self._mm.save_stream(self)

    def attach(self, engine, slot, dry_run=False):
        """
        Attach the stream to the engine.

        :param slot: The stream slot.

        """
        return engine.attach_stream(self, slot, dry_run)

    # See https://opendatagoup.atlassian.net/wiki/x/GgCHBQ
    @staticmethod
    def expand(urllike):
        if urllike.find(':') == -1:
            raise FastScoreError("{} is not a literal descriptor".format(urllike))
        tag,more = urllike.split(':', 1)
        if not tag in LITERAL_EXAMPLES:
            raise FastScoreError("transport tag unknown: {}".format(tag))

        def parse_literal(tag, more):
            if tag == 'http' or tag == 'https':
                return {
                    "Type": "HTTP",
                    "Url": "{}:{}".format(tag, more),
                }, more

            elif tag == 'kafka':
                broker,topic = more.split('/')
                port = 9092
                if broker.find(':') != -1:
                    broker,port = broker.split(':')
                    port = int(port)
                pos = topic.rfind('.')
                if pos != -1:
                    topic = topic[:pos]
                return {
                    "Type": "Kafka",
                    "BootstrapServers": ["{}:{}".format(broker, port)],
                    "Topic": topic,
                    }, more

            elif tag == 'rest':
                assert more == ''
                return "REST", None

            elif tag == 'rest-chunked':
                assert more == ''
                return {
                    "Type": "REST",
                    "Mode": "chunked"
                }, None

            elif tag == 'file':
                assert more.startswith('/') # absolute paths only
                return {
                    "Type": "file",
                    "Path": more
                }, more

            elif tag == 'tcp':
                host,port = more.split(':')
                port = int(port)
                return {
                    "Type": "TCP",
                    "Host": host if host != '' else '0.0.0.0',
                    "Port": port,
                }, None

            elif tag == 'udp':
                host,port = more.split(':')
                port = int(port)
                tt = {
                    "Type": "UDP",
                    "Port": port,
                }
                if host != '':
                    tt["Host"] = host
                return tt,None

            elif tag == 'exec':
                return {
                    "Type": "exec",
                    "Run": more
                }, None

            elif tag == 'inline':
                if more.find('%') != -1:    # url-encoded
                    data = unquote(more).split(',')
                    data = [ b64encode(x) for x in data ]
                    return {
                        "Type": "inline",
                        "DataBinary": data,
                    }, None
                else:
                    return {
                        "Type": "inline",
                        "Data": more.split(',')
                    }, None

            elif tag == 'inline-chunked':
                if more.find('%') != -1:    # url-encoded
                    return {
                        "Type": "inline",
                        "DataBinary": b64encode(unquote(more))
                    }, None
                else:
                    return {
                        "Type": "inline",
                        "Data": more
                    }, None

            elif tag == 'discard':
                assert more == ''
                return "discard", None

        try:
            tt,guess = parse_literal(tag, more)
        except:
            x = "a valid {} literal example: {}".format(tag, LITERAL_EXAMPLES[tag])
            raise FastScoreError("literal descriptor parse error ({})".format(x))

        encoding = 'json'
        if guess:
            if guess.endswith('.json'):
                encoding = 'json'
            elif guess.endswith('.avro'):
                encoding = 'avro-binary'
            elif guess.endswith('.utf8'):
                encoding = 'utf8'
            elif guess.endswith('.bin'):
                encoding = None

        name = 'inline-{}'.format(random.randint(0, 1000000))
        desc = {
            'Transport': tt,
            'Encoding': encoding
        }

        return Stream(name, desc)
