import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestGetPid:
    def test_get_pid_returns_integer(self):
        from execution_server import get_pid
        pid = get_pid()
        assert isinstance(pid, int)
        assert pid > 0


class TestGetStepIdx:
    def test_find_step_by_elem_id(self):
        from execution_server import get_step_idx
        elems = [
            {'elem_id': 'a', 'number': '1'},
            {'elem_id': 'b', 'number': '2'},
            {'elem_id': 'c', 'number': '3'},
        ]
        assert get_step_idx(elems, 'b') == 1

    def test_find_first_step_with_empty_id(self):
        from execution_server import get_step_idx
        elems = [
            {'elem_id': 'a', 'number': '1'},
            {'elem_id': 'b', 'number': '2'},
        ]
        assert get_step_idx(elems, '') == 0

    def test_returns_negative_one_for_missing(self):
        from execution_server import get_step_idx
        elems = [
            {'elem_id': 'a', 'number': '1'},
            {'elem_id': 'b', 'number': '2'},
        ]
        assert get_step_idx(elems, 'z') == -1

    def test_empty_list_returns_negative_one(self):
        from execution_server import get_step_idx
        assert get_step_idx([], 'a') == -1


class TestRequiresManualInput:
    def test_manual_step_type(self):
        from execution_server import requires_manual_input
        elem = {'elem_type': 'STEP', 'step_type': 'MANUAL_INPUT'}
        assert requires_manual_input(elem) is True

    def test_non_manual_step(self):
        from execution_server import requires_manual_input
        elem = {'elem_type': 'STEP', 'step_type': 'CMD_FSW'}
        assert requires_manual_input(elem) is False

    def test_custom_script_with_execution_inputs(self):
        from execution_server import requires_manual_input
        elem = {
            'elem_type': 'STEP',
            'step_type': 'CUSTOM_SCRIPT',
            'execution_user_input': {
                'inputs': [{'phase': 'EXECUTION'}]
            },
        }
        assert requires_manual_input(elem) is True

    def test_custom_script_without_execution_inputs(self):
        from execution_server import requires_manual_input
        elem = {
            'elem_type': 'STEP',
            'step_type': 'CUSTOM_SCRIPT',
            'execution_user_input': {
                'inputs': [{'phase': 'PLANNING'}]
            },
        }
        assert requires_manual_input(elem) is False

    def test_custom_script_with_entry_inputs(self):
        from execution_server import requires_manual_input
        elem = {
            'elem_type': 'STEP',
            'step_type': 'CUSTOM_SCRIPT',
            'execution_user_input': {
                'entries': [{
                    'entry_inputs': [{'phase': 'EXECUTION'}]
                }]
            },
        }
        assert requires_manual_input(elem) is True

    def test_none_element_returns_false(self):
        from execution_server import requires_manual_input
        assert requires_manual_input(None) is False

    def test_non_step_type_returns_false(self):
        from execution_server import requires_manual_input
        elem = {'elem_type': 'SECTION', 'step_type': 'MANUAL_INPUT'}
        assert requires_manual_input(elem) is False


class TestIsCommandStep:
    def test_cmd_fsw_step(self):
        from execution_server import is_command_step
        elem = {'elem_type': 'STEP', 'step_type': 'CMD_FSW'}
        assert is_command_step(elem) is True

    def test_cmd_hw_step(self):
        from execution_server import is_command_step
        elem = {'elem_type': 'STEP', 'step_type': 'CMD_HW'}
        assert is_command_step(elem) is True

    def test_custom_script_step(self):
        from execution_server import is_command_step
        elem = {'elem_type': 'STEP', 'step_type': 'CUSTOM_SCRIPT'}
        assert is_command_step(elem) is True

    def test_non_command_step(self):
        from execution_server import is_command_step
        elem = {'elem_type': 'STEP', 'step_type': 'VERIFY_EHA'}
        assert is_command_step(elem) is False

    def test_none_element_returns_false(self):
        from execution_server import is_command_step
        assert is_command_step(None) is False

    def test_non_step_type_returns_false(self):
        from execution_server import is_command_step
        elem = {'elem_type': 'SECTION', 'step_type': 'CMD_FSW'}
        assert is_command_step(elem) is False


class TestStopExecutionWithError:
    @patch('execution_server.post_execution_message')
    @patch('execution_server.update_execution')
    def test_calls_post_message_and_update(self, mock_update, mock_post):
        from execution_server import stop_execution_with_error
        stop_execution_with_error('exec-1', 'something broke')

        mock_post.assert_called_once_with('exec-1', 'ERROR', 'something broke')
        mock_update.assert_called_once_with('exec-1', {'status': 'IDLE'})


class TestNeedsApproval:
    def test_step_modifying_no_approval(self):
        from execution_server import needs_approval
        elem = {
            'elem_type': 'STEP',
            'procedure_modification_status': 'MODIFYING',
            'procedure_modification': None,
        }
        assert needs_approval(elem) is True

    def test_step_approved(self):
        from execution_server import needs_approval
        elem = {
            'elem_type': 'STEP',
            'procedure_modification_status': 'ADDED',
            'procedure_modification': {'approval': {'status': 'APPROVED'}},
        }
        assert needs_approval(elem) is False

    def test_step_pending_approval(self):
        from execution_server import needs_approval
        elem = {
            'elem_type': 'STEP',
            'procedure_modification_status': 'DELETED',
            'procedure_modification': {'approval': {'status': 'PENDING'}},
        }
        assert needs_approval(elem) is True

    def test_step_no_modification_status(self):
        from execution_server import needs_approval
        elem = {
            'elem_type': 'STEP',
            'procedure_modification_status': None,
        }
        assert needs_approval(elem) is False

    def test_section_type_returns_false(self):
        from execution_server import needs_approval
        elem = {
            'elem_type': 'SECTION',
            'procedure_modification_status': 'MODIFYING',
        }
        assert needs_approval(elem) is False

    def test_procedure_section_modifying(self):
        from execution_server import needs_approval
        elem = {
            'elem_type': 'PROCEDURE_SECTION',
            'procedure_modification_status': 'MODIFYING',
            'procedure_modification': None,
        }
        assert needs_approval(elem) is True
