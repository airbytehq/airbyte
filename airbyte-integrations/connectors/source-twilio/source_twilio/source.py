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

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import SyncMode
from airbyte_cdk.logger import AirbyteLogger
from source_twilio.auth import HttpBasicAuthenticator
from source_twilio.streams import Accounts, Addresses, DependentPhoneNumbers, Applications, AvailablePhoneNumberCountries, \
    AvailablePhoneNumbersLocal, AvailablePhoneNumbersMobile, AvailablePhoneNumbersTollFree, IncomingPhoneNumbers, Keys, Calls, Conferences, \
    ConferenceParticipants, OutgoingCallerIds, Recordings, Transcriptions, Queues, Messages, MessageMedia, UsageRecords, UsageTriggers, \
    Alerts


class SourceTwilio(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            auth = HttpBasicAuthenticator((config["account_sid"], config["auth_token"],),)
            accounts_gen = Accounts(authenticator=auth, start_date=config["start_date"]).read_records(
                sync_mode=SyncMode.full_refresh
            )
            next(accounts_gen)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Twilio API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = HttpBasicAuthenticator((config["account_sid"], config["auth_token"],),)

        streams = [
            Accounts(authenticator=auth, start_date=config["start_date"]),
            Addresses(authenticator=auth, start_date=config["start_date"]),
            DependentPhoneNumbers(authenticator=auth, start_date=config["start_date"]),
            Applications(authenticator=auth, start_date=config["start_date"]),
            AvailablePhoneNumberCountries(authenticator=auth),
            AvailablePhoneNumbersLocal(authenticator=auth),
            AvailablePhoneNumbersMobile(authenticator=auth),
            AvailablePhoneNumbersTollFree(authenticator=auth),
            IncomingPhoneNumbers(authenticator=auth, start_date=config["start_date"]),
            Keys(authenticator=auth, start_date=config["start_date"]),
            Calls(authenticator=auth, start_date=config["start_date"]),
            Conferences(authenticator=auth, start_date=config["start_date"]),
            ConferenceParticipants(authenticator=auth),
            OutgoingCallerIds(authenticator=auth, start_date=config["start_date"]),
            Recordings(authenticator=auth, start_date=config["start_date"]),
            Transcriptions(authenticator=auth, start_date=config["start_date"]),
            Queues(authenticator=auth, start_date=config["start_date"]),
            Messages(authenticator=auth, start_date=config["start_date"]),
            MessageMedia(authenticator=auth, start_date=config["start_date"]),
            UsageRecords(authenticator=auth, start_date=config["start_date"]),
            UsageTriggers(authenticator=auth, start_date=config["start_date"]),
            Alerts(authenticator=auth),
        ]
        return streams
