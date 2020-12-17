"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os

from .api import APIClient


class FakeDataFactory:
    @staticmethod
    def account(seed):
        return {
            "ownerId": 2000 + seed,
            "name": f"Company Name {seed}",
            "domain": f"www.domain.n{seed}.com",
            "customProperties": [{"label": "My Number", "name": " my number", "value": 1, "type": "NUMBER"}],
            "targeted": True,
        }

    @staticmethod
    def contact(seed):
        return {"attributes": {"email": f"airbyte-test-email-{seed}@airbyte.io"}}

    @staticmethod
    def conversation(seed, email=None):
        return {
            "email": email or f"airbyte-test-email-{seed}@airbyte.io",
            "message": {"body": f"Test conversation message #{seed}", "attributes": {"integrationSource": "Message from airbyte tests"}},
        }

    @staticmethod
    def message(seed):
        return {
            "type": "chat",
            "body": f"Test message #{seed}",
        }


def main():
    client = APIClient(access_token=os.getenv("DRIFT_TOKEN", "YOUR_TOKEN_HERE"))

    # create 120 accounts and 120 conversation with 120 new contacts
    for i in range(120):
        client.accounts.create(**FakeDataFactory.account(i + 1))
        conversation = client.conversations.create(**FakeDataFactory.conversation(i))
        # in each conversation create +3 additional messages
        for k in range(3):
            client.messages.create(conversation_id=conversation["id"], **FakeDataFactory.message(k))


if __name__ == "__main__":
    main()
