# ===============================================================================
# Copyright 2021 ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================
import imaplib
import email
from io import StringIO


class Client:
    def __init__(self, config):
        self._imap = imaplib.IMAP4_SSL('imap.gmail.com')
        self._config = config

    def login(self):
        config = self._config
        u, p = config['email_address'], config['email_password']
        rv, data = self._imap.login(u, p)

    def fetch_attachment(self, logger, prev):
        self._imap.select()
        logger.debug(f'fetch attachment. prev={prev}')
        cfg = self._config
        # rv, data = self._imap.search(None, cfg['email_subject'])
        rv, data = self._imap.search(None, f"SUBJECT \"{cfg['email_subject']}\"")
        for num in data[0].split():

            rv, data = self._imap.fetch(num, '(RFC822)')
            if rv != 'OK':
                print("ERROR getting message", num)
                return

            msg = email.message_from_bytes(data[0][1])
            hdr = str(email.header.make_header(email.header.decode_header(msg['Subject'])))
            logger.debug(f'checking message: {hdr}')
            if not prev or not hdr.startswith(prev):
                attachment = self._extract_attachment(msg)
                return hdr, attachment

    def _extract_attachment(self, msg):
        for part in msg.walk():
            # this part comes from the snipped I don't understand yet...
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            fileName = part.get_filename()
            if fileName:
                txt = part.get_payload(decode=True)
                txt = txt.decode('utf8')
                return StringIO(txt)
# ============= EOF =============================================
