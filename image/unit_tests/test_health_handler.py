import json
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

import tornado.web
import tornado.testing

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def _make_app():
    with patch('execution_server.ProcessPoolExecutor') as mock_ppe, \
         patch('execution_server.StateManager') as mock_sm, \
         patch('execution_server.ingenium_library'), \
         patch.dict(os.environ, {'REDIS_HOST': 'localhost', 'REDIS_PORT': '6379'}):

        mock_pool = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 12345
        mock_pool.submit.return_value = mock_future
        mock_ppe.return_value = mock_pool

        from configparser import ConfigParser
        config = ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), '..', 'config.ini'))

        from execution_server import HealthHandler, RequestLogHandler

        app = tornado.web.Application([
            (r'/api/v4/health', HealthHandler),
        ])
        return app


class TestHealthHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return _make_app()

    def test_health_returns_200(self):
        response = self.fetch('/api/v4/health')
        self.assertEqual(response.code, 200)

    def test_health_returns_ok_status(self):
        response = self.fetch('/api/v4/health')
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'OK')

    def test_health_response_has_message_field(self):
        response = self.fetch('/api/v4/health')
        body = json.loads(response.body)
        self.assertIn('message', body)
