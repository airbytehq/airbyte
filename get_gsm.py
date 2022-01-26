#!/usr/bin/env python3

import os
import base64
import binascii

GCP_GSM_CREDENTIALS = os.getenv("GCP_GSM_CREDENTIALS")
print("-".join([x for x in GCP_GSM_CREDENTIALS]))
