import genson
import json
import os
import logging

logger = logging.getLogger(__name__)

DEST_NAME = "source_vk_ads_new"

for filename in os.listdir(os.path.join(DEST_NAME, "schemas")):

    filename = os.path.join(DEST_NAME, "schemas", filename)

    is_populated = False
    can_populate = False

    print(f"Get {filename}...")
    with open(filename, "r") as f:
        fileobj = json.load(f)
        if isinstance(fileobj, dict):
            if "$schema" in fileobj.keys():
                is_populated = True
                print(f"{filename} is already populated with JSON schema")
                continue
            can_populate = True
        else:
            raise Exception(f"file {filename} doesn't contain obj")

    if not is_populated and can_populate:
        print(f"{filename} populating...")

        with open(filename, "w") as f:
            builder = genson.SchemaBuilder()
            builder.add_object(fileobj)
            f.write(builder.to_json(indent=2))

        print(f"{filename} populating successfull")
