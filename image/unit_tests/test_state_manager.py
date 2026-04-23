import json
import pytest
from unittest.mock import MagicMock, patch

from state_manager import StateManager


class TestStateManagerHashTemplate:
    def test_hash_template_format(self):
        from state_manager import StateManager
        assert StateManager.HASH_TEMPLATE == 'execution_id:{}'
        assert StateManager.HASH_TEMPLATE.format('abc-123') == 'execution_id:abc-123'


class TestStateManagerSetConfigValue:
    @patch('state_manager.redis.StrictRedis')
    def test_set_config_value_stores_data(self, mock_redis_cls):
        mock_client = MagicMock()
        mock_redis_cls.return_value = mock_client

        sm = StateManager('localhost', 6379)
        sm.set_config_value('exec-1', 'venue_name', 'WSTS')

        mock_client.hset.assert_called_once_with('execution_id:exec-1', 'venue_name', 'WSTS')

    @patch('state_manager.redis.StrictRedis')
    def test_set_config_value_multiple_keys(self, mock_redis_cls):
        mock_client = MagicMock()
        mock_redis_cls.return_value = mock_client

        sm = StateManager('localhost', 6379)
        sm.set_config_value('exec-1', 'key1', 'val1')
        sm.set_config_value('exec-1', 'key2', 'val2')

        assert mock_client.hset.call_count == 2


class TestStateManagerGetConfigValue:
    @patch('state_manager.redis.StrictRedis')
    def test_get_config_value_returns_string(self, mock_redis_cls):
        mock_client = MagicMock()
        mock_client.hget.return_value = 'WSTS'
        mock_redis_cls.return_value = mock_client

        sm = StateManager('localhost', 6379)
        result = sm.get_config_value('exec-1', 'venue_name')

        assert result == 'WSTS'
        mock_client.hget.assert_called_once_with('execution_id:exec-1', 'venue_name')

    @patch('state_manager.redis.StrictRedis')
    def test_get_config_value_returns_none_for_missing(self, mock_redis_cls):
        mock_client = MagicMock()
        mock_client.hget.return_value = None
        mock_redis_cls.return_value = mock_client

        sm = StateManager('localhost', 6379)
        result = sm.get_config_value('exec-1', 'nonexistent')

        assert result is None


class TestStateManagerGetVariableValue:
    @patch('state_manager.redis.StrictRedis')
    def test_get_variable_value_returns_correct_variable(self, mock_redis_cls):
        mock_client = MagicMock()
        variables = {'my_var': 42, 'other_var': 'hello'}
        mock_client.hget.return_value = json.dumps(variables)
        mock_redis_cls.return_value = mock_client

        sm = StateManager('localhost', 6379)
        result = sm.get_variable_value('exec-1', 'my_var')

        assert result == 42
        mock_client.hget.assert_called_once_with(
            'execution_id:exec-1', 'manual_input_variables'
        )

    @patch('state_manager.redis.StrictRedis')
    def test_get_variable_value_returns_none_for_missing_hash(self, mock_redis_cls):
        mock_client = MagicMock()
        mock_client.hget.return_value = None
        mock_redis_cls.return_value = mock_client

        sm = StateManager('localhost', 6379)
        result = sm.get_variable_value('exec-1', 'my_var')

        assert result is None

    @patch('state_manager.redis.StrictRedis')
    def test_get_variable_value_returns_none_for_missing_variable(self, mock_redis_cls):
        mock_client = MagicMock()
        variables = {'other_var': 'hello'}
        mock_client.hget.return_value = json.dumps(variables)
        mock_redis_cls.return_value = mock_client

        sm = StateManager('localhost', 6379)
        result = sm.get_variable_value('exec-1', 'nonexistent')

        assert result is None


class TestStateManagerDeleteExecution:
    @patch('state_manager.redis.StrictRedis')
    def test_delete_execution_deletes_hash(self, mock_redis_cls):
        mock_client = MagicMock()
        mock_redis_cls.return_value = mock_client

        sm = StateManager('localhost', 6379)
        sm.delete_execution('exec-1')

        mock_client.delete.assert_called_once_with('execution_id:exec-1')
