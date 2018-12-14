
from .constants import MODEL_CONTENT_TYPES, ATTACHMENT_CONTENT_TYPES

from .attachment import Attachment
from .snapshot import Snapshot

from .errors import FastScoreError
import re

import requests
import six

class ModelMetadata(object):
    def __init__(self, name, mtype):
        self._name = name
        self._mtype = mtype

    @property
    def name(self):
        return self._name

    @property
    def mtype(self):
        return self._mtype

    def to_dict(self):
        return { 'name': self._name, 'mtype': self._mtype }

class Model(object):
    """
    Represents an analytic model. A model can be created directly:

    >>> model = fastscore.Model('model-1')
    >>> model.mtype = 'python'
    >>> model.source = '...'

    Or, retrieved from a Model Manage instance:

    >>> mm = connect.lookup('model-manage')
    >>> model = mm.models['model-1']

    A directly-created model must be saved to make attachment and snapshot
    manipulation functions available:

    >>> mm = connect.lookup('model-manage')
    >>> model.update(mm)
    >>> model.attachments.names()
    []

    """

    @property
    def TYPES():
        return MODEL_CONTENT_TYPES.keys()

    class AttachmentBag(object):
        def __init__(self, model):
            self.model = model

        def names(self):
            return self.model.list_attachments()

        def __iter__(self):
            for x in self.model.list_attachments():
                (atype,sz) = self.model.get_attachment(x)
                yield Attachment(x, atype, None, datasize=sz, model=self.model)

        def __getitem__(self, name):
            (atype,sz) = self.model.get_attachment(name)
            return Attachment(name, atype, None, datasize=sz, model=self.model)

        def __delitem__(self, name):
            self.model.remove_attachment(name)

    class SnapshotBag(object):
        def __init__(self, model):
            self.model = model

        def browse(self, date1=None, date2=None, count=None):
            page = self.model.list_snapshots(date1, date2, count)
            return [ Snapshot(x['id'],
                              x['created_on'],
                              x['type'],
                              x['size'], self.model) for x in page ]

        def __getitem__(self, snapid):
            info =  self.model.get_snapshot(snapid)
            return Snapshot(info['id'],
                            info['created_on'],
                            info['type'],
                            info['size'], self.model)

        def __delitem__(self, snapid):
            self.model.remove_snapshot(snapid)

    def __init__(self, name, mtype='python', source=None, model_manage=None):
        self._mm = model_manage
        self._name = name
        self.mtype = mtype
        self.source = source
        self._attachments = Model.AttachmentBag(self)
        self._snapshots = Model.SnapshotBag(self)

    @property
    def name(self):
        """
        A model name, e.g. 'model-1'.
        """
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def mtype(self):
        """
        A model type:

        * **pfa-json**: a PFA model in JSON format.
        * **pfa-yaml**: a PFA model in YAML format.
        * **pfa-pretty**: a PrettyPFA model.
        * **h2o-java**: an H20 model.
        * **python**: a Python model.
        * **python3**: a Python 3 model.
        * **R**: an R model.
        * **java**: a Java model.
        * **c**: a C model.
        * **octave**: an Octave model.
        * **jupyter**: an Jupyter model.
        * **sas**: a SAS model.

        """
        return self._mtype

    @mtype.setter
    def mtype(self, mtype):
        assert mtype in MODEL_CONTENT_TYPES
        self._mtype = mtype

    @property
    def source(self):
        """
        The source code of the model.
        """
        return self._source

    @source.setter
    def source(self, source):
        self._source = source

    @property
    def attachments(self):
        """
        A collection of model attachments. See :class:`.Attachment`.
        """
        return self._attachments

    @property
    def snapshots(self):
        return self._snapshots

    def update(self, model_manage=None):
        if model_manage == None and self._mm == None:
            raise FastScoreError("Model '%s' not associated with Model Manage" % self.name)
        if self._mm == None:
            self._mm = model_manage
        return self._mm.save_model(self)

    def saved(self):
        if self._mm == None:
            raise FastScoreError("Model '%s' not saved (use update() method)" % self.name)

    def list_attachments(self):
        self.saved()
        try:
            return self._mm.swg.attachment_list(self._mm.name, self.name)
        except Exception as e:
            raise FastScoreError("Cannot list attachments", caused_by=e)

    def get_attachment(self, name):
        self.saved()
        try:
            (_,_,headers) = \
                    self._mm.swg.attachment_head_with_http_info(self._mm.name, \
                            self.name, name)
            ct = headers['content-type']
            sz = int(headers['content-length'])
            for atype,ct1 in ATTACHMENT_CONTENT_TYPES.items():
                if ct1 == ct:
                    return (atype,sz)
            raise FastScoreError("Unrecognized attachment MIME type '%s'" % ct)
        except Exception as e:
            raise FastScoreError("Cannot retrieve attachment '%s'" % name, caused_by=e)

    def download_attachment(self, name):
        self.saved()
        try:
            if six.PY2:
                return self._mm.swg.attachment_get(self._mm.name, self.name, name)
            else: # Python 3
                params = {'host': self._mm.swg.api_client.host,
                          'instance': self._mm.name,
                          'model': self.name,
                          'attachment': name}
                path = "{host}/{instance}/1/model/{model}/attachment/{attachment}".format(**params)
                r = requests.get(path, verify=False)
                if r.status_code == 200:
                    with open(name, 'wb') as f:
                        f.write(r.content)
                    return name
                else:
                    raise FastScoreError("Cannot download attachment '%s'" % name)
        except Exception as e:
            raise FastScoreError("Cannot download attachment '%s'" % name, caused_by=e)

    def remove_attachment(self, name):
        self.saved()
        try:
            self._mm.swg.attachment_delete(self._mm.name, self.name, name)
        except Exception as e:
            raise FastScoreError("Cannot remove attachment '%s'" % name, caused_by=e)

    def save_attachment(self, att):
        self.saved()
        try:
            ct = ATTACHMENT_CONTENT_TYPES[att.atype]

            ##
            ## schema: { type: file }
            ##   is not supported by Swagger 2.0 for in-body parameters.
            ##
            with open(att.datafile, 'rb') as f:
                data = f.read()

            if six.PY2:
                self._mm.swg.attachment_put(self._mm.name, \
                        self.name, att.name, data=data, content_type=ct)
            else:
                params = {'host': self._mm.swg.api_client.host,
                          'instance': self._mm.name,
                          'model': self.name,
                          'attachment': att.name}
                path = "{host}/{instance}/1/model/{model}/attachment/{attachment}".format(**params)
                r = requests.put(path, headers={"content-type":ct}, data=data, verify=False)
                if r.status_code != 201 and r.status_code != 204:
                    raise FastScoreError("Error uploading attachment.")
        except Exception as e:
           raise FastScoreError("Cannot upload attachment '%s'" % att.name, \
                   caused_by=e)

    def list_snapshots(self, date1, date2, count):
        self.saved()
        try:
            params = {}
            if date1 or date2:
                date_range = ''
                if date1:
                    date_range += date1.isoformat()
                date_range += '--'
                if date2:
                    date_range += date2.isoformat()
                params['date_range'] = date_range
            if count:
                params['count'] = count
            return self._mm.swg.snapshot_list(self._mm.name, self.name, **params)
        except Exception as e:
            raise FastScoreError("Cannot list snapshots", caused_by=e)

    def get_snapshot(self, snapid):
        self.saved()
        try:
            return self._mm.swg.snapshot_get_metadata(self._mm.name, self.name, snapid)
        except Exception as e:
            raise FastScoreError("Cannot retrieve snapshot '%s' metadata" % snapid, caused_by=e)

    def download_snapshot(self, snapid):
        self.saved()
        try:
            return self._mm.swg.snapshot_get_contents(self._mm.name, self.name, snapid)
        except Exception as e:
            raise FastScoreError("Cannot retrieve snapshot '%s' contents" % snapid, caused_by=e)

    def remove_snapshot(self, snapid):
        self.saved()
        try:
            self._mm.swg.snapshot_delete(self._mm.name, self.name, snapid)
        except Exception as e:
            raise FastScoreError("Cannot remove snapshot '%s'" % snapid, caused_by=e)

    def deploy(self, engine):
        """
        Deploy this model to an engine.

        :param engine: The Engine instance to use.
        """
        engine.load_model(self)
