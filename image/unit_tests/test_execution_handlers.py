import json
import os
import sys
import time
import logging
import pytest
import jwt
from unittest.mock import patch, MagicMock

import tornado.web
import tornado.testing

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_public_key = _private_key.public_key()
_private_pem = _private_key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption()
)
_public_pem = _public_key.public_bytes(
    serialization.Encoding.PEM,
    serialization.PublicFormat.SubjectPublicKeyInfo
)


def _make_token(scopes=None):
    now = int(time.time())
    if scopes is None:
        scopes = [{'scope': 'execute:wsts'}, {'scope': 'admin'}]
    payload = {
        'username': 'test_user',
        'scopes': scopes,
        'iat': now,
        'exp': now + 3600,
    }
    return jwt.encode(payload, _private_pem, algorithm='RS256')


def _make_app():
    with patch('execution_server.ProcessPoolExecutor') as mock_ppe, \
         patch('execution_server.StateManager') as mock_sm_cls, \
         patch('execution_server.ingenium_library'), \
         patch.dict(os.environ, {'REDIS_HOST': 'localhost', 'REDIS_PORT': '6379'}):

        mock_pool = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 12345
        mock_pool.submit.return_value = mock_future
        mock_ppe.return_value = mock_pool

        mock_sm = MagicMock()
        mock_sm.set_config_value = MagicMock()
        mock_sm.get_config_value = MagicMock(return_value="'test_value'")
        mock_sm.get_variable_value = MagicMock(return_value='hello')
        mock_sm.delete_execution = MagicMock()
        mock_sm_cls.return_value = mock_sm

        import execution_server
        execution_server.public_pem = _public_pem.decode('utf-8')

        from execution_server import (
            ExecutionHandler, ConfigHandler, VariableHandler,
            LoggingHandler, HealthHandler
        )

        app = tornado.web.Application([
            (r'/api/v4/executions/([0-9a-zA-Z\-]+)', ExecutionHandler),
            (r'/api/v4/executions/([0-9a-zA-Z\-]+)/config_value', ConfigHandler),
            (r'/api/v4/executions/([0-9a-zA-Z\-]+)/variable_value', VariableHandler),
            (r'/api/v4/logging', LoggingHandler),
            (r'/api/v4/health', HealthHandler),
        ])
        app.state_manager = mock_sm
        return app


class TestExecutionHandlerPut(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return _make_app()

    def test_put_registers_execution(self):
        token = _make_token()
        venue_info = {
            'ampcs_address': 'http://venue:8080',
            'sse_address': 'http://sse:8080',
            'name': 'WSTS',
            'venue_id': 'v-1',
            'type': 'wsts',
        }
        response = self.fetch(
            '/api/v4/executions/exec-123',
            method='PUT',
            body=json.dumps(venue_info),
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            },
        )
        self.assertEqual(response.code, 204)

    def test_put_without_auth_returns_401(self):
        response = self.fetch(
            '/api/v4/executions/exec-123',
            method='PUT',
            body=json.dumps({'name': 'test'}),
            headers={'Content-Type': 'application/json'},
        )
        self.assertEqual(response.code, 401)


class TestExecutionHandlerDelete(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return _make_app()

    def test_delete_unregisters_execution(self):
        token = _make_token()
        response = self.fetch(
            '/api/v4/executions/exec-123',
            method='DELETE',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(response.code, 204)

    def test_delete_without_auth_returns_401(self):
        response = self.fetch(
            '/api/v4/executions/exec-123',
            method='DELETE',
        )
        self.assertEqual(response.code, 401)


class TestLoggingHandlerGet(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return _make_app()

    def test_get_returns_current_log_level(self):
        token = _make_token()
        response = self.fetch(
            '/api/v4/logging',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertIn('level', body)


class TestLoggingHandlerPost(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return _make_app()

    def test_post_sets_log_level(self):
        token = _make_token()
        response = self.fetch(
            '/api/v4/logging',
            method='POST',
            body=json.dumps({'level': 'WARNING'}),
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            },
        )
        self.assertEqual(response.code, 204)

    def test_post_invalid_format_returns_400(self):
        token = _make_token()
        response = self.fetch(
            '/api/v4/logging',
            method='POST',
            body=json.dumps({'not_level': 'DEBUG'}),
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            },
        )
        self.assertEqual(response.code, 400)


class TestConfigHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return _make_app()

    def test_get_config_returns_value(self):
        token = _make_token()
        response = self.fetch(
            '/api/v4/executions/exec-123/config_value?parameter_name=venue_name',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['name'], 'venue_name')
        self.assertEqual(body['value'], 'test_value')

    def test_get_config_missing_param_returns_400(self):
        token = _make_token()
        response = self.fetch(
            '/api/v4/executions/exec-123/config_value',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(response.code, 400)


class TestVariableHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return _make_app()

    def test_get_variable_returns_value(self):
        token = _make_token()
        response = self.fetch(
            '/api/v4/executions/exec-123/variable_value?variable_name=my_var',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['name'], 'my_var')
        self.assertEqual(body['value'], 'hello')

    def test_get_variable_missing_name_returns_400(self):
        token = _make_token()
        response = self.fetch(
            '/api/v4/executions/exec-123/variable_value',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(response.code, 400)
