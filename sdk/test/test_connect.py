from . import config

from fastscore.suite import Connect

from fastscore.suite.instance import ActiveSensorInfo

from fastscore import FastScoreError

from unittest import TestCase
from mock import patch

from os.path import exists
from os import remove

class ConnectTests(TestCase):

    class ServiceInfo(object):
        def __init__(self, name, health='ok'):
            self.api = 'model-manage'
            self.name = name
            self.health = health

    def setUp(self):
        self.connect = Connect(config.dashboard)

    @patch('fastscore.suite.connect.ConnectApi.health_get')
    def test_check_health(self, health_get):
        self.connect.check_health()
        health_get.assert_called_once_with('connect')

    @patch('fastscore.suite.connect.ConnectApi.swagger_get')
    def test_get_swagger(self, swagger_get):
        self.connect.get_swagger()
        swagger_get.assert_called_once_with('connect')

    def test_connect(self):
        self.assertRaises(FastScoreError, lambda : Connect('foobar'))
        self.assertRaises(FastScoreError, lambda : Connect('http://fake-host:8000'))

    @patch('fastscore.suite.connect.ConnectApi.config_put_with_http_info',
                return_value=(None,204,None))
    def test_configure(self, config_put):
        self.assertRaises(FastScoreError, lambda : self.connect.configure('fastscore:\n'))
        self.assertRaises(FastScoreError, lambda : self.connect.configure([]))
        self.connect.configure({'fastscore': []})
        self.assertTrue(config_put.called)

    @patch('fastscore.suite.connect.ConnectApi.config_get',
                return_value='fastscore:\n')
    def test_get_config(self, config_get):
        self.assertRaises(FastScoreError, lambda : self.connect.get_config(3.14))
        self.connect.get_config()
        config_get.assert_called_with('connect', accept='application/x-yaml')
        self.connect.get_config('db')
        config_get.assert_called_with('connect', q='db', accept='application/x-yaml')

    def test_save(self):
        savefile = '/tmp/__fastscore_test__'
        if exists(savefile):
            remove(savefile)
        self.assertRaises(FastScoreError, lambda : self.connect.dump('/'))
        self.connect.dump(savefile)
        self.assertTrue(exists(savefile))
        Connect.load(savefile)

    @patch('fastscore.suite.connect.ConnectApi.connect_get')
    def test_get(self, connect_get):
        connect_get.return_value = []
        self.assertRaises(FastScoreError, lambda : self.connect.get('model-manage'))
        connect_get.return_value = [ConnectTests.ServiceInfo('mm-1', health='fail')]
        self.assertRaises(FastScoreError, lambda : self.connect.get('model-manage'))
        connect_get.return_value = [ConnectTests.ServiceInfo('mm-1')]
        mm = self.connect.get('model-manage')

    @patch('fastscore.suite.connect.ConnectApi.connect_get',
                return_value=[ServiceInfo('mm-1')])
    def test_cache(self, connect_get):
        mm1 = self.connect.get('mm-1')
        mm2 = self.connect.get('mm-1')
        self.assertEqual(mm1, mm2)
        connect_get.assert_called_once_with('connect', name='mm-1')

    @patch('fastscore.suite.connect.ConnectApi.connect_get',
                return_value=[ServiceInfo('mm-1'),
                              ServiceInfo('mm-2'),
                              ServiceInfo('mm-3')])
    def test_lookup(self, connect_get):
        mm = self.connect.lookup('model-manage')
        self.assertEqual('mm-1', mm.name)
        self.connect.prefer('model-manage', 'mm-2')
        mm = self.connect.lookup('model-manage')
        self.assertEqual('mm-2', mm.name)
        self.connect.target = self.connect.get('mm-3')
        mm = self.connect.lookup('model-manage')
        self.assertEqual('mm-3', mm.name)

    @patch('fastscore.suite.connect.ConnectApi.connect_get',
                return_value=[ServiceInfo('mm-1')])
    def test_fleet(self, connect_get):
        self.connect.fleet()
        connect_get.assert_called_once_with('connect')

    @patch('fastscore.suite.connect.ConnectApi2.active_sensor_list')
    def test_active_sensors(self, sensor_list):
        self.connect.active_sensors.ids()
        sensor_list.assert_called_once_with('connect')

    @patch('fastscore.suite.connect.ConnectApi2.active_sensor_list',
            return_value=[ActiveSensorInfo(1, 'dummy')])
    def test_active_sensors(self, sensor_list):
        for x in self.connect.active_sensors.values():
            self.assertIsInstance(x, ActiveSensorInfo)
        sensor_list.assert_called_once_with('connect')

    @patch('fastscore.suite.connect.ConnectApi2.active_sensor_points')
    def test_tapping_points(self, sensor_available):
        self.connect.tapping_points()
        sensor_available.assert_called_once_with('connect')

    #NB: connect.pneumo() not tested
