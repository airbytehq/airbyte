#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json


# this key was generated with rsa library from cryptography
test_private_key = """
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCjM57/r+LuNv9z
Bbe7+sMCJJm6t1MafRfxYVEz9c52/mLa5iEnpJfE+NRFgyp8hE8t493Btt/bJk94
2bMthZqMh2n9dIJZOUYBzd5MHLOc6vCUHFZT9fzHX/yTrz/bxa31BQs6c1p2HOiY
Kr3r0Dyj5jXsKo0mgt+iVKGgcSZ6NCzMRL8N9M++13k2RUPwaGksuyNqzAqgNhHd
wQcuS42AEFEOT1sfa4xG5mMY6+tPKDP92/ISHNUMD9NpzIA8A+tFX/w/L5VQKR3r
fTfrSTtkG6qF+3ARdeKqpxrW4ZPHuzNH8Y2I1uBuVaDvmZMvi+BLKgwwhWuEGjB1
j6Tv4TgXAgMBAAECggEAJTXLXlPdg1/hzXlzw3XwyYfLz0EmPwdfkqcUKysz2Hi2
1F8dFxtViVEMoQ6/fKV0Iivur1DBaIerHgxQ6KOqMblcRrAuWiaPWjD0qtjucOw2
TybI3hrbeB/gCFIwVq0TNSbhwQF1EjIULEGujNotQVdnWwH2rd2wHKR8N4ck9T6b
SKz8+u21RY2cBprneS6wxh+dvba8+7cpHn4cB+TB6UMeUow01LF4ye+hYVDNx6j9
VcdWXlH9fCy/GUTF4um+ABunlMCm6D5DAUVeiugd+ChSKzqOlV/H17EK1MF4HAjh
Alo2FJrKd8/ZwX1Xmngi9Y2Dlggmfiw4HzeNZNFFPQKBgQDmeQxDBvZapjdJntOM
DccoQGJyZMznd277xefKTfZLetcWWtgantW7IAxEEbwZOfrQFnBsNIlnreGPoZ7n
DL2jv/oVeEcr29FxlbDR2R1/h8Mp7d41Qi1Sd9RAhGcVtYZhLCCMMxt4DN7/v77M
2lc3B0NhgC3kxOJCC8kN2gqSTQKBgQC1RyENp1UTOSUbFsx1WbAzy2K974CRnL54
uK7efoLQ7fLh6OsRlBoy60aUpHv2tCb5ac+xdMELoAQu3PQKJMDJITstwgM4p6AP
x32lAHzOYnhG9/3P7kc29OaY8tlkDAn0ckv05DLAGLbKAemcGKW3/u08EITQtdW7
dEH75Ow98wKBgQDb5tV3QrZeKcgI251XPXIwCrakFV+Y3tErM1qFIbwFqtB8yPL2
+2RM5jgt3ooNu89/KlncNIiCP1s/k2Mta2+qRStVvuyRgWympsAOic1meGATqp1h
TaI21JTVdj9xbEEqiFMJ0l28PvOrLAXeKdobbDezWPzxEZYclGgiak+55QKBgBVU
6W7R4hEBCHzHkge9Jh7yMAxpwpdf+on6MZm9CWfMmGg9IGxRIUQcq5GSSYQebveq
m+Yl9xGHIvbgyVboPEduwagAzKA+GXfB4ecox4cBz2WKiTOOtpKg/wHAkhRT1lgN
myKWN+KjBd9/mh3kSJv+Q6xtxTNKMnx8kccyiRpBAoGBAJV9AAXj4icaDiPKoQw5
UERTGuVoEpWbc3yi/PXJ99fQxHZIHQa7a7VyyTHsDplqWu/qfHFHj+IJops8+l1F
U7PQBfXvIpubb55EhNCaID1VaRauGjW2x8PGA/27KQ3mB1uxEZUO8crcDYvPsZJf
jHfASOY3OsGgYW95pkyx5TH7
-----END PRIVATE KEY-----

"""

AUTH_BODY = "grant_type=refresh_token&client_id=43987534895734985.apps.googleusercontent.com&client_secret=2347586435987643598&refresh_token=1%2F%2F4398574389537495437983457985437"

service_account_info = {
    "type": "service_account",
    "project_id": "test-project-id",
    "private_key_id": "test-private-key-id",
    "private_key": test_private_key,
    "client_email": "test-service-account@test-project.iam.gserviceaccount.com",
    "client_id": "1234567890",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test-service-account%40test-project.iam.gserviceaccount.com",
}

service_account_info_encoded = json.dumps(service_account_info).encode("utf-8")

service_account_credentials = {
    "auth_type": "Service",
    "service_account_info": service_account_info_encoded,
}


oauth_credentials = {
    "auth_type": "Client",
    "client_id": "43987534895734985.apps.googleusercontent.com",
    "client_secret": "2347586435987643598",
    "refresh_token": "1//4398574389537495437983457985437",
}
