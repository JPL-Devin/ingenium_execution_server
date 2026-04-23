import os
import sys
import time
import pytest
import jwt as pyjwt
from unittest.mock import patch, MagicMock

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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


def _make_token(private_pem=_private_pem, expired=False):
    now = int(time.time())
    payload = {
        'username': 'test_user',
        'scopes': [{'scope': 'execute:wsts'}],
        'iat': now - (7200 if expired else 0),
        'exp': now + (-3600 if expired else 3600),
    }
    return pyjwt.encode(payload, private_pem, algorithm='RS256')


class TestDecodeIngeniumToken:
    @patch.dict(os.environ, {'PUBLIC_PEM': _public_pem.decode('utf-8')})
    def test_decode_valid_token(self):
        import ingenium_embedded.ingenium_config as ic
        ic.ing_token = _make_token()

        from ingenium_embedded.ingenium_library import decode_ingenium_token
        decoded = decode_ingenium_token(verify=True)

        assert decoded['username'] == 'test_user'
        assert 'scopes' in decoded

    @patch.dict(os.environ, {'PUBLIC_PEM': _public_pem.decode('utf-8')})
    def test_decode_invalid_token_raises(self):
        import ingenium_embedded.ingenium_config as ic
        ic.ing_token = 'invalid.token.string'

        from ingenium_embedded.ingenium_library import decode_ingenium_token
        with pytest.raises(Exception):
            decode_ingenium_token(verify=True)

    @patch.dict(os.environ, {'PUBLIC_PEM': _public_pem.decode('utf-8')})
    def test_decode_expired_token_raises(self):
        import ingenium_embedded.ingenium_config as ic
        ic.ing_token = _make_token(expired=True)

        from ingenium_embedded.ingenium_library import decode_ingenium_token
        with pytest.raises(pyjwt.ExpiredSignatureError):
            decode_ingenium_token(verify=True)

    @patch.dict(os.environ, {'PUBLIC_PEM': _public_pem.decode('utf-8')})
    def test_decode_expired_token_no_verify(self):
        import ingenium_embedded.ingenium_config as ic
        ic.ing_token = _make_token(expired=True)

        from ingenium_embedded.ingenium_library import decode_ingenium_token
        decoded = decode_ingenium_token(verify=False)
        assert decoded['username'] == 'test_user'


class TestDecodeVenueToken:
    @patch.dict(os.environ, {'EXEC_VENUE_PUBLIC_PEM': _public_pem.decode('utf-8')})
    def test_decode_valid_venue_token(self):
        import ingenium_embedded.ingenium_config as ic
        ic.venue_token = _make_token()

        from ingenium_embedded.ingenium_library import decode_venue_token
        decoded = decode_venue_token(verify=True)

        assert decoded['username'] == 'test_user'

    @patch.dict(os.environ, {'EXEC_VENUE_PUBLIC_PEM': _public_pem.decode('utf-8')})
    def test_decode_invalid_venue_token_raises(self):
        import ingenium_embedded.ingenium_config as ic
        ic.venue_token = 'bad.token.here'

        from ingenium_embedded.ingenium_library import decode_venue_token
        with pytest.raises(Exception):
            decode_venue_token(verify=True)

    @patch.dict(os.environ, {'EXEC_VENUE_PUBLIC_PEM': _public_pem.decode('utf-8')})
    def test_decode_venue_token_verify_false(self):
        import ingenium_embedded.ingenium_config as ic
        ic.venue_token = _make_token(expired=True)

        from ingenium_embedded.ingenium_library import decode_venue_token
        decoded = decode_venue_token(verify=False)
        assert decoded['username'] == 'test_user'

    def test_decode_venue_token_wrong_key_raises(self):
        other_private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        other_pem = other_private.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
        )
        token = _make_token(private_pem=other_pem)

        import ingenium_embedded.ingenium_config as ic
        ic.venue_token = token

        with patch.dict(os.environ, {'EXEC_VENUE_PUBLIC_PEM': _public_pem.decode('utf-8')}):
            from ingenium_embedded.ingenium_library import decode_venue_token
            with pytest.raises(pyjwt.InvalidSignatureError):
                decode_venue_token(verify=True)
