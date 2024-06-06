import os
import json
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader

JSON_SCHEMA_TO_D2 = {
    'string': "string",
    "integer": "int",
    "boolean": "bool"
}


def get_property_d2_type(v):
    # TODO: ref
    p_type = v.get('type')
    if isinstance(p_type, str):
        return p_type
    elif isinstance(p_type, list):
        real_type = [x for x in p_type if x != 'null'][0]
    if real_type in JSON_SCHEMA_TO_D2:
        return JSON_SCHEMA_TO_D2.get(real_type)
    return real_type


def main():
    """
    Main function to iterate through directory and convert JSON schemas.
    """
    CONNECTOR_NAME = 'source_facebook_marketing'
    schema_dir = f"/Users/artem.inzhyyants/PycharmProjects/airbyte/airbyte-integrations/connectors/source-facebook-marketing/{CONNECTOR_NAME}/schemas"
    output_file = f"/Users/artem.inzhyyants/PycharmProjects/airbyte/airbyte-integrations/connectors/source-facebook-marketing/{CONNECTOR_NAME}/schemas/combined_schemas.d2"

    schemas = []

    for filename in os.listdir(schema_dir):
        if filename.startswith('shared'): continue
        stream_name = filename.split('.')[0]
        json_schema = ResourceSchemaLoader(CONNECTOR_NAME).get_schema(stream_name)
        properties = json_schema['properties']
        relations = json_schema.get('_erd_relations', {})
        d2_props = []
        for k, v in properties.items():
            property_type = get_property_d2_type(v)
            stream_prop = f"{k}: {property_type}"
            if v.get('_erd_constrains'):
                stream_prop = f"{stream_prop} {{constraint: {v.get('_erd_constrains')} }}"
            d2_props.append(stream_prop)
            d_props_joined = '\n'.join(d2_props)
            relations_joined = '\n'.join([f"{stream_name}.{k} -> {v}" for k, v in relations.items()])
        schemas.append(f"""{stream_name}: {{
  shape: sql_table
  {d_props_joined}
}}
{relations_joined}""")
    with open(output_file, "w") as f:
        f.write('\n'.join(schemas))


if __name__ == "__main__":
    main()
    # TODO: generate svg using docker CLI: https://github.com/terrastruct/d2/blob/master/docs/INSTALL.md#docker
