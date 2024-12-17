from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping, Union, MutableMapping, Optional, Tuple
from box_sdk_gen import CCGConfig, BoxCCGAuth, BoxClient,File,FileMini,FolderMini,WebLink, Items

@dataclass
class BoxFileExtended:
    file:File
    text_representation:str



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
    # TODO Add Header for statistics gathering
    return BoxClient(ccg_auth)

def box_file_get_by_id(client:BoxClient,file_id:str)->File:
    return client.files.get_file_by_id(file_id=file_id)

def box_file_text_extract(client:BoxClient,file_id:str)->str:
    # TODO Implement text extraction
    pass

def box_folder_items_get_by_id(client:BoxClient, folder_id:str)-> Iterable[List[BoxFileExtended]]:
    # folder items iterator
    for item in client.folders.get_folder_items(folder_id).entries:
        if item.type == "file":
            file = box_file_get_by_id(client=client,file_id=item.id)
            text_representation = box_file_text_extract(client=client,file_id=item.id)
            yield BoxFileExtended(file=file,text_representation=text_representation)
        # TODO add recursive folder items retrieval
