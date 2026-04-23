import json
import os
import sys
import time
import pytest
import jwt
from unittest.mock import patch, MagicMock

import tornado.web
import tornado.testing

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generate keys at module level for use in tests
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


def _make_token(payload=None):
    now = int(time.time())
    if payload is None:
        payload = {
            'username': 'test_user',
            'scopes': [{'scope': 'execute:wsts'}, {'scope': 'admin'}],
            'iat': now,
            'exp': now + 3600,
        }
    return jwt.encode(payload, _private_pem, algorithm='RS256')


def _make_expired_token():
    now = int(time.time())
    payload = {
        'username': 'test_user',
        'scopes': [{'scope': 'execute:wsts'}],
        'iat': now - 7200,
        'exp': now - 3600,
    }
    return jwt.encode(payload, _private_pem, algorithm='RS256')


def _make_app():
    with patch('execution_server.ProcessPoolExecutor') as mock_ppe, \
         patch('execution_server.StateManager'), \
         patch('execution_server.ingenium_library'), \
         patch.dict(os.environ, {'REDIS_HOST': 'localhost', 'REDIS_PORT': '6379'}):

        mock_pool = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 12345
        mock_pool.submit.return_value = mock_future
        mock_ppe.return_value = mock_pool

        import execution_server
        execution_server.public_pem = _public_pem.decode('utf-8')

        from execution_server import HealthHandler, LoggingHandler

        app = tornado.web.Application([
            (r'/api/v4/health', HealthHandler),
            (r'/api/v4/logging', LoggingHandler),
        ])
        return app


class TestExecApiDecoratorNoAuth(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return _make_app()

    def test_no_auth_required_passes(self):
        response = self.fetch('/api/v4/health')
        self.assertEqual(response.code, 200)


class TestExecApiDecoratorMissingHeader(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return _make_app()

    def test_missing_auth_header_returns_401(self):
        response = self.fetch('/api/v4/logging')
        self.assertEqual(response.code, 401)
        body = json.loads(response.body)
        self.assertIn('Authorization header was not provided', body['message'])


class TestExecApiDecoratorInvalidJWT(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return _make_app()

    def test_invalid_bearer_prefix_returns_401(self):
        response = self.fetch(
            '/api/v4/logging',
            headers={'Authorization': 'Basic invalid_token'}
        )
        self.assertEqual(response.code, 401)

    def test_missing_token_value_returns_401(self):
        response = self.fetch(
            '/api/v4/logging',
            headers={'Authorization': 'Bearer'}
        )
        self.assertEqual(response.code, 401)

    def test_too_many_parts_returns_401(self):
        response = self.fetch(
            '/api/v4/logging',
            headers={'Authorization': 'Bearer token extra'}
        )
        self.assertEqual(response.code, 401)

    def test_invalid_jwt_string_returns_401(self):
        response = self.fetch(
            '/api/v4/logging',
            headers={'Authorization': 'Bearer not.a.valid.jwt'}
        )
        self.assertEqual(response.code, 401)


class TestExecApiDecoratorExpiredJWT(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return _make_app()

    def test_expired_jwt_returns_401(self):
        token = _make_expired_token()
        response = self.fetch(
            '/api/v4/logging',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.code, 401)


class TestExecApiDecoratorValidJWT(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return _make_app()

    def test_valid_jwt_passes_through(self):
        token = _make_token()
        response = self.fetch(
            '/api/v4/logging',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertIn('level', body)

    def test_insufficient_scopes_returns_401(self):
        now = int(time.time())
        payload = {
            'username': 'test_user',
            'scopes': [{'scope': 'read:only'}],
            'iat': now,
            'exp': now + 3600,
        }
        token = _make_token(payload)
        response = self.fetch(
            '/api/v4/logging',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.code, 401)
        body = json.loads(response.body)
        self.assertIn('scope requirement', body['message'])
