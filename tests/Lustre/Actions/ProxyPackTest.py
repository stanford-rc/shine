#!/usr/bin/env python
# Shine.Lustre.Actions.Proxy test suite: message packing

"""Unit tests for shine_msg_pack()/shine_msg_unpack() and pickle_protocol"""

import binascii
import pickle
import unittest

from Shine.Configuration.Globals import Globals
from Shine.Lustre.Actions.Proxy import shine_msg_pack, shine_msg_unpack, \
                                       SHINE_MSG_MAGIC


def _protocol(msg):
    """Pickle protocol number of a packed shine message."""
    data = binascii.a2b_base64(msg.split(b':', 2)[2])
    assert data[0:1] == pickle.PROTO
    return data[1]


class ProxyPackTest(unittest.TestCase):

    def tearDown(self):
        Globals().replace('pickle_protocol', 4)

    def testDefaultProtocol(self):
        """default pickle protocol is 4"""
        self.assertEqual(Globals().get_pickle_protocol(), 4)
        msg = shine_msg_pack(evtype='comp', status='done')
        self.assertTrue(msg.startswith(SHINE_MSG_MAGIC))
        self.assertEqual(_protocol(msg), 4)

    def testRoundTrip(self):
        """packed message unpacks to the same dict"""
        data = {'evtype': 'comp', 'status': 'done', 'rc': 0}
        self.assertEqual(shine_msg_unpack(shine_msg_pack(**data)), data)

    def testConfiguredProtocol(self):
        """pickle_protocol from the configuration is used"""
        Globals().replace('pickle_protocol', 2)
        self.assertEqual(Globals().get_pickle_protocol(), 2)
        self.assertEqual(_protocol(shine_msg_pack(evtype='comp')), 2)


if __name__ == '__main__':
    unittest.main()
