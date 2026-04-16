# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any, Dict, Optional

import requests_mock as rm

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_BOT_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
_BASE_URL = f"https://api.telegram.org/bot{_BOT_TOKEN}"
_CHAT_ID = "-1001234567890"


def _config(chat_ids: Optional[list] = None, allowed_updates: Optional[list] = None) -> Dict[str, Any]:
    config: Dict[str, Any] = {"bot_token": _BOT_TOKEN}
    if chat_ids is not None:
        config["chat_ids"] = chat_ids
    if allowed_updates is not None:
        config["allowed_updates"] = allowed_updates
    return config


def _read(
    stream_name: str,
    config: Optional[Dict[str, Any]] = None,
    sync_mode: SyncMode = SyncMode.full_refresh,
) -> EntrypointOutput:
    cfg = config or _config()
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=cfg)
    return entrypoint_read(source, cfg, catalog)


def _telegram_ok(result: Any) -> Dict[str, Any]:
    return {"ok": True, "result": result}


# --- get_me stream ---


def test_get_me_returns_bot_info(requests_mock: rm.Mocker) -> None:
    requests_mock.get(
        f"{_BASE_URL}/getMe",
        json=_telegram_ok(
            {
                "id": 123456,
                "is_bot": True,
                "first_name": "TestBot",
                "username": "test_bot",
                "can_join_groups": True,
                "can_read_all_group_messages": False,
                "supports_inline_queries": False,
            }
        ),
    )
    output = _read("get_me")
    assert len(output.records) == 1
    record = output.records[0].record.data
    assert record["id"] == 123456
    assert record["is_bot"] is True
    assert record["first_name"] == "TestBot"
    assert record["username"] == "test_bot"


def test_get_me_no_errors(requests_mock: rm.Mocker) -> None:
    requests_mock.get(
        f"{_BASE_URL}/getMe",
        json=_telegram_ok(
            {
                "id": 123456,
                "is_bot": True,
                "first_name": "TestBot",
                "username": "test_bot",
            }
        ),
    )
    output = _read("get_me")
    assert len(output.errors) == 0


# --- updates stream ---


def test_updates_returns_messages(requests_mock: rm.Mocker) -> None:
    requests_mock.get(
        f"{_BASE_URL}/getUpdates",
        json=_telegram_ok(
            [
                {
                    "update_id": 100001,
                    "message": {
                        "message_id": 1,
                        "from": {"id": 111, "is_bot": False, "first_name": "User"},
                        "chat": {"id": -100123, "title": "Test Group", "type": "supergroup"},
                        "date": 1700000000,
                        "text": "Hello world",
                    },
                },
                {
                    "update_id": 100002,
                    "channel_post": {
                        "message_id": 2,
                        "chat": {"id": -100456, "title": "Test Channel", "type": "channel"},
                        "date": 1700000001,
                        "text": "Channel announcement",
                    },
                },
            ]
        ),
    )
    output = _read("updates")
    assert len(output.records) == 2
    assert output.records[0].record.data["update_id"] == 100001
    assert output.records[0].record.data["message"]["text"] == "Hello world"
    assert output.records[1].record.data["update_id"] == 100002
    assert output.records[1].record.data["channel_post"]["text"] == "Channel announcement"


def test_updates_empty_result(requests_mock: rm.Mocker) -> None:
    requests_mock.get(
        f"{_BASE_URL}/getUpdates",
        json=_telegram_ok([]),
    )
    output = _read("updates")
    assert len(output.records) == 0


# --- chats stream ---


def test_chats_returns_chat_info(requests_mock: rm.Mocker) -> None:
    requests_mock.get(
        f"{_BASE_URL}/getChat",
        json=_telegram_ok(
            {
                "id": -1001234567890,
                "type": "supergroup",
                "title": "Test Group",
                "username": "testgroup",
                "description": "A test group",
                "is_forum": False,
            }
        ),
    )
    output = _read("chats", config=_config(chat_ids=[_CHAT_ID]))
    assert len(output.records) == 1
    record = output.records[0].record.data
    assert record["id"] == -1001234567890
    assert record["type"] == "supergroup"
    assert record["title"] == "Test Group"


def test_chats_multiple_chat_ids(requests_mock: rm.Mocker) -> None:
    requests_mock.get(
        f"{_BASE_URL}/getChat",
        [
            {"json": _telegram_ok({"id": -1001111111111, "type": "supergroup", "title": "Group One"})},
            {"json": _telegram_ok({"id": -1002222222222, "type": "channel", "title": "Channel Two"})},
        ],
    )
    output = _read("chats", config=_config(chat_ids=["-1001111111111", "-1002222222222"]))
    assert len(output.records) == 2


def test_chats_no_chat_ids_returns_nothing() -> None:
    output = _read("chats", config=_config(chat_ids=[]))
    assert len(output.records) == 0


# --- chat_administrators stream ---


def test_chat_administrators_returns_admins(requests_mock: rm.Mocker) -> None:
    requests_mock.get(
        f"{_BASE_URL}/getChatAdministrators",
        json=_telegram_ok(
            [
                {
                    "status": "creator",
                    "user": {
                        "id": 111,
                        "is_bot": False,
                        "first_name": "Admin",
                        "username": "admin_user",
                    },
                    "is_anonymous": False,
                    "custom_title": "Owner",
                },
                {
                    "status": "administrator",
                    "user": {
                        "id": 123456,
                        "is_bot": True,
                        "first_name": "TestBot",
                        "username": "test_bot",
                    },
                    "is_anonymous": False,
                    "can_manage_chat": True,
                    "can_delete_messages": False,
                },
            ]
        ),
    )
    output = _read("chat_administrators", config=_config(chat_ids=[_CHAT_ID]))
    assert len(output.records) == 2
    creator = output.records[0].record.data
    assert creator["status"] == "creator"
    assert creator["user"]["username"] == "admin_user"
    assert str(creator["_chat_id"]) == _CHAT_ID
    bot_admin = output.records[1].record.data
    assert bot_admin["status"] == "administrator"
    assert str(bot_admin["_chat_id"]) == _CHAT_ID


# --- webhook_info stream ---


def test_webhook_info_returns_info(requests_mock: rm.Mocker) -> None:
    requests_mock.get(
        f"{_BASE_URL}/getWebhookInfo",
        json=_telegram_ok(
            {
                "url": "",
                "has_custom_certificate": False,
                "pending_update_count": 0,
            }
        ),
    )
    output = _read("webhook_info")
    assert len(output.records) == 1
    record = output.records[0].record.data
    assert record["url"] == ""
    assert record["has_custom_certificate"] is False
    assert record["pending_update_count"] == 0


def test_webhook_info_with_errors_and_updates(requests_mock: rm.Mocker) -> None:
    requests_mock.get(
        f"{_BASE_URL}/getWebhookInfo",
        json=_telegram_ok(
            {
                "url": "https://example.com/webhook",
                "has_custom_certificate": True,
                "pending_update_count": 5,
                "ip_address": "1.2.3.4",
                "last_error_date": 1700000000,
                "last_error_message": "Connection timed out",
                "max_connections": 40,
                "allowed_updates": ["message", "callback_query"],
            }
        ),
    )
    output = _read("webhook_info")
    assert len(output.records) == 1
    record = output.records[0].record.data
    assert record["url"] == "https://example.com/webhook"
    assert record["pending_update_count"] == 5
    assert record["last_error_message"] == "Connection timed out"
    assert record["allowed_updates"] == ["message", "callback_query"]
