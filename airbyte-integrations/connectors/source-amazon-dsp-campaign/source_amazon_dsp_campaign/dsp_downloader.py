import sys
import time
import requests
import json
import random
from datetime import datetime, timedelta




# Report class to store report configurations

class Report:

    def __init__(self, report_type, format, time_unit, dimensions, metrics,report_start_date,report_end_date):

        self.report_type = report_type
        self.format = format
        self.time_unit = time_unit
        self.dimensions = dimensions
        self.metrics = metrics
        self.report_start_date=report_start_date
        self.report_end_date = report_end_date

# Magic method to print the report configurations

    def __str__(self):

        return (
            f"\nReport Type: {self.report_type}\n"
            f"Format: {self.format}\n"
            f"Time Unit: {self.time_unit}\n"
            f"Dimensions: {self.dimensions}\n"
            f"Metrics: {self.metrics}\n"
        )


# Credentials class to store credentials

class Credentials:

    def __init__(self, refresh_token, client_id, client_secret, auth_url,access_token=""):

        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.auth_url=auth_url

# Magic method to print the credentials

    def __str__(self):

        return (
            f"Refresh Token: {self.refresh_token}\n"
            f"\nClient ID: {self.client_id}\n"
            f"\nClient Secret: {self.client_secret}\n"
            f"\nAccess Token: {self.access_token}\n"
        )


# Advertiser class to store advertiser configurations

class Advertiser:

    def __init__(self, advertiser_name, advertiser_id, region, country, aws_region, base_url):

        self.advertiser_name = advertiser_name
        self.advertiser_id = advertiser_id
        self.region = region
        self.country = country
        self.aws_region = aws_region
        self.base_url = base_url

# Magic method to print the advertiser configurations

    def __str__(self):

        return (
            f"\nCustomer ID: {self.advertiser_name}\n"
            f"Account Info ID (Entity ID): {self.advertiser_id}\n"
            f"Region: {self.region}\n"
            f"Country: {self.country}\n"
            f"AWS Region: {self.aws_region}\n"
            f"Base URL: {self.base_url}\n"
        )

    def __repr__(self):
        return str(self)


# Explicit method to get the required access token for the API

def get_access_token(credentials):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "refresh_token",
        "client_id": credentials.client_id,
        "refresh_token": credentials.refresh_token,
        "client_secret": credentials.client_secret
    }

    response = requests.post(
        credentials.auth_url, headers=headers, data=data)
    r_json = response.json()
    json_object = json.dumps(r_json, indent=4)
    return r_json["access_token"]

# Explicit method to handle api respnse error codes- 429,500,504

def handle_status_codes(response,advertiser,report_config):
        if response.status_code == 429:
            print(
                f"Error {response.status_code}:\nToo many requests... Retrying...\n")
            return -1
        elif response.status_code == 500 or response.status_code == 504:
            print(
                f"Error {response.status_code}:\nError occured due to possible intermittent issue... Retrying...\n")
            return -1
        elif response.status_code // 100 == 2:
            return 1
        else:
            response.raise_for_status()

# Explicit method to generate and fetch the report id which can be used in the later stages to download the report

def create_report_and_get_reportid(credentials, advertiser, report_config):
    print(advertiser)
    headers = {
        "Amazon-Advertising-API-ClientId": credentials.client_id,
        "Authorization": "Bearer " + credentials.access_token,
        "Content-Type": "application/json",
        "Accept": "application/vnd.dspcreatereports.v3+json"
    }


    data = {
        "startDate": report_config.report_start_date,
        "endDate": report_config.report_end_date,
        "format": report_config.format,
        "timeUnit": report_config.time_unit,
        "type": report_config.report_type,
        "dimensions": report_config.dimensions,
        "metrics": report_config.metrics,
    }
    url = (
        f"{advertiser.base_url}/accounts/{advertiser.advertiser_id}/dsp/reports")

    while True:
        response = requests.post(url, headers=headers, json=data)
        status = handle_status_codes(response,advertiser,report_config)
        if status == -1:
            time.sleep(3)
        else:
            r_json = response.json()
            json_object = json.dumps(r_json, indent=4)

            print("Requesting DSP Report...\n"
                  f"Status Code: {response.status_code}\n"
                  f"Report Status: {r_json['status']}\n"
                  f"Report ID: {r_json['reportId']}\n")
            return r_json["reportId"]

# Explicit method to download the report using the report id generated in the previous step

def download_report(credentials, advertiser, report_id,report_config):

    headers = {
        "Amazon-Advertising-API-ClientId": credentials.client_id,
        "Authorization": "Bearer " + credentials.access_token,
        "Content-Type": "application/json",
        "Accept": "application/vnd.dspgetreports.v3+json",
        "Accept-Encoding": "gzip, deflate, br"
    }

    api_url = (
        f"{advertiser.base_url}/accounts/{advertiser.advertiser_id}/dsp/reports/{report_id}")
    start_time = time.time()
    base_delay = 0.05  # Starting with a 50ms delay
    max_delay = 16     # Maximum delay should be capped for practicality, here it's 16 seconds
    while True:
        response = requests.get(api_url, headers=headers)
        status = handle_status_codes(response,advertiser,report_config)
        if status == -1:
            time.sleep(4)
        else:
            r_json = response.json()
            if r_json["status"] == "IN_PROGRESS":
                print("DSP Report Generation In Progress...\n"
                      f"Status Code: {response.status_code}\n"
                      f"Report Status: {r_json['status']}\n"
                      f"Report ID: {r_json['reportId']}\n")
                # Implement exponential backoff with jitter for IN_PROGRESS status
                delay = min(base_delay * (2 ** ((time.time() - start_time) / 10)), max_delay)  # Using division to slow down the exponential growth
                jitter = delay * random.uniform(0.5, 1.5)
                sleep_time = delay + jitter
                time.sleep(sleep_time)
                # time.sleep(4)
            elif r_json["status"] == "SUCCESS":
                print("DSP Report Generation Complete.\n")
                print(f"{r_json}\n")
                # json_object = json.dumps(r_json, indent=4)
                # write_finalfile(json_object)
                return r_json
# Method to log the configuration file


def log_config_file(print_list):
    """
        Method to log DSP configuration
    """
    string_list = ["REPORT CONFIGURATION", "CREDENTIALS", "ADVERTISERS"]

    for i, item in enumerate(print_list):
        print(
            f"-------------------------------{string_list[i]}-------------------------------\n"
            f"{item}\n"
        )
    print(f"-----------------------------------------------------------------------\n")


def generate(advertiser, credentials, report_config):
    report_id = create_report_and_get_reportid(
        credentials, advertiser, report_config)

    return download_report(credentials, advertiser, report_id,report_config)



# Explict class to execute the entire flow
class execute():
    # Static method for execute class to run the entire flow
    @staticmethod
    def runfile(start_date,end_date,config,**kwargs):
            credentials = Credentials(
                config["refresh_token"],
                config["client_id"],
                config["client_secret"],
                config["auth_url"]["default"]
            )
            credentials.access_token = get_access_token(credentials)
            report_type=config['report_types']['report_type']
            report_config = Report(
                report_type.upper(),
                config["format"] if "format" in config else "CSV",
                config["time_unit"] if "time_unit" in config else "DAILY",
                config["report_types"]["dimensions"].split(","),
                config["report_types"]["reqbody"]["metrics"].split(","),
                start_date,end_date

            )

            advertisers = []
            if (config["advertisers"]["active"] == True):
                advertisers.append(Advertiser(
                    config["advertisers"]["advertiser_name"],
                    config["advertisers"]["advertiser_id"],
                    config["advertisers"]["region"],
                    config["advertisers"]["country"],
                    config["advertisers"]["aws_region"],
                    config["advertisers"]["url"]
                ))

                log_config_file([report_config, credentials, advertisers])

                for advertiser in advertisers:
                        return generate(advertiser, credentials, report_config)


                   