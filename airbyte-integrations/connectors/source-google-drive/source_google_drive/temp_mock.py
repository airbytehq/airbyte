from typing import Any, Iterator


def _get_looping_google_api_list_response(service: Any, key: str, args: dict[str, Any]) -> Iterator[dict[str, Any]]:
    domain = args.get("domain") or args.get("groupKey")

    if key == "users":
        # Mocking 5 users
        for i in range(1, 6):
            yield {
                "primaryEmail": f"user{i}@{domain}",
                "name": {"fullName": f"User {i}"},
                "emails": [{"address": f"user{i}@{domain}"}],
            }

    elif key == "groups":
        # Mocking 5 groups
        for i in range(1, 6):
            yield {
                "email": f"group{i}@{domain}",
                "name": f"Group {i}",
                "id": f"group-id-{i}",
            }

    elif key == "members":
        # Mocking 5 members per group
        group_id = args.get("groupKey")
        for i in range(1, 6):
            yield {
                "email": f"member{i}@{domain}",
                "role": "MEMBER",
                "type": "USER",
                "groupId": group_id,
            }
