from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from box_sdk_gen import CCGConfig, BoxCCGAuth, BoxClient


def get_box_ccg_client(config: Mapping[str, Any])->BoxClient:
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
    ccg_config = CCGConfig(
        client_id = client_id, 
        client_secret = client_secret, 
        enterprise_id = enterprise_id, 
        user_id = user_id
        )
    ccg_auth =  BoxCCGAuth(ccg_config)
    return BoxClient(ccg_auth)

