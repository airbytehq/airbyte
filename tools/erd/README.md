# erd
ERD util generates code for ERD diagram (Graphviz's dot language)
https://graphviz.org/Gallery/directed/UML_Class_diagram.html

Generated code can be visualized on any visual editor, like:
http://magjac.com/graphviz-visual-editor/

DOT code is generated based on:
- connectors "configured catalog" file:
  - show node for each stream
  - show primary key fields
  - show cursor fields
- "edges" file (should be created manually):
  - show edges between nodes (linkage)
  - show additional fields which are used in linkage

# "edges" file format
Edges file contain information which is used for 'edges' creation, for example
```json
{
  "<dependant_stream>:<dependant_field>": "<main_stream_name>:<main_field>",
  "*:<dependant_field>": "<main_stream_name>:<main_field>",
  "*:account_id": "account:id"  # means, all streams with field 'account_id' depends on stream 'account' with field 'id'
}
```
"*:field_a" - means, all streams with 'field_a' will be linked to main_stream_name

## Usage
```bash
python erd.py --catalog <path_configured_catalog_file> --edges <path_to_edges_file>
```
It will generate code for ERD diagram 