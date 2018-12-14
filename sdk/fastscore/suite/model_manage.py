
from .instance import InstanceBase
from ..model import Model, ModelMetadata
from ..schema import Schema, SchemaMetadata
from ..stream import Stream, StreamMetadata
from ..sensor import Sensor, SensorMetadata
from ..errors import FastScoreError
from ..v1.rest import ApiException

from ..constants import MODEL_CONTENT_TYPES

from ..v1 import ModelManageApi
from ..v2 import ModelManageApi as ModelManageApi2

class ModelManage(InstanceBase):
    """
    An instance of a Model Manage service. Use :class:`.Connect` to create a
    ModelManage instance:

    >>> mm = connect.lookup('model-manage')

    """

    class ModelBag(object):
        def __init__(self, model_manage):
            self.mm = model_manage

        def names(self):
            try:
                return self.mm.swg.model_list(self.mm.name)
            except Exception as e:
                raise FastScoreError("Cannot list models", caused_by=e)

        def __iter__(self):
            for x in self.mm.swg.model_list(self.mm.name, _return='type'):
                yield ModelMetadata(x['name'], x['type'])

        def __getitem__(self, name):
            try:
                (source,_,headers) = self.mm.swg.model_get_with_http_info(self.mm.name, name)
            except Exception as e:
                if isinstance(e, ApiException) and e.status == 404: # less scary
                    raise FastScoreError("Model '%s' not found" % name)
                else:
                    raise FastScoreError("Cannot retrieve '%s' model" % name, caused_by=e)
            ct = headers['content-type']
            for mtype,ct1 in MODEL_CONTENT_TYPES.items():
                if ct1 == ct:
                    return Model(name, mtype=mtype, source=source, model_manage=self.mm)
            raise FastScoreError("Unexpected model MIME type '%s'" % ct)

        def __setitem__(self, name, what):
            raise FastScoreError("Model assignment not allowed (use update() method)")

        def __delitem__(self, name):
            try:
                self.mm.swg.model_delete(self.mm.name, name)
            except Exception as e:
                if isinstance(e, ApiException) and e.status == 404: # less scary
                    raise FastScoreError("Model '%s' not found" % name)
                else:
                    raise FastScoreError("Cannot remove model '%s'" % name, caused_by=e)

    class SchemaBag(object):
        def __init__(self, model_manage):
            self.mm = model_manage

        def names(self):
            try:
                return self.mm.swg.schema_list(self.mm.name)
            except Exception as e:
                raise FastScoreError("Cannot list schemas", caused_by=e)

        def __iter__(self):
            try:
                for x in self.mm.swg.schema_list(self.mm.name):
                    yield SchemaMetadata(x)
            except Exception as e:
                raise FastScoreError("Cannot iterate schemas", caused_by=e)

        def __getitem__(self, name):
            try:
                source = self.mm.swg.schema_get(self.mm.name, name)
            except Exception as e:
                if isinstance(e, ApiException) and e.status == 404:
                    raise FastScoreError("Schema '%s' not found" % name)
                else:
                    raise FastScoreError("Cannot retrieve '%s' schema" % name, caused_by=e)
            return Schema(name, source=source, model_manage=self.mm)

        def __setitem__(self, name, what):
            raise FastScoreError("Schema assignment not allowed (use update() method)")

        def __delitem__(self, name):
            try:
                self.mm.swg.schema_delete(self.mm.name, name)
            except Exception as e:
                if isinstance(e, ApiException) and e.status == 404:
                    raise FastScoreError("Schema '%s' not found" % name)
                else:
                    raise FastScoreError("Cannot remove schema '%s'" % name, caused_by=e)

    class StreamBag(object):
        def __init__(self, model_manage):
            self.mm = model_manage

        def names(self):
            try:
                return self.mm.swg.stream_list(self.mm.name)
            except Exception as e:
                raise FastScoreError("Cannot list streams", caused_by=e)

        def __iter__(self):
            for x in self.mm.swg.stream_list(self.mm.name):
                yield StreamMetadata(x)

        def __getitem__(self, name):
            try:
                desc = self.mm.swg.stream_get(self.mm.name, name)
            except Exception as e:
                if isinstance(e, ApiException) and e.status == 404:
                    raise FastScoreError("Stream '%s' not found" % name)
                else:
                    raise FastScoreError("Cannot retrieve '%s' stream" % name, caused_by=e)
            return Stream(name, desc, model_manage=self.mm)

        def __setitem__(self, name, what):
            raise FastScoreError("Stream assignment not allowed (use update() method")

        def __delitem__(self, name):
            try:
                self.mm.swg.stream_delete(self.mm.name, name)
            except Exception as e:
                if isinstance(e, ApiException) and e.status == 404:
                    raise FastScoreError("Stream '%s' not found" % name)
                else:
                    raise FastScoreError("Cannot remove stream '%s'" % name, caused_by=e)

    class SensorBag(object):
        def __init__(self, model_manage):
            self.mm = model_manage

        def names(self):
            try:
                return self.mm.swg.sensor_list(self.mm.name)
            except Exception as e:
                raise FastScoreError("Cannot list sensors", caused_by=e)

        def __iter__(self):
            try:
                for x in self.mm.swg.sensor_list(self.mm.name):
                    yield SensorMetadata(x)
            except Exception as e:
                raise FastScoreError("Cannot iterate sensors", caused_by=e)

        def __getitem__(self, name):
            try:
                desc = self.mm.swg.sensor_get(self.mm.name, name)
            except Exception as e:
                if isinstance(e, ApiException) and e.status == 404:
                    raise FastScoreError("Sensor '%s' not found" % name)
                else:
                    raise FastScoreError("Cannot retrieve '%s' sensor" % name, caused_by=e)
            return Sensor(name, desc=desc, model_manage=self.mm)

        def __setitem__(self, name, what):
            raise FastScoreError("Sensor assignment not allowed (use update() method")

        def __delitem__(self, name):
            try:
                self.mm.swg.sensor_delete(self.mm.name, name)
            except Exception as e:
                if isinstance(e, ApiException) and e.status == 404:
                    raise FastScoreError("Sensor '%s' not found" % name)
                else:
                    raise FastScoreError("Cannot remove sensor '%s'" % name, caused_by=e)

    def __init__(self, name):
        super(ModelManage, self).__init__(name, 'model-manage', \
                    ModelManageApi(), ModelManageApi2())
        self._models = ModelManage.ModelBag(self)
        self._schemata = ModelManage.SchemaBag(self)
        self._streams = ModelManage.StreamBag(self)
        self._sensors = ModelManage.SensorBag(self)

    @property
    def models(self):
        """
        A collection of :class:`.Model` objects indexed by model name.

        >>> mm.models.names()
        [u'model-1']
        >>> model = mm.models['model-1']
        >>> model.mtype
        'python'
        >>> del mm.models['model-1']
        >>> mm.models.names()
        []

        """
        return self._models

    @property
    def schemata(self):
        """
        A collection of :class:`.Schema` objects indexed schema name. The
        alternative name for the property is 'schemas'.

        >>> from fastscore import Schema
        >>> s = Schema('schema-1')
        >>> s.source = '{"type": "string"}'
        >>> s.update(mm)
        False   # Success; schema created, not updated
        >>> mm.schemata.names()
        ['schema-1']
        >>> del mm.schemata['schema-1']
        >>> mm.schemata.names()
        []

        """

        return self._schemata

    @property
    def schemas(self):
        return self._schemata

    @property
    def streams(self):
        """
        A collection of :class:`.Stream` objects indexed by stream name.

        >>> mm.streams.names()
        ['demo-1','demo-2]
        >>> mm.streams['demo-1'].desc
        {u'Description': u'A demo stream... }
        >>> del.strems['demo-2']
        >> mm.streams.names()
        ['demo-1']

        """

        return self._streams

    @property
    def sensors(self):
        """
        A collection of :class:`.Sensor` objects indexed by sensor name.

        >>> from fastscore import Sensor
        >>> s = Sensor('sensor-1')
        >>> s.desc = {'tap': 'manifold.input.records.size',... }
        >>> s.update(mm)
        False   # Success; sensor created, not updated
        >>> mm.sensors.names()
        ['sensor-1']
        >>> del mm.sensors['sensor-1']
        >>> mm.sensors.names()
        []

        """

        return self._sensors

    def save_model(self, model):
        if model.source == None:
            raise FastScoreError("Model source property not set")
        ct = MODEL_CONTENT_TYPES[model.mtype]
        try:
            (_,status,_) = self.swg.model_put_with_http_info(self.name,
                                    model.name, model.source, content_type=ct)
            return status == 204
        except Exception as e:
           raise FastScoreError("Cannot save model '%s'" % model.name, caused_by=e)

    def save_schema(self, schema):
        if schema.source == None:
            raise FastScoreError("Schema source property not set")
        try:
            (_,status,_) = self.swg.schema_put_with_http_info(self.name,
                                    schema.name, schema.source)
            return status == 204
        except Exception as e:
           raise FastScoreError("Cannot save schema '%s'" % schema.name, caused_by=e)

    def save_stream(self, stream):
        if stream.desc == None:
            raise FastScoreError("Stream descriptor property not set")
        try:
            (_,status,_) = self.swg.stream_put_with_http_info(self.name,
                                    stream.name, stream.desc)
            return status == 204
        except Exception as e:
           raise FastScoreError("Cannot save stream '%s'" % stream.name, caused_by=e)

    def save_sensor(self, sensor):
        if sensor.desc == None:
            raise FastScoreError("Sensor descriptor property not set")
        try:
            (_,status,_) = self.swg.sensor_put_with_http_info(self.name,
                                    sensor.name, sensor.desc)
            return status == 204
        except Exception as e:
           raise FastScoreError("Cannot save sensor '%s'" % model.name, caused_by=e)
