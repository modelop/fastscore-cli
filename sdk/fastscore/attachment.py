
from os.path import getsize

from .constants import ATTACHMENT_CONTENT_TYPES
from .errors import FastScoreError

class Attachment(object):
    """
    Represents a model attachment. An attachment can be created directly but it
    must (ultimately) associated with the model:

    >>> att = fastscore.Attachment('att-1', datafile='/tmp/att1.zip')
    >>> model = mm.models['model-1']
    >>> att.upload(model)

    :param atype: An attachment type. Guessed from the data file name if omitted.
    :param datafile: The data file.
    :param model: The model instance.

    """

    def __init__(self, name, atype=None, datafile=None, datasize=None, model=None):
        self._name = name
        if atype == None and datafile != None:
            atype = guess_type(datafile)
        self._atype = atype
        if datasize == None and datafile != None:
            datasize = getsize(datafile)
        self._datasize = datasize
        self._datafile = datafile
        self._model = model

    @property
    def name(self):
        """
        An attachment name.
        """
        return self._name

    @property
    def atype(self):
        """
        An attachment type.

        * **zip** A ZIP archive.
        * **tgz** A gzipped tarball.

        """
        return self._atype

    @atype.setter
    def atype(self, atype):
        assert atype in ATTACHMENT_CONTENT_TYPES
        self._atype = atype

    @property
    def datafile(self):
        """
        A name of the file that contains the attachment data. The attachment is downloaded
        when this property is first accessed.
        """
        if self._datafile == None:
            self._datafile = self._model.download_attachment(self._name)
        return self._datafile

    @datafile.setter
    def datafile(self, datafile):
        self._datafile = datafile
        if datafile:
            self._datasize = getsize(datafile)
        else:
            self._datasize = None

    @property
    def datasize(self):
        """
        The size of the attachment. Checking the attachment size does NOT trigger the download.
        """
        return self._datasize

    def upload(self, model=None):
        """
        Adds the attachment to the model.

        :param model: The model instance. Can be None if the model instance has been provided
          when the attachemnet was created.

        """
        if model == None and self._model == None:
            raise FastScoreError("Attachment '%s' not associated with a model" % self.name)
        if self._model == None:
            self._model = model
        self._model.save_attachment(self)

def guess_type(datafile):
    if datafile.endswith('.zip'):
        return 'zip'
    elif datafile.endswith('.tar.gz'):
        return 'tgz'
    elif datafile.endswith('.tgz'):
        return 'tgz'
    else:
        raise FastScoreError("Unable to guess attachment type for '%s'" % datafile)
