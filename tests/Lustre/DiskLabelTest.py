#!/usr/bin/env python
# Shine.Lustre.Disk test suite: label check against tunefs.lustre output

"""Unit tests for Disk._mountdata_check() label parsing"""

import unittest
from unittest import mock

from Shine.Lustre.Disk import Disk, DiskDeviceError

TUNEFS_OUTPUT = """checking for existing Lustre data: found

   Read previous values:
Target:     %s
Index:      6
Lustre FS:  fir
Mount type: ldiskfs
Flags:      0x2
              (OST )
Persistent mount opts: errors=remount-ro

Permanent disk data:
Target:     ignored
"""


def fake_tunefs(target):
    process = mock.Mock()
    process.communicate.return_value = \
        ((TUNEFS_OUTPUT % target).encode(), b'')
    process.returncode = 0
    return process


class DiskLabelTest(unittest.TestCase):

    def _check(self, target, label='fir-OST0006'):
        disk = Disk(dev='/dev/md6')
        with mock.patch('Shine.Lustre.Disk.subprocess.Popen',
                        return_value=fake_tunefs(target)):
            disk._mountdata_check(label_check=label)
        return disk

    def testDash(self):
        """fsname-svname label: accepted"""
        disk = self._check('fir-OST0006')
        self.assertEqual(disk.ldd_svname, 'fir-OST0006')
        self.assertEqual(disk._ldd_flags, 0x2)

    def testColon(self):
        """fsname:svname label (target not yet registered): accepted"""
        self.assertEqual(self._check('fir:OST0006').ldd_svname, 'fir-OST0006')

    def testEqual(self):
        """fsname=svname label: accepted"""
        self.assertEqual(self._check('fir=OST0006').ldd_svname, 'fir-OST0006')

    def testMismatch(self):
        """different label: device error"""
        self.assertRaises(DiskDeviceError, self._check, 'fir-OST0007')


if __name__ == '__main__':
    unittest.main()
