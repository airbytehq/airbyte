#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from pytest import fixture


@fixture(name="config")
def config_fixture():
    config = {
        "access_token": "TOKEN",
        "start_date": "2022-03-20T00:00:00Z",
    }

    return config


@fixture
def single_conversation_response():
    return {
        "type": "conversation",
        "id": "151272900024304",
        "created_at": 1647365706,
        "updated_at": 1647366443,
        "conversation_parts": {
            "type": "conversation_part.list",
            "conversation_parts": [
                {"type": "conversation_part", "id": "13740311965"},
                {"type": "conversation_part", "id": "13740312024"},
            ],
            "total_count": 2,
        },
    }

@fixture
def conversation_parts_responses():
    return [
        (
            "https://api.intercom.io/conversations", 
            _conversations_response(
                conversations=[
                    {"id":"151272900026677","updated_at":1650988600},
                    {"id":"151272900026666","updated_at":1650988500}
                ],
                next_url="https://api.intercom.io/conversations?per_page=2&page=2"
            )
        ),
        (
            "https://api.intercom.io/conversations?per_page=2&page=2",
            _conversations_response(
                conversations=[
                    {"id":"151272900026466","updated_at":1650988450},
                    {"id":"151272900026680","updated_at":1650988100}, # Older than state, won't be processed
                ]
            )
        ),
        (
            "https://api.intercom.io/conversations/151272900026677",
            _conversation_response(
                conversation_id="151272900026677",
                conversation_parts=[
                    {"id": "13740311961","updated_at":1650988300},
                    {"id": "13740311962","updated_at":1650988450}
                ]
            )
        ),
        (
            "https://api.intercom.io/conversations/151272900026666",
            _conversation_response(
                conversation_id="151272900026666",
                conversation_parts=[
                    {"id": "13740311955","updated_at":1650988150},
                    {"id": "13740312056","updated_at":1650988500}
                ]
            )
        ),
        (
            "https://api.intercom.io/conversations/151272900026466",
            _conversation_response(
                conversation_id="151272900026466",
                conversation_parts=[{"id": "13740311970","updated_at":1650988600}]
            )
        )
    ]


def  _conversations_response(conversations, next_url = None):
    return {
        "type": "conversation.list",
        "pages": {"next": next_url} if next_url else {},
        "conversations": conversations
    }


def _conversation_response(conversation_id, conversation_parts):
    return {
        "type": "conversation",
        "id": conversation_id,
        "conversation_parts": {
            "type": "conversation_part.list",
            "conversation_parts": conversation_parts,
            "total_count": len(conversation_parts),
        },
    }
