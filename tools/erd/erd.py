from collections import OrderedDict
import json
import argparse
import sys

graph_template = """
digraph SourceERD {{

graph [
    label="Stream relationship diagram"
    labelloc="t"
    fontname="Helvetica,Arial,sans-serif"
    ranksep=3
    rankdir = "RL"
    overlap=scalexy
]

node [
    fontname="Helvetica,Arial,sans-serif"
    shape=record
    style=filled
    fillcolor=gray95
]

{nodes}

{edges}

}}
"""

node_template = """
{stream_name} [
    shape=plain
    label=<<table>
        <tr><td><b>{stream_name}  </b></td></tr>
        {fields}
    </table>>
]
"""


def get_main_fields(stream_info):
    show = OrderedDict()
    pk = stream_info['primary_key']
    if not isinstance(pk, list):
        pk = [pk]
    for key in pk:
        if key:
            show[key] = ['key']

    cursor_field = stream_info['cursor_field']
    if not isinstance(cursor_field, list):
        cursor_field = [cursor_field]
    for cursor in cursor_field:
        if cursor:
            if cursor in show:
                show[cursor].append('cursor')
            else:
                show[cursor] = ['cursor']

    stream_info['show'] = show


def find_rels_old(stream_name, stream_info, common_fields):
    for common_field, edge in common_fields.items():
        if common_field in stream_info['schema']:
            if common_field not in stream_info['show']:
                stream_info['show'][common_field] = ''
            if f'{stream_name}:' not in edge:
                stream_info['edges'].append(f'{stream_name}:"{common_field}" -> {edge}')


def find_rels(stream_name, stream_info, common_fields):
    for source, target in common_fields.items():
        if ':' not in source:
            source = f'*:{source}'
        node_name, field = source.split(':')
        if node_name in (stream_name, '*'):
            if field in stream_info['schema']:
                if field not in stream_info['show']:
                    stream_info['show'][field] = ''
                # check if we not
                if f'{stream_name}:' not in target:
                    stream_info['edges'].append(f'{stream_name}:{field} -> {target}')


def show_fields(ss):
    fields = '\n'
    for field, field_type in ss['show'].items():
        type = f'({",".join(field_type)})' if field_type else ''
        fields += f'            <tr><td align="left" port="{field}">- {field} {type}</td></tr>\n'

    return f'''
        <tr><td>
        <table border="0" cellborder="0" cellspacing="0">
            {fields}
            <tr><td align="left"> ... </td></tr>
        </table>
        </td></tr>
'''


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--catalog", help="Path to file full configured catalog with json schema")
    parser.add_argument("-e", "--edges", help="Path to edges file")
    args = parser.parse_args()

    configured_catalog_path = args.catalog
    with open(configured_catalog_path) as cc_file:
        cc = json.load(cc_file)
    if not cc:
        print(f'Unable to read configured catalog file: {configured_catalog_path}', file=sys.stderr)
        exit()

    edges_path = args.edges
    with open(edges_path) as edges_file:
        common_fields = json.load(edges_file)
    if not common_fields:
        print(f'Unable to read edges file: {edges_path}',  file=sys.stderr)

    info = {}
    for stream in cc['catalog']['streams']:
        info[stream['name']] = {
            'primary_key': ['/'.join(key) for key in stream.get('source_defined_primary_key', [])],
            'cursor_field': stream.get('default_cursor_field', []),
            'schema': stream['json_schema']['properties'],
            'show': [],
            'edges': [],
        }

    for stream_name, stream_info in info.items():
        get_main_fields(stream_info)
        find_rels(stream_name, stream_info, common_fields)

    nodes = '\n'
    for stream_name, stream_info in info.items():
        nodes += '\n' + node_template.format(stream_name=stream_name, fields=show_fields(stream_info))

    edges = '\n'
    for stream_name, stream_info in info.items():
        if stream_info['edges']:
            edges += '\n' + '\n'.join(stream_info['edges'])

    graph = graph_template.format(nodes=nodes, edges=edges)
    print(graph)
