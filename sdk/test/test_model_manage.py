from . import config

from fastscore.suite import Connect
from fastscore import Model
from fastscore.model import ModelMetadata
from fastscore import Stream
from fastscore.stream import StreamMetadata
from fastscore import Schema
from fastscore.schema import SchemaMetadata
from fastscore import Sensor
from fastscore.sensor import SensorMetadata

from fastscore.suite.instance import ActiveSensorInfo

from fastscore import FastScoreError

from unittest import TestCase
from mock import patch

class ModelManageTests(TestCase):

    class ServiceInfo(object):
        def __init__(self, name):
            self.api = 'model-manage'
            self.name = name
            self.health = 'ok'

    @patch('fastscore.suite.connect.ConnectApi.connect_get',
                return_value=[ServiceInfo('mm-1')])
    def setUp(self, connect_get):
        self.connect = Connect('https://dashboard:1234')
        self.mm = self.connect.get('mm-1')

    @patch('fastscore.suite.model_manage.ModelManageApi.health_get')
    def test_check_health(self, health_get):
        self.mm.check_health()
        health_get.assert_called_once_with('mm-1')

    @patch('fastscore.suite.model_manage.ModelManageApi.swagger_get')
    def test_get_swagger(self, swagger_get):
        self.mm.get_swagger()
        swagger_get.assert_called_once_with('mm-1')

    @patch('fastscore.suite.model_manage.ModelManageApi2.active_sensor_list')
    def test_active_sensors(self, sensor_list):
        self.mm.active_sensors.ids()
        sensor_list.assert_called_once_with('mm-1')

    @patch('fastscore.suite.model_manage.ModelManageApi2.active_sensor_list',
                return_value=[ActiveSensorInfo(1, 'dummy')])
    def test_active_sensors(self, sensor_list):
        for x in self.mm.active_sensors.values():
            self.assertIsInstance(x, ActiveSensorInfo)
        sensor_list.assert_called_once_with('mm-1')

    @patch('fastscore.suite.model_manage.ModelManageApi2.active_sensor_points')
    def test_tapping_points(self, sensor_available):
        self.mm.tapping_points()
        sensor_available.assert_called_once_with('mm-1')

    ##-- models ----------------------------------------------------------------

    @patch('fastscore.suite.model_manage.ModelManageApi.model_list')
    def test_model_names(self, model_list):
        self.mm.models.names()
        model_list.assert_called_once_with('mm-1')

    @patch('fastscore.suite.model_manage.ModelManageApi.model_list',
                return_value=[{'name':'m1', 'type':'python'}])
    def test_iter_models(self, model_list):
        for x in self.mm.models:
            self.assertIsInstance(x, ModelMetadata)
        model_list.assert_called_once_with('mm-1', _return='type')

    @patch('fastscore.suite.model_manage.ModelManageApi.model_get_with_http_info',
                return_value=('foo',200,{'content-type':'application/vnd.fastscore.model-python'}))
    def test_get_model(self, model_get):
        model = self.mm.models['m1']
        self.assertIsInstance(model, Model)
        model_get.assert_called_once_with('mm-1', 'm1')

    @patch('fastscore.suite.model_manage.ModelManageApi.model_delete')
    def test_remove_model(self, model_delete):
        del self.mm.models['m1']
        model_delete.assert_called_once_with('mm-1', 'm1')

    def test_assign_model(self):
        def set_model():
            self.mm.models['m1'] = None
        self.assertRaises(FastScoreError, set_model)

    ##-- streams ---------------------------------------------------------------

    @patch('fastscore.suite.model_manage.ModelManageApi.stream_list')
    def test_stream_names(self, stream_list):
        self.mm.streams.names()
        stream_list.assert_called_once_with('mm-1')

    @patch('fastscore.suite.model_manage.ModelManageApi.stream_list',
                return_value=['s1'])
    def test_iter_streams(self, stream_list):
        for x in self.mm.streams:
            self.assertIsInstance(x, StreamMetadata)
        stream_list.assert_called_once_with('mm-1')

    @patch('fastscore.suite.model_manage.ModelManageApi.stream_get')
    def test_get_stream(self, stream_get):
        stream = self.mm.streams['s1']
        self.assertIsInstance(stream, Stream)
        stream_get.assert_called_once_with('mm-1', 's1')

    @patch('fastscore.suite.model_manage.ModelManageApi.stream_delete')
    def test_remove_stream(self, stream_delete):
        del self.mm.streams['s1']
        stream_delete.assert_called_once_with('mm-1', 's1')

    def test_assign_stream(self):
        def set_stream():
            self.mm.streams['s1'] = None
        self.assertRaises(FastScoreError, set_stream)

    ##-- schemas ---------------------------------------------------------------

    @patch('fastscore.suite.model_manage.ModelManageApi.schema_list')
    def test_schema_names(self, schema_list):
        self.mm.schemas.names()
        schema_list.assert_called_once_with('mm-1')

    @patch('fastscore.suite.model_manage.ModelManageApi.schema_list',
                return_value=['s1'])
    def test_iter_schemas(self, schema_list):
        for x in self.mm.schemas:
            self.assertIsInstance(x, SchemaMetadata)
        schema_list.assert_called_once_with('mm-1')

    @patch('fastscore.suite.model_manage.ModelManageApi.schema_get')
    def test_get_schema(self, schema_get):
        schema = self.mm.schemas['s1']
        self.assertIsInstance(schema, Schema)
        schema_get.assert_called_once_with('mm-1', 's1')

    @patch('fastscore.suite.model_manage.ModelManageApi.schema_delete')
    def test_remove_schema(self, schema_delete):
        del self.mm.schemas['s1']
        schema_delete.assert_called_once_with('mm-1', 's1')

    def test_assign_schema(self):
        def set_schema():
            self.mm.schemas['s1'] = None
        self.assertRaises(FastScoreError, set_schema)

    ##-- sensors ---------------------------------------------------------------

    @patch('fastscore.suite.model_manage.ModelManageApi.sensor_list')
    def test_sensor_names(self, sensor_list):
        self.mm.sensors.names()
        sensor_list.assert_called_once_with('mm-1')

    @patch('fastscore.suite.model_manage.ModelManageApi.sensor_list',
                return_value=['s1'])
    def test_iter_sensors(self, sensor_list):
        for x in self.mm.sensors:
            self.assertIsInstance(x, SensorMetadata)
        sensor_list.assert_called_once_with('mm-1')

    @patch('fastscore.suite.model_manage.ModelManageApi.sensor_get')
    def test_get_sensor(self, sensor_get):
        sensor = self.mm.sensors['s1']
        self.assertIsInstance(sensor, Sensor)
        sensor_get.assert_called_once_with('mm-1', 's1')

    @patch('fastscore.suite.model_manage.ModelManageApi.sensor_delete')
    def test_remove_sensor(self, sensor_delete):
        del self.mm.sensors['s1']
        sensor_delete.assert_called_once_with('mm-1', 's1')

    def test_assign_sensor(self):
        def set_sensor():
            self.mm.sensors['s1'] = None
        self.assertRaises(FastScoreError, set_sensor)
