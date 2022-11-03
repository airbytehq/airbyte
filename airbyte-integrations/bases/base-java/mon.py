import json
import time

path = '/dpi.log'
alert_path = '/hack_alert'
def check():
    print("check")
    with open(path, 'r') as dpi_file:
        dpi_lines = dpi_file.readlines()
        for line in dpi_lines:
            print(f"line: {line}")
            dpi_data = json.loads(line)
            # print(f'prot {dpi_data["l7_protocol_id"]} {dpi_data["l7_protocol_name"]} enc {dpi_data["encrypted"]}')
            # if (int(dpi_data["ndpi"]["proto_id"]) in [7, 19, 20] and bool(dpi_data["ndpi"]["encrypted"]) == False and "6" in dpi_data["ndpi"]["confidence"]):
            if ( int(dpi_data["ndpi"]["proto_id"]) in [0] and bool(dpi_data["ndpi"]["encrypted"]) == False ):
                print("alert")
                with open(alert_path, 'w') as creating_new_csv_file:
                    pass
                print('Done')
                exit(0)

try:
#     time.sleep(3)
#     while True:
    check()
        # time.sleep(3)
except Exception as exp:
#     print(f"Error: {exp}")
    pass
