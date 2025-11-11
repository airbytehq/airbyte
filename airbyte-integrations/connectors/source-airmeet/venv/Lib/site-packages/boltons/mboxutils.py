# Copyright (c) 2013, Mahmoud Hashemi
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * The names of the contributors may not be used to endorse or
#      promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Useful utilities for working with the `mbox`_-formatted
mailboxes. Credit to Mark Williams for these.

.. _mbox: https://en.wikipedia.org/wiki/Mbox
"""

import mailbox
import tempfile


DEFAULT_MAXMEM = 4 * 1024 * 1024  # 4MB


class mbox_readonlydir(mailbox.mbox):
    """A subclass of :class:`mailbox.mbox` suitable for use with mboxs
    insides a read-only mail directory, e.g., ``/var/mail``. Otherwise
    the API is exactly the same as the built-in mbox.

    Deletes messages via truncation, in the manner of `Heirloom mailx`_.

    Args:
        path (str): Path to the mbox file.
        factory (type): Message type (defaults to :class:`rfc822.Message`)
        create (bool): Create mailbox if it does not exist. (defaults
                       to ``True``)
        maxmem (int): Specifies, in bytes, the largest sized mailbox
                      to attempt to copy into memory. Larger mailboxes
                      will be copied incrementally which is more
                      hazardous. (defaults to 4MB)

    .. note::

       Because this truncates and rewrites parts of the mbox file,
       this class can corrupt your mailbox.  Only use this if you know
       the built-in :class:`mailbox.mbox` does not work for your use
       case.

    .. _Heirloom mailx: http://heirloom.sourceforge.net/mailx.html
    """
    def __init__(self, path, factory=None, create=True, maxmem=1024 * 1024):
        mailbox.mbox.__init__(self, path, factory, create)
        self.maxmem = maxmem

    def flush(self):
        """Write any pending changes to disk. This is called on mailbox
        close and is usually not called explicitly.

        .. note::

           This deletes messages via truncation. Interruptions may
           corrupt your mailbox.
        """

        # Appending and basic assertions are the same as in mailbox.mbox.flush.
        if not self._pending:
            if self._pending_sync:
                # Messages have only been added, so syncing the file
                # is enough.
                mailbox._sync_flush(self._file)
                self._pending_sync = False
            return

        # In order to be writing anything out at all, self._toc must
        # already have been generated (and presumably has been modified
        # by adding or deleting an item).
        assert self._toc is not None

        # Check length of self._file; if it's changed, some other process
        # has modified the mailbox since we scanned it.
        self._file.seek(0, 2)
        cur_len = self._file.tell()
        if cur_len != self._file_length:
            raise mailbox.ExternalClashError('Size of mailbox file changed '
                                             '(expected %i, found %i)' %
                                             (self._file_length, cur_len))

        self._file.seek(0)

        # Truncation logic begins here.  Mostly the same except we
        # can use tempfile because we're not doing rename(2).
        with tempfile.TemporaryFile() as new_file:
            new_toc = {}
            self._pre_mailbox_hook(new_file)
            for key in sorted(self._toc.keys()):
                start, stop = self._toc[key]
                self._file.seek(start)
                self._pre_message_hook(new_file)
                new_start = new_file.tell()
                while True:
                    buffer = self._file.read(min(4096,
                                                 stop - self._file.tell()))
                    if buffer == '':
                        break
                    new_file.write(buffer)
                new_toc[key] = (new_start, new_file.tell())
                self._post_message_hook(new_file)
            self._file_length = new_file.tell()

            self._file.seek(0)
            new_file.seek(0)

            # Copy back our messages
            if self._file_length <= self.maxmem:
                self._file.write(new_file.read())
            else:
                while True:
                    buffer = new_file.read(4096)
                    if not buffer:
                        break
                    self._file.write(buffer)

            # Delete the rest.
            self._file.truncate()

        # Same wrap up.
        self._toc = new_toc
        self._pending = False
        self._pending_sync = False
        if self._locked:
            mailbox._lock_file(self._file, dotlock=False)
