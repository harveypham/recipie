import unittest
from unittest.mock import Mock

from _context import recipie

from recipie.contextlib import *


class RollbackSpec(unittest.TestCase):

    def test_RollbackExecutesOnErrorAndPropagatesError(self):
        mock = Mock()
        with self.assertRaises(Exception):
            with rollback(mock):
                raise Exception("Intentional failure")
        mock.assert_called_once()

    def test_RollbackDoesNotExecuteOnNoError(self):
        mock = Mock()
        with rollback(mock):
            pass
        mock.assert_not_called()

class CommitSpec(unittest.TestCase):

    def test_CommitExecutesOnNoError(self):
        mock = Mock()
        with commit(mock):
            pass
        mock.assert_called_once()


    def test_CommitDoesNotExecuteOnErrorAndPropagatesError(self):
        mock = Mock()
        with self.assertRaises(Exception):
            with commit(mock):
                raise Exception("Intentional failure")
        mock.assert_not_called()
