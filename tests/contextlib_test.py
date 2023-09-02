import unittest
from unittest.mock import Mock

from _context import recipie

from recipie.contextlib import *
from recipie.functools import no_op


class RollbackSpec(unittest.TestCase):

    def test_RollbackExecutesOnErrorAndPropagatesError(self):
        mock = Mock()
        with self.assertRaises(Exception):
            with rollback(mock, 1, 2, 3):
                raise Exception("Intentional failure")
        mock.assert_called_once_with(1, 2, 3)

    def test_RollbackDoesNotExecuteOnNoError(self):
        mock = Mock()
        with rollback(mock):
            pass
        mock.assert_not_called()

class CommitSpec(unittest.TestCase):

    def test_CommitExecutesOnNoError(self):
        mock = Mock()
        with commit(mock, 1, 2, 3):
            pass
        mock.assert_called_once_with(1, 2, 3)

    def test_CommitDoesNotExecuteOnErrorAndPropagatesError(self):
        mock = Mock()
        with self.assertRaises(Exception):
            with commit(mock):
                raise Exception("Intentional failure")
        mock.assert_not_called()

class CleanupSpec(unittest.TestCase):

    def test_CleanupExecutesOnNoError(self):
        mock = Mock()
        with cleanup(mock, 1, 2, 3):
            pass
        mock.assert_called_once_with(1, 2, 3)

    def test_CleanupExecutesOnError(self):
        mock = Mock()
        with self.assertRaises(AssertionError):
            with cleanup(mock, 1, 2, 3):
                assert False, "Intentional failure"
        mock.assert_called_once_with(1, 2, 3)

    def test_CleanupDoesNotExecuteIfCanceled(self):
        mock = Mock()
        with cleanup(mock, 1, 2, 3) as task:
            task.cancel()
        mock.assert_not_called()


class BufferSpec(unittest.TestCase):

    def testBufferSizeMustBeMoreThanOne(self):
        Buffer(2, no_op)
        self.assertRaises(AssertionError, Buffer, 1, no_op)

    def testClearNotCallOnEmptyBuffer(self):
        mock = Mock()
        Buffer(2, mock).clear()
        mock.assert_not_called()

    def testAppendWaitsUntilClosingWhenNotExceedingBufferSize(self):
        mock = Mock()
        with Buffer(2, mock) as buffer:
            buffer.append(1)
            buffer.append(2)
            mock.assert_not_called()

        mock.assert_called_once_with([1, 2])

    def testAppendTriggerCallsWhenExceedingBufferSize(self):
        mock = Mock()
        with Buffer(2, mock) as buffer:
            buffer.append(1)
            buffer.append(2)
            mock.assert_not_called()
            buffer.append(3)
            mock.assert_called_once_with([1, 2])

        self.assertEqual(mock.call_count, 2)
        mock.assert_called_with([3])

    def testExtend(self):
        mock = Mock()
        with Buffer(2, mock) as buffer:
            with self.subTest("Extend does not trigger call if buffer size is within limit"):
                buffer.extend([1, 2])
                mock.assert_not_called()

            with self.subTest("Extend triggers calls if buffer size exceeds its size"):
                buffer.extend([3, 4])
                mock.assert_called_once_with([1, 2])

        self.assertEqual(mock.call_count, 2)
        mock.assert_called_with([3, 4])
