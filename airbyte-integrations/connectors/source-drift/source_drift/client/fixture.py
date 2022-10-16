#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


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
