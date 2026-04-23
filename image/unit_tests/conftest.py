import os
import sys
import pytest
import json
import time
import jwt
from unittest.mock import MagicMock, patch
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Add image directory to path so modules can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope='session')
def rsa_key_pair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return {
        'private_key': private_key,
        'public_key': public_key,
        'private_pem': private_pem,
        'public_pem': public_pem,
    }


@pytest.fixture
def valid_jwt_payload():
    now = int(time.time())
    return {
        'username': 'test_user',
        'scopes': [
            {'scope': 'execute:wsts'},
            {'scope': 'execute:testbed'},
            {'scope': 'admin'},
        ],
        'iat': now,
        'exp': now + 3600,
    }


@pytest.fixture
def valid_jwt_token(rsa_key_pair, valid_jwt_payload):
    return jwt.encode(
        valid_jwt_payload,
        rsa_key_pair['private_pem'],
        algorithm='RS256',
    )


@pytest.fixture
def expired_jwt_token(rsa_key_pair):
    now = int(time.time())
    payload = {
        'username': 'test_user',
        'scopes': [{'scope': 'execute:wsts'}],
        'iat': now - 7200,
        'exp': now - 3600,
    }
    return jwt.encode(payload, rsa_key_pair['private_pem'], algorithm='RS256')


@pytest.fixture
def mock_redis():
    mock = MagicMock()
    mock.hset = MagicMock()
    mock.hget = MagicMock(return_value=None)
    mock.hmget = MagicMock(return_value=[])
    mock.delete = MagicMock()
    mock.get = MagicMock(return_value=None)
    mock.set = MagicMock()
    return mock


@pytest.fixture
def env_vars(rsa_key_pair):
    env = {
        'PUBLIC_PEM': rsa_key_pair['public_pem'].decode('utf-8'),
        'EXEC_VENUE_PUBLIC_PEM': rsa_key_pair['public_pem'].decode('utf-8'),
        'EXEC_VENUE_PRIVATE_PEM': rsa_key_pair['private_pem'].decode('utf-8'),
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': '6379',
    }
    return env
