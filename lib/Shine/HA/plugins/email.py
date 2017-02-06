#
# Copyright (C) 2017 Board of Trustees, Leland Stanford Jr. University
#
# Written by Stephane Thiell <sthiell@stanford.edu>
#
#   --*-*- Stanford University Research Computing Center -*-*--
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""shine-HA email alerting"""

from __future__ import absolute_import

from datetime import datetime
from email.mime.text import MIMEText
import logging
import sys

from ClusterShell.Task import task_self
import Shine.CLI.Display as Display
from Shine.HA.alerts import Alert, ALERT_CLS_FS

LOGGER = logging.getLogger(__name__)


class EmailAlert(Alert):
    """shine-HA Email Alert class"""

    def __init__(self, email_from, email_to, subject_prefix='', reply_to=None,
                 sendmail_cmd='/usr/sbin/sendmail', sendmail_args='-t -oi'):
        Alert.__init__(self, 'email')
        self.email_from = email_from
        self.email_to = email_to
        self.subject_prefix = subject_prefix
        self.reply_to = reply_to
        self.sendmail_cmd = sendmail_cmd
        self.sendmail_args = sendmail_args

    def sendmail(self, subject, message):
        """Send email using local MTA"""

        # Create a text/plain message
        msg = MIMEText(message)
        msg['From'] = self.email_from
        msg['To'] = self.email_to
        msg['Subject'] = self.subject_prefix + subject
        if self.reply_to:
            msg['Reply-To'] = self.reply_to

        cmd = [self.sendmail_cmd] + self.sendmail_args.split()
        LOGGER.debug('EmailAlert.sendmail: cmd=%s msg=%s', cmd, msg.as_string())
        worker = task_self().shell(' '.join(cmd))
        worker.write(msg.as_string())
        worker.set_write_eof()

    def _fs_error(self, level, message, ctx):
        comps = ctx['FileSystem'].components.managed(inactive=True)

        # Display FS Status (part of the code from Shine.CLI.Display)
        pat_fields = set(['status', 'node', 'type'])

        def fieldvals(comp):
            """Get the value list of field for ``comp''."""
            return Display._get_fields(comp, pat_fields).values()

        grplst = [(list(compgrp)[0], compgrp)
                  for _, compgrp in comps.groupby(key=fieldvals)]

        att_fields = []
        for first, compgrp in grplst:
            # Get component fields
            fields = Display._get_fields(first, pat_fields)
            compgrpstr = '%s (%d)' % (str(compgrp.labels()),
                                      len(compgrp.labels()))
            att_fields.append('%-10s %-16s %s' % (fields['status'],
                                                  fields['node'],
                                                  compgrpstr))

        body = 'ALERT LEVEL: %s\n\n' % level
        body += 'LUSTRE STATE OVERVIEW:\n\n'
        body += '%-10s %-16s %s\n' % ('STATE', 'NODE', 'COMPONENTS')
        body += '\n'.join(att_fields)
        body += '\n\n'

        if 'comp_st_cnt_list' in ctx:
            comp_st_cnt_list = ctx['comp_st_cnt_list']
            started, compid = min((scobj.started, scobj.comp.uniqueid())
                                  for scobj in comp_st_cnt_list)
            started_strdate = datetime.fromtimestamp(started) \
                                      .strftime('%Y-%m-%d %H:%M:%S')
            body += 'ISSUE STARTED FOR %s ON %s\n' % (compid, started_strdate)

        body += '\n\n'
        body += 'Generated by %s' % sys.modules[__name__].__file__
        body += '\n'
        self.sendmail(message, body)

    def info(self, aclass, message, ctx=None):
        if aclass == ALERT_CLS_FS:
            self._fs_error('INFO', message, ctx)

    def warning(self, aclass, message, ctx=None):
        if aclass == ALERT_CLS_FS:
            self._fs_error('WARNING', message, ctx)

    def critical(self, aclass, message, ctx=None):
        if aclass == ALERT_CLS_FS:
            self._fs_error('CRITICAL', message, ctx)


ALERT_CLASS = EmailAlert