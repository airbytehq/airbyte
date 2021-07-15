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

import base64
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from .streams import UserSettingsStream
from .streams import Users


class BasicAuthenticator(TokenAuthenticator):
    """basic Authorization header"""

    def __init__(self, email: str, password: str):
        token = base64.b64encode(f'{email}:{password}'.encode('utf-8'))
        super().__init__(token.decode('utf-8'), auth_method='Basic')


class BasicApiTokenAuthenticator(BasicAuthenticator):
    def __init__(self, email: str, token: str):
        super().__init__(email + '/token', token)


class SourceZendeskSupport(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        auth = BasicApiTokenAuthenticator(config['email'], config['api_token'])
        settings, err = UserSettingsStream(
            config['subdomain'], authenticator=auth).get_settings()
        if err:
            return None, err
        logger.info('available features: %s' % [
                    k for k, v in settings.get('active_features', {}).items() if v])
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        args = {
            'subdomain': config['subdomain'],
            'start_date': datetime.strptime(config['start_date'], '%Y-%m-%dT%H:%M:%SZ'),
            'authenticator': BasicApiTokenAuthenticator(config['email'], config['api_token']),
        }
        return [
            Users(**args)
        ]
