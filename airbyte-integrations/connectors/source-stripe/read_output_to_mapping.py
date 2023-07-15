import dataclasses
import json
import sys
from dataclasses import dataclass
from typing import Mapping, Any, Optional

from airbyte_cdk.models import AirbyteMessage

@dataclass(eq=True, frozen=True)
class RequestDescriptor:
    url: str
    headers: Optional[Mapping[str, str]]
    body: Optional[Mapping[str, Any]]


@dataclass(eq=True, frozen=True)
class ResponseDescriptor:
    status_code: int
    body: Any # FIXME obviously this is not the right type
    headers: Any


replace = {
    "acct_1JwnoiEcXtiJtvvh": "my_stripe_account_id",
}

mapping = []
request = None
response = None
for lin in sys.stdin:
    for before, after in replace.items():
        lin = lin.replace(before, after)
    try:
        obj = json.loads(lin)
        if obj["type"] == "DEBUG":
            if obj["message"].startswith("Making outbound API request"):
                if request is not None:
                    mapping.append((request, response))
                    request = None
                    response = None
                request = RequestDescriptor(url=obj["data"]["url"],
                                            headers=obj["data"]["headers"],
                                            body=obj["data"]["request_body"])
            elif obj["message"].startswith("Receiving response"):
                response = ResponseDescriptor(
                    body=obj["data"]["body"],
                    status_code=int(obj["data"]["status"]),
                    headers=obj["data"]["headers"],
                )
    except:
        pass

if request is not None:
    mapping.append((request, response))
    request = None
    response = None
tuples = [(dataclasses.astuple(req), dataclasses.astuple(res)) for req, res in mapping]
for t in tuples:
    print(json.dumps(t))
