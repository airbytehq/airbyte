#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import responses
from source_maestro_qa.source import BASE_URL


data_url = f"{BASE_URL}csv-data-url"

def setup_good_response():
    responses.add(
        responses.POST,
        f"{BASE_URL}request-groups-export",
        json={
            "exportId": "123",
        },
    )

    responses.add(
        responses.GET,
        f"{BASE_URL}get-export-data",
        json={
            "status": "complete",
            "dataUrl": data_url,
        }
    )

    responses.add(
        responses.GET,
        data_url,
        body="""
group_name,group_id,agent_name,agent_email,agent_ids,available
All Agents,groupid1,Jon Doe,john@doe.com,10061553646875,False
All Agents,groupid1,Frank Lopez,frank@lopez.com,qppMJnv8L6KGZMYEN,False
All Agents,groupid1,Jon Snow,jon@snow.com,1267169520869,False
""",
    )


def setup_bad_response():
    responses.add(
        responses.POST,
        f"{BASE_URL}request-groups-export",
        status=401,
    )

    responses.add(
        responses.GET,
        f"{BASE_URL}get-export-data",
        json={
            "status": "errored"
        }
    )

