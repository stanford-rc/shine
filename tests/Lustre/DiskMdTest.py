#!/usr/bin/env python
# Shine.Lustre test suite: md array without /dev node (issue #1)

"""Unit tests for md array detection and Target.full_check without device node"""

import os
import shutil
import tempfile
import unittest

import Shine.Lustre.Disk as DiskModule
from Shine.Lustre.Disk import Disk, DiskNoDeviceException
from Shine.Lustre.Component import ComponentError, MOUNTED, RECOVERING, \
                                   OFFLINE, NO_DEVICE, TARGET_ERROR
from Shine.Lustre.FileSystem import FileSystem
from Shine.Lustre.Server import Server


class MdSysfsTestCase(unittest.TestCase):
    """Fake /sys/block and a /dev/md6 path that does not exist."""

    def setUp(self):
        self.sysfs = tempfile.mkdtemp(prefix='shine-test-sysfs-')
        self._saved = DiskModule.SYSFS_BLOCK
        DiskModule.SYSFS_BLOCK = self.sysfs
        self.devdir = tempfile.mkdtemp(prefix='shine-test-dev-')
        self.dev = os.path.join(self.devdir, 'md6')

    def tearDown(self):
        DiskModule.SYSFS_BLOCK = self._saved
        shutil.rmtree(self.sysfs)
        shutil.rmtree(self.devdir)

    def _md(self, state, members=(), name='md6'):
        mddir = os.path.join(self.sysfs, name, 'md')
        os.makedirs(mddir)
        with open(os.path.join(mddir, 'array_state'), 'w') as fstate:
            fstate.write(state + '\n')
        for member in members:
            os.mkdir(os.path.join(mddir, 'dev-' + member))


class DiskMdTest(MdSysfsTestCase):

    def testNoArray(self):
        """no md array in sysfs: not assembled"""
        self.assertFalse(Disk(dev=self.dev)._md_assembled())

    def testArrayAssembled(self):
        """md array with member disks: assembled"""
        self._md('active', ['dm-1', 'dm-2'])
        self.assertTrue(Disk(dev=self.dev)._md_assembled())

    def testArrayInactive(self):
        """md array inactive, no members listed: assembled"""
        self._md('inactive')
        self.assertTrue(Disk(dev=self.dev)._md_assembled())

    def testArrayCleared(self):
        """empty md entry left after a stop: not assembled"""
        self._md('clear')
        self.assertFalse(Disk(dev=self.dev)._md_assembled())

    def testNotMd(self):
        """device that is not mdN: sysfs not used"""
        self._md('active', ['dm-1'], name='sdz')
        self.assertFalse(Disk(dev=os.path.join(self.devdir, 'sdz'))._md_assembled())

    def testDeviceCheckUnchanged(self):
        """missing node: _device_check still raises DiskNoDeviceException"""
        self._md('active', ['dm-1'])
        self.assertRaises(DiskNoDeviceException, Disk(dev=self.dev)._device_check)


class TargetNoNodeTest(MdSysfsTestCase):
    """Target.full_check() when the device node is missing."""

    def _target(self, dev, lustre_state=OFFLINE, lustre_error=False):
        fs = FileSystem('testfs')
        srv = Server('localhost', ['localhost@tcp'])
        fs.local_server = srv
        tgt = fs.new_target(srv, 'ost', 0, dev)

        def fake_lustre_check():
            if lustre_error:
                tgt.local_state = TARGET_ERROR
                raise ComponentError(tgt, "incoherent state")
            tgt.local_state = lustre_state
        tgt.lustre_check = fake_lustre_check
        return tgt

    def testAssembledNotMounted(self):
        """md assembled, Lustre not mounted: offline"""
        self._md('active', ['dm-1'])
        tgt = self._target(self.dev)
        tgt.full_check()
        self.assertEqual(tgt.local_state, OFFLINE)

    def testAssembledMounted(self):
        """md assembled, Lustre mounted: mounted"""
        self._md('active', ['dm-1'])
        tgt = self._target(self.dev, MOUNTED)
        tgt.full_check()
        self.assertEqual(tgt.local_state, MOUNTED)

    def testAssembledRecovering(self):
        """md assembled, Lustre recovering: recovering"""
        self._md('active', ['dm-1'])
        tgt = self._target(self.dev, RECOVERING)
        tgt.full_check()
        self.assertEqual(tgt.local_state, RECOVERING)

    def testNoArray(self):
        """no md array, Lustre not mounted: no_device"""
        tgt = self._target(self.dev)
        tgt.full_check()
        self.assertEqual(tgt.local_state, NO_DEVICE)

    def testArrayCleared(self):
        """empty md entry, Lustre not mounted: no_device"""
        self._md('clear')
        tgt = self._target(self.dev)
        tgt.full_check()
        self.assertEqual(tgt.local_state, NO_DEVICE)

    def testNotMd(self):
        """missing non-md device, Lustre not mounted: no_device"""
        tgt = self._target(os.path.join(self.devdir, 'sdz'))
        tgt.full_check()
        self.assertEqual(tgt.local_state, NO_DEVICE)

    def testLustreIncoherent(self):
        """incoherent Lustre state is still an error"""
        self._md('active', ['dm-1'])
        tgt = self._target(self.dev, lustre_error=True)
        self.assertRaises(ComponentError, tgt.full_check)
        self.assertEqual(tgt.local_state, TARGET_ERROR)


if __name__ == '__main__':
    unittest.main()
