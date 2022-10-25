# Script para gerar schemas automaticamente a partir dos streams especificados no configured catalog.
# Você deve especificar no input (config.json) que seja apenas 1 pagina com 1 registro.
# Então você deve executar o seguinte comando: 
# python main.py read --config secrets/config.json --catalog sample_files/configured_catalog.json | python generate_schema.py

import sys
from time import sleep
import json

def generate_schema():
    while True:
        line = sys.stdin.readline()
        if not line:
            break

        print(line.strip())
        line_strip = line.strip()

        if line_strip is None or line_strip == '':
            pass
        elif '{' in line_strip:
            record = json.loads(line_strip)
            if record["type"] == "RECORD":
                print(record["record"])
                columns = list(record["record"]["data"].keys())

                properties = {
                        column: {
                            "type": [
                                "null",
                                "string"
                            ]
                        }
                        for column in columns
                    }

                properties.update({"_ab_cdc_updated_at": {"type": ["null","string"]}})
                properties.update({"_ab_cdc_deleted_at": {"type": ["null","string"]}})

                schema = {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": properties,
                    "additionalProperties": True
                }

                with open(f'source_crm_365/schemas/{record["record"]["stream"]}.json','w') as schema_file:
                    json.dump(schema,schema_file,indent=2)         
    return


if __name__ == "__main__":
    generate_schema()