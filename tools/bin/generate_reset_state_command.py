import click
import json

# Example usage: python tools/bin/generate_reset_state_command.py ./query_result_2024-05-10T00_19_00.930855Z.json
def get_stream_condition(stream_state):
    escaped_stream_name = stream_state['stream_descriptor']['name'].replace("'", "''")
    if 'namespace' in stream_state['stream_descriptor']:
        escaped_namespace = stream_state['stream_descriptor']['namespace'].replace("'", "''")
        namespace_condition = f"namespace = '{escaped_namespace}'"
    else:
        namespace_condition = 'namespace IS NULL'
    return f"(stream_name = '{escaped_stream_name}' AND {namespace_condition})"

@click.command()
@click.argument('filename', type=click.Path(exists=True))
def run(filename: str):
    output = 'BEGIN TRANSACTION;\n'
    with open(filename) as f:
        last_good_states = json.load(f)
        for good_state in last_good_states:
            connection_id = good_state['connection_id']
            if good_state['state'] is None:
                # All the streams in this sync are full refresh (and therefore there is no state at all)
                continue
            connection_state = json.loads(good_state['state'])
            stream_conditions = []
            for state in connection_state:
                if state['type'] == 'GLOBAL':
                    global_state = state['global']
                    escaped_state = json.dumps(global_state['shared_state']).replace("'", "''")
                    output += f"UPDATE state SET state = '{escaped_state}' :: jsonb, updated_at = current_timestamp WHERE connection_id = '{connection_id}' AND namespace IS NULL AND stream_name IS NULL;\n"
                    for stream_state in global_state['stream_states']:
                        stream_condition = get_stream_condition(stream_state)
                        stream_conditions.append(stream_condition)
                else:
                    stream_state = state['stream']
                    stream_condition = get_stream_condition(stream_state)
                    escaped_state = json.dumps(stream_state['stream_state']).replace("'", "''")
                    output += f"UPDATE state SET state = '{escaped_state}' :: jsonb, updated_at = CURRENT_TIMESTAMP WHERE connection_id = '{connection_id}' AND {stream_condition};\n"
                    stream_conditions.append(stream_condition)
            stream_conditions_str = ' OR '.join(stream_conditions)
            output += f"DELETE FROM state WHERE connection_id = '{connection_id}'"
            if stream_conditions_str:
                output += f" AND NOT ({stream_conditions_str})"
            output += ";\n\n"

    print(output + 'COMMIT;')

if __name__ == '__main__':
    run()

