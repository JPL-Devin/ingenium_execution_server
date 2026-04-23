import os
import sys
import pytest
from unittest.mock import patch, MagicMock, PropertyMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestWorkerProcessInit:
    @patch('execution_server.ProcessPoolExecutor')
    def test_worker_process_init(self, mock_ppe):
        mock_pool = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 9999
        mock_pool.submit.return_value = mock_future
        mock_ppe.return_value = mock_pool

        from execution_server import WorkerProcess
        wp = WorkerProcess('worker-0')

        assert wp.name == 'worker-0'
        assert wp.pid == 9999
        assert wp.execution_id is None
        assert wp.run_mode is None
        assert wp.future is None

    @patch('execution_server.ProcessPoolExecutor')
    def test_worker_process_is_idle_initially(self, mock_ppe):
        mock_pool = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 1234
        mock_pool.submit.return_value = mock_future
        mock_ppe.return_value = mock_pool

        from execution_server import WorkerProcess
        wp = WorkerProcess('worker-0')

        assert wp.is_idle() is True


class TestWorkerProcessSubmit:
    @patch('execution_server.ProcessPoolExecutor')
    def test_submit_func_sets_execution_id(self, mock_ppe):
        mock_pool = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 5555
        mock_pool.submit.return_value = mock_future
        mock_ppe.return_value = mock_pool

        from execution_server import WorkerProcess
        wp = WorkerProcess('worker-0')

        mock_func = MagicMock()
        wp.submit_func(mock_func, None, 'exec-1', 'elem-1', 'user1', 'ASYNC')

        assert wp.execution_id == 'exec-1'
        assert wp.run_mode == 'ASYNC'
        assert wp.future is mock_future

    @patch('execution_server.ProcessPoolExecutor')
    def test_submit_func_is_not_idle(self, mock_ppe):
        mock_pool = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 5555
        mock_pool.submit.return_value = mock_future
        mock_ppe.return_value = mock_pool

        from execution_server import WorkerProcess
        wp = WorkerProcess('worker-0')

        mock_func = MagicMock()
        wp.submit_func(mock_func, None, 'exec-1', 'elem-1', 'user1', 'SYNC')

        assert wp.is_idle() is False


class TestWorkerProcessDoneCallback:
    @patch('execution_server.ProcessPoolExecutor')
    def test_done_callback_clears_state(self, mock_ppe):
        mock_pool = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 5555
        mock_pool.submit.return_value = mock_future
        mock_ppe.return_value = mock_pool

        from execution_server import WorkerProcess
        wp = WorkerProcess('worker-0')

        mock_func = MagicMock()
        result_future = wp.submit_func(mock_func, None, 'exec-1', 'elem-1', 'user1', 'SYNC')

        wp.done_callback(result_future)

        assert wp.execution_id is None
        assert wp.run_mode is None
        assert wp.future is None

    @patch('execution_server.ProcessPoolExecutor')
    def test_done_callback_ignores_different_context(self, mock_ppe):
        mock_pool = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 5555
        mock_pool.submit.return_value = mock_future
        mock_ppe.return_value = mock_pool

        from execution_server import WorkerProcess
        wp = WorkerProcess('worker-0')

        mock_func = MagicMock()
        wp.submit_func(mock_func, None, 'exec-1', 'elem-1', 'user1', 'SYNC')

        other_future = MagicMock()
        wp.done_callback(other_future)

        assert wp.execution_id == 'exec-1'


class TestWorkerPoolSubmit:
    @patch('execution_server.ProcessPoolExecutor')
    def test_worker_pool_submit_func(self, mock_ppe):
        mock_pool = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 7777
        mock_pool.submit.return_value = mock_future
        mock_ppe.return_value = mock_pool

        from execution_server import WorkerPool
        pool = WorkerPool(2)

        assert len(pool.workers) == 2

        mock_func = MagicMock()
        result = pool.submit_func(mock_func, None, 'exec-1', 'elem-1', 'user1', 'ASYNC')
        assert result is mock_future


class TestWorkerPoolCancelRun:
    @patch('execution_server.ProcessPoolExecutor')
    @patch('execution_server.os.kill')
    @patch('execution_server.psutil.pids', return_value=[])
    def test_cancel_run_finds_worker(self, mock_pids, mock_kill, mock_ppe):
        mock_pool = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 7777
        mock_pool.submit.return_value = mock_future
        mock_ppe.return_value = mock_pool

        from execution_server import WorkerPool
        pool = WorkerPool(1)

        mock_func = MagicMock()
        pool.submit_func(mock_func, None, 'exec-1', 'elem-1', 'user1', 'ASYNC')

        found, run_mode = pool.cancel_run('exec-1')
        assert found is True
        assert run_mode == 'ASYNC'

    @patch('execution_server.ProcessPoolExecutor')
    def test_cancel_run_not_found(self, mock_ppe):
        mock_pool = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 7777
        mock_pool.submit.return_value = mock_future
        mock_ppe.return_value = mock_pool

        from execution_server import WorkerPool
        pool = WorkerPool(1)

        found, run_mode = pool.cancel_run('nonexistent')
        assert found is False
        assert run_mode is None
