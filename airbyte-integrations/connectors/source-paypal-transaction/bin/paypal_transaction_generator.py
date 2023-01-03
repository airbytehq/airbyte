#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

#
# REQUIREMENTS:
# 1. sudo apt-get install chromium-chromedriver
# 2. pip install selenium
# 3. ../secrets/creds.json with buyers email/password and account client_id/secret

# HOW TO USE:
# python paypal_transaction_generator.py    - will generate 3 transactions by default
# python paypal_transaction_generator.py 10 - will generate 10 transactions

import json
import random
import sys
from time import sleep

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# from pprint import pprint


PAYMENT_DATA = {
    "intent": "sale",
    "payer": {"payment_method": "paypal"},
    "transactions": [
        {
            "amount": {
                "total": "30.11",
                "currency": "USD",
                "details": {
                    "subtotal": "30.00",
                    "tax": "0.07",
                    "shipping": "0.03",
                    "handling_fee": "1.00",
                    "shipping_discount": "-1.00",
                    "insurance": "0.01",
                },
            },
            "description": "This is the payment transaction description.",
            "custom": "EBAY_EMS_90048630020055",
            "invoice_number": "CHAMGE_IT",
            "payment_options": {"allowed_payment_method": "INSTANT_FUNDING_SOURCE"},
            "soft_descriptor": "ECHI5786755",
            "item_list": {
                "items": [
                    {
                        "name": "hat",
                        "description": "Brown color hat",
                        "quantity": "5",
                        "price": "3",
                        "tax": "0.01",
                        "sku": "1",
                        "currency": "USD",
                    },
                    {
                        "name": "handbag",
                        "description": "Black color hand bag",
                        "quantity": "1",
                        "price": "15",
                        "tax": "0.02",
                        "sku": "product34",
                        "currency": "USD",
                    },
                ],
                "shipping_address": {
                    "recipient_name": "Hello World",
                    "line1": "4thFloor",
                    "line2": "unit#34",
                    "city": "SAn Jose",
                    "country_code": "US",
                    "postal_code": "95131",
                    "phone": "011862212345678",
                    "state": "CA",
                },
            },
        }
    ],
    "note_to_payer": "Contact us for any questions on your order.",
    "redirect_urls": {"return_url": "https://example.com", "cancel_url": "https://example.com"},
}


def read_json(filepath):
    with open(filepath, "r") as f:
        return json.loads(f.read())


def get_api_token():

    client_id = CREDS.get("client_id")
    secret = CREDS.get("secret")

    token_refresh_endpoint = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    data = "grant_type=client_credentials"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    auth = (client_id, secret)
    response = requests.request(method="POST", url=token_refresh_endpoint, data=data, headers=headers, auth=auth)
    response_json = response.json()
    # print(response_json)
    API_TOKEN = response_json["access_token"]
    return API_TOKEN


def random_digits(digits):
    lower = 10 ** (digits - 1)
    upper = 10**digits - 1
    return random.randint(lower, upper)


def make_payment():

    # generate new invoice_number
    PAYMENT_DATA["transactions"][0]["invoice_number"] = random_digits(11)

    response = requests.request(
        method="POST", url="https://api-m.sandbox.paypal.com/v1/payments/payment", headers=headers, data=json.dumps(PAYMENT_DATA)
    )
    response_json = response.json()
    # pprint(response_json)

    execute_url = ""
    approval_url = ""

    for link in response_json["links"]:
        if link["rel"] == "approval_url":
            approval_url = link["href"]
        elif link["rel"] == "execute":
            execute_url = link["href"]
        elif link["rel"] == "self":
            self_url = link["href"]

    print(f"Payment made: {self_url}")
    return approval_url, execute_url


# APPROVE PAYMENT
def login():
    driver = webdriver.Chrome("/usr/bin/chromedriver")

    # SIGN_IN
    driver.get("https://www.sandbox.paypal.com/ua/signin")
    driver.find_element_by_id("email").send_keys(CREDS["buyer_username"])
    driver.find_element_by_id("btnNext").click()
    sleep(2)
    driver.find_element_by_id("password").send_keys(CREDS["buyer_password"])
    driver.find_element_by_id("btnLogin").click()
    return driver


def approve_payment(driver, url):
    driver.get(url)
    global cookies_accepted

    sleep(3)
    if not cookies_accepted:
        cookies = driver.find_element_by_id("acceptAllButton")
        if cookies:
            cookies.click()

        cookies_accepted = True
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "payment-submit-btn")))
    sleep(1)
    element.click()

    # sleep(5)
    # driver.find_element_by_id("payment-submit-btn").click()

    wait = WebDriverWait(driver, 5)
    wait.until(EC.title_is("Example Domain"))
    print(f"Payment approved: {driver.current_url}")


def execute_payment(url):
    response = requests.request(method="POST", url=url, data='{"payer_id": "ZE5533HZPGMC6"}', headers=headers)
    response_json = response.json()
    print(f'Payment executed: {url} with STATE: {response_json["state"]}')


TOTAL_TRANSACTIONS = int(sys.argv[1]) if len(sys.argv) > 1 else 3

CREDS = read_json("../secrets/creds.json")
headers = {"Authorization": f"Bearer {get_api_token()}", "Content-Type": "application/json"}
driver = login()
cookies_accepted = False
for i in range(TOTAL_TRANSACTIONS):
    print(f"Payment #{i}")
    approval_url, execute_url = make_payment()
    approve_payment(driver, approval_url)
    execute_payment(execute_url)
driver.quit()
