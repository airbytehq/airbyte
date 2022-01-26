#!/usr/bin/env python3

import os
import base64
import binascii
print(base64.b64encode(os.getenv("GCP_GSM_CREDENTIALS").encode('ascii')).decode('ascii'))
