# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import logging
from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from box_sdk_gen import (
    AiAsk,
    AiItemBase,
    AiItemBaseTypeField,
    AiResponseFull,
    BoxCCGAuth,
    BoxClient,
    BoxSDKError,
    CCGConfig,
    CreateAiAskMode,
    File,
)


logger = logging.getLogger("airbyte")


@dataclass
class BoxFileExtended:
    file: File
    text_representation: str


def get_box_ccg_client(config: Mapping[str, Any]) -> BoxClient:
    client_id = config["client_id"]
    client_secret = config["client_secret"]
    box_subject_type = config["box_subject_type"]
    box_subject_id = config["box_subject_id"]

    if box_subject_type == "enterprise":
        enterprise_id = box_subject_id
        user_id = None
    else:
        enterprise_id = None
        user_id = box_subject_id
    ccg_config = CCGConfig(client_id=client_id, client_secret=client_secret, enterprise_id=enterprise_id, user_id=user_id)
    ccg_auth = BoxCCGAuth(ccg_config)
    return add_extra_header_to_box_client(BoxClient(ccg_auth))


def add_extra_header_to_box_client(box_client: BoxClient) -> BoxClient:
    """
    Add extra headers to the Box client.

    Args:
        box_client (BoxClient): A Box client object.
        header (Dict[str, str]): A dictionary of extra headers to add to the Box client.

    Returns:
        BoxClient: A Box client object with the extra headers added.
    """
    header = {"x-box-ai-library": "airbyte"}
    return box_client.with_extra_headers(extra_headers=header)


def _do_request(box_client: BoxClient, url: str):
    """
    Performs a GET request to a Box API endpoint using the provided Box client.

    This is an internal helper function and should not be called directly.

    Args:
        box_client (BoxClient): An authenticated Box client object.
        url (str): The URL of the Box API endpoint to make the request to.

    Returns:
        bytes: The content of the response from the Box API.

    Raises:
        BoxSDKError: If an error occurs while retrieving the access token.
        requests.exceptions.RequestException: If the request fails (e.g., network error,
                                             4XX or 5XX status code).
    """
    try:
        access_token = box_client.auth.retrieve_token().access_token
    except BoxSDKError as e:
        raise

    resp = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
    resp.raise_for_status()
    return resp.content


def box_file_get_by_id(client: BoxClient, file_id: str) -> File:
    return client.files.get_file_by_id(file_id=file_id)


def box_file_text_extract(client: BoxClient, file_id: str) -> str:
    # Request the file with the "extracted_text" representation hint
    file_text_representation = client.files.get_file_by_id(
        file_id,
        x_rep_hints="[extracted_text]",
        fields=["name", "representations"],
    )
    # Check if any representations exist
    if not file_text_representation.representations.entries:
        logger.debug(f"No representation for file {file_text_representation.id}")
        return ""

    # Find the "extracted_text" representation
    extracted_text_entry = next(
        (entry for entry in file_text_representation.representations.entries if entry.representation == "extracted_text"),
        None,
    )
    if not extracted_text_entry:
        return ""

    # Handle cases where the extracted text needs generation
    if extracted_text_entry.status.state == "none":
        _do_request(extracted_text_entry.info.url)  # Trigger text generation

    # Construct the download URL and sanitize filename
    url = extracted_text_entry.content.url_template.replace("{+asset_path}", "")

    # Download and truncate the raw content
    raw_content = _do_request(client, url)

    # check to see if rawcontent is bytes
    if isinstance(raw_content, bytes):
        return raw_content.decode("utf-8")
    else:
        return raw_content


def box_file_ai_ask(client: BoxClient, file_id: str, prompt: str) -> str:
    mode = CreateAiAskMode.SINGLE_ITEM_QA
    ai_item = AiItemBase(id=file_id, type=AiItemBaseTypeField.FILE)
    response = client.ai.create_ai_ask(mode=mode, prompt=prompt, items=[ai_item])
    return response.answer

def box_file_ai_extract(client: BoxClient, file_id: str,prompt:str) -> str:
    ai_item = AiItemBase(id=file_id, type=AiItemBaseTypeField.FILE)
    response = client.ai.create_ai_extract(prompt=prompt,items=[ai_item])
    return response.answer

def box_folder_text_representation(
    client: BoxClient, folder_id: str, is_recursive: bool = False, by_pass_text_extraction: bool = False
) -> Iterable[BoxFileExtended]:
    # folder items iterator
    for item in client.folders.get_folder_items(folder_id).entries:
        if item.type == "file":
            file = box_file_get_by_id(client=client, file_id=item.id)
            if not by_pass_text_extraction:
                text_representation = box_file_text_extract(client=client, file_id=item.id)
            else:
                text_representation = ""
            yield BoxFileExtended(file=file, text_representation=text_representation)
        elif item.type == "folder" and is_recursive:
            yield from box_folder_text_representation(
                client=client, folder_id=item.id, is_recursive=is_recursive, by_pass_text_extraction=by_pass_text_extraction
            )


def box_folder_ai_ask(
    client: BoxClient, folder_id: str, prompt: str, is_recursive: bool = False, by_pass_text_extraction: bool = False
) -> Iterable[BoxFileExtended]:
    # folder items iterator
    for item in client.folders.get_folder_items(folder_id).entries:
        if item.type == "file":
            file = box_file_get_by_id(client=client, file_id=item.id)
            if not by_pass_text_extraction:
                text_representation = box_file_ai_ask(client=client, file_id=item.id, prompt=prompt)
            else:
                text_representation = ""
            yield BoxFileExtended(file=file, text_representation=text_representation)
        elif item.type == "folder" and is_recursive:
            yield from box_folder_ai_ask(
                client=client, folder_id=item.id, prompt=prompt, is_recursive=is_recursive, by_pass_text_extraction=by_pass_text_extraction
            )

def box_folder_ai_extract(
    client: BoxClient, folder_id: str, prompt: str, is_recursive: bool = False, by_pass_text_extraction: bool = False
) -> Iterable[BoxFileExtended]:
    # folder items iterator
    for item in client.folders.get_folder_items(folder_id).entries:
        if item.type == "file":
            file = box_file_get_by_id(client=client, file_id=item.id)
            if not by_pass_text_extraction:
                text_representation = box_file_ai_extract(client=client, file_id=item.id, prompt=prompt)
            else:
                text_representation = ""
            yield BoxFileExtended(file=file, text_representation=text_representation)
        elif item.type == "folder" and is_recursive:
            yield from box_folder_ai_extract(
                client=client, folder_id=item.id, prompt=prompt, is_recursive=is_recursive, by_pass_text_extraction=by_pass_text_extraction
            )

