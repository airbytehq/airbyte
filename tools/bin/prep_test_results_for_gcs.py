import argparse
import json
import os


'''

This script is intended to be run in conjuction with https://github.com/EnricoMi/publish-unit-test-result-action to upload trimmed
test results from the output to a GCS bucket for further analysis.

The script takes as input the filename of the json output by the aforementioned action, trims it, and uploads it to GCS with a ".jsonl" filename 

'''

# Initiate the parser
parser = argparse.ArgumentParser()

# Add long and short argument
parser.add_argument("--json", "-j", help="Path to the result json output by https://github.com/EnricoMi/publish-unit-test-result-action")

def main():
    # Read arguments from the command line
    args = parser.parse_args()

    token = os.getenv('GITHUB_TOKEN')

    f = open(args.json)
    d = json.load(f)
    out = []
    
    check_run_id = int(d["check_url"].split("/")[-1])
    for elem in d['cases']:
        if 'success' in elem['states']:
            for i in range(len(elem['states']['success'])):
                output = {
                    "test_name": elem['states']['success'][i]['test_name'],
                    "class_name": elem['states']['success'][i]['class_name'],
                    "result_file": elem['states']['success'][i]['result_file'],
                    "time": elem['states']['success'][i]['time'],
                    "state": "success",
                    "check_run_id": check_run_id,
                }
                out.append(output)
        if 'failure' in elem['states']:
            for i in range(len(elem['states']['failure'])):
                output = {
                    "test_name": elem['states']['failure'][i]['test_name'],
                    "class_name": elem['states']['failure'][i]['class_name'],
                    "result_file": elem['states']['failure'][i]['result_file'],
                    "time": elem['states']['failure'][i]['time'],
                    "state": "failure",
                    "check_run_id": check_run_id,
                }
                out.append(output)
        if 'skipped' in elem['states']:
            for i in range(len(elem['states']['skipped'])):
                output = {
                    "test_name": elem['states']['skipped'][i]['test_name'],
                    "class_name": elem['states']['skipped'][i]['class_name'],
                    "result_file": elem['states']['skipped'][i]['result_file'],
                    "time": elem['states']['skipped'][i]['time'],
                    "state": "skipped",
                    "check_run_id": check_run_id,
                }
                out.append(output)

    with open(args.json + "l", 'w') as f:
        for o in out:
            json.dump(o, f)
            f.write('\n')


if __name__ == '__main__':
    main()