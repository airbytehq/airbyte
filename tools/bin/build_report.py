#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import requests
import re
from slack_sdk import WebhookClient
from slack_sdk.errors import SlackApiError


def get_status_page(connector) -> str:
    response = requests.get(f'https://dnsgjos7lj2fu.cloudfront.net/tests/summary/{connector}/index.html')
    if response.status_code == 200:
        return response.text


def parse(page) -> list:
    history = []
    for row in re.findall(r'<tr>(.*?)</tr>', page):
        cols = re.findall(r'<td>(.*?)</td>', row)
        if not cols or len(cols) != 3:
            continue
        history.append({
            'date': cols[0],
            'status': re.findall(r' (\S+)</span>', cols[1])[0],
            'link': re.findall(r'href="(.*?)"', cols[2])[0],
        })
    return history


def check_connector(connector):
    status_page = get_status_page(connector)

    # check if connector is tested
    if not status_page:
        NO_TESTS.append(connector)
        print('F', end='', flush=True)
        return

    print('.', end='', flush=True)

    if connector.startswith('source'):
        TESTED_SOURCE.append(connector)
    elif connector.startswith('destination'):
        TESTED_DESTINATION.append(connector)

    # order: recent values goes first
    history = parse(status_page)
    # order: recent values goes last
    short_status = ''.join(['✅' if build['status'] == 'success' else '❌' for build in history[::-1]])  # ex: ❌✅✅❌✅✅❌❌

    # check latest build status
    last_build = history[0]
    if last_build['status'] == 'success':
        if connector.startswith('source'):
            SUCCESS_SOURCE.append(connector)
        elif connector.startswith('destination'):
            SUCCESS_DESTINATION.append(connector)
    else:
        failed_today = [connector, short_status, last_build['link']]

        if len(history) > 1 and history[1]['status'] != 'success':
            FAILED_2_LAST.append(failed_today)
            return

        FAILED_LAST.append(failed_today)


def failed_report(failed_report) -> str:
    max_name_len = max([len(connector[0]) for connector in failed_report])
    max_status_len = max(len(connector[1]) for connector in failed_report)
    for connector in failed_report:
        connector[0] = connector[0].ljust(max_name_len, ' ')
        connector[1] = connector[1].rjust(max_status_len, ' ')
    return '\n'.join([' '.join(connector) for connector in failed_report])


def create_report(connectors) -> str:

    sources_len = len([name for name in connectors if name.startswith('source')])
    destinations_len = len([name for name in connectors if name.startswith('destination')])

    report = f"""
CONNECTORS:   total: {len(connectors)}
Sources:      total: {sources_len} / tested: {len(TESTED_SOURCE)} / success: {len(SUCCESS_SOURCE)} ({round(len(SUCCESS_SOURCE)/sources_len*100, 1)}%)
Destinations: total: {destinations_len} / tested: {len(TESTED_DESTINATION)} / success: {len(SUCCESS_DESTINATION)} ({round(len(SUCCESS_DESTINATION)/destinations_len*100, 1)}%)

"""
    if FAILED_LAST:
        report += f"FAILED LAST BUILD ONLY - {len(FAILED_LAST)} connectors:\n" + \
                  failed_report(FAILED_LAST) + '\n\n'

    if FAILED_2_LAST:
        report += f"FAILED TWO LAST BUILDS - {len(FAILED_2_LAST)} connectors:\n" + \
                  failed_report(FAILED_2_LAST) + '\n\n'

    if NO_TESTS:
        report += f"NO TESTS - {len(NO_TESTS)} connectors:\n" + '\n'.join(NO_TESTS) + '\n'

    return report


def send_report(report):
    webhook = WebhookClient(os.environ["SLACK_BUILD_REPORT"])
    try:
        def chunk_messages(report):
            """split report into messages with no more than 4000 chars each (slack limitation)"""
            msg = ''
            for line in report.splitlines():
                msg += line + '\n'
                if len(msg) > 3500:
                    yield msg
                    msg = ''
            yield msg
        for msg in chunk_messages(report):
            webhook.send(text=f"```{msg}```")
        print(f'Report has been sent')
    except SlackApiError as e:
        print(f'Unable to send report')
        assert e.response["error"]


TESTED_SOURCE = []
TESTED_DESTINATION = []
SUCCESS_SOURCE = []
SUCCESS_DESTINATION = []
NO_TESTS = []
FAILED_LAST = []
FAILED_2_LAST = []


if __name__ == "__main__":
    # find all connectors
    connectors = sorted(os.listdir("./airbyte-integrations/connectors"))
    print(f"Checking connectors: {len(connectors)}")

    # analyse build results for each connector
    [check_connector(connector) for connector in connectors]

    report = create_report(connectors)
    print(report)
    send_report(report)
    print('Finish')
