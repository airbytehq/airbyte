#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


def req_body(offset, endpoint: str):
    return {"SERVICE": f"{endpoint}.get", "FILTER": {}, "OFFSET": offset}


def get_next_page_token(response, response_key: str, API_OFFSET_LIMIT: int, endpoint: str):
    response = response.json()
    offset = response["REQUEST"]["OFFSET"] if response["REQUEST"]["OFFSET"] >= 0 else None
    if offset is None:
        response_request = response["REQUEST"]["OFFSET"]
        raise Exception(f"No valid offset value found:{response_request}")

    if len(response["RESPONSE"][response_key]) == API_OFFSET_LIMIT:
        return req_body(offset + API_OFFSET_LIMIT, endpoint)
    return None


def get_request_body_json(next_page_token, endpoint):
    if next_page_token:
        return next_page_token
    else:
        return {"SERVICE": f"{endpoint}.get", "FILTER": {}, "OFFSET": 0}
