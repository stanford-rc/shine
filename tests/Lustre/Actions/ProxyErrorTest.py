#!/usr/bin/env python
# Shine.Lustre.Actions.Proxy test suite: errors reported by remote nodes

"""Unit tests for FSProxyAction error handling"""

import time
import unittest
from unittest import mock

from ClusterShell.NodeSet import NodeSet

import Shine.Lustre.Actions.Proxy as ProxyModule
from Shine.Lustre.Actions.Proxy import FSProxyAction, ProxyActionUnpickleError


class FakeFS(object):
    fs_name = 'testfs'

    def __init__(self):
        self.errors = []

    def _handle_shine_proxy_error(self, nodes, message):
        self.errors.append((str(nodes), message))


class ProxyErrorTest(unittest.TestCase):

    def _worker(self, node, rc=0):
        worker = mock.Mock()
        worker.current_node = node
        worker.current_msg = b'SHINE:3:garbage'
        worker.did_timeout.return_value = False
        worker.iter_retcodes.return_value = [(rc, [node])]
        worker.nodes = NodeSet(node)
        return worker

    def _run(self, exc):
        fs = FakeFS()
        action = FSProxyAction(fs, 'status', NodeSet('node1,node2'), False)
        action.start = time.time()   # set by launch() normally
        with mock.patch.object(ProxyModule, 'shine_msg_unpack',
                               side_effect=exc):
            for node in ('node1', 'node2'):
                action.ev_read(self._worker(node))
                # the same message twice is reported once
                action.ev_read(self._worker(node))
        action.ev_close(self._worker('node1'))
        return fs.errors

    def testUnpickleError(self):
        """unpickling error from remote nodes: reported, no exception"""
        errors = self._run(ProxyActionUnpickleError(
            "Cannot unpickle message: unsupported pickle protocol: 5"))
        self.assertEqual(len(errors), 1)
        nodes, message = errors[0]
        self.assertEqual(NodeSet(nodes), NodeSet('node1,node2'))
        self.assertIsInstance(message, bytes)
        self.assertIn(b'unsupported pickle protocol: 5', message)
        self.assertEqual(message.count(b'unsupported'), 1)

    def testAttributeError(self):
        """unreadable message (AttributeError): reported, no exception"""
        errors = self._run(AttributeError("no attribute 'x'"))
        self.assertEqual(len(errors), 1)
        self.assertIn(b'Cannot read message', errors[0][1])


if __name__ == '__main__':
    unittest.main()
