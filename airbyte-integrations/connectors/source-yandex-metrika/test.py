import json


with open('exh.json', 'r') as f:
    with open('exh2.json', 'w') as f1:
        is_inside_records_batch = False
        current_records_batch_count = 0
        for l_n, l in enumerate(f):
            try:
                l_data = json.loads(l)
                if l_data['type'] == 'RECORD':
                    current_records_batch_count += 1
                    is_inside_records_batch = True
                else:
                    if is_inside_records_batch:
                        is_inside_records_batch = False
                        f1.write(f'Read {current_records_batch_count} records')
                        current_records_batch_count = 0
                    f1.write(l)
            except:
                if is_inside_records_batch:
                    is_inside_records_batch = False
                    f1.write(f'Read {current_records_batch_count} records')
                    current_records_batch_count = 0
                f1.write(l)