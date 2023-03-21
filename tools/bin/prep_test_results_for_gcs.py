import argparse
import json
import os


'''

This script is intended to be run in conjuction with https://github.com/EnricoMi/publish-unit-test-result-action to upload trimmed
test results from the output to a GCS bucket for further analysis.

The script takes as input the filename of the json output by the aforementioned action, trims it, and writes it out in jsonl format with ".jsonl" filename 

'''

# Initiate the parser
parser = argparse.ArgumentParser()

# Add long and short argument
parser.add_argument("--json", "-j", help="Path to the result json output by https://github.com/EnricoMi/publish-unit-test-result-action")
parser.add_argument("--runid", "-r", help="Run id of the action") # this can be derived from checks api, but it's easier to derive it here
parser.add_argument("--jobid", "-c", help="Job id of the action") # this can be derived from checks api, but it's easier to derive it here

def main():
    # Read arguments from the command line
    args = parser.parse_args()

    f = open(args.json)
    d = json.load(f)
    out = []
    
    check_run_id = int(d["check_url"].split("/")[-1])

    for elem in d['cases']:
        for conclusion in ('success', 'failure', 'skipped'):
            if conclusion not in elem['states']: 
                continue
            for i in range(len(elem['states'][conclusion])):
                output = {
                    "test_name": elem['states'][conclusion][i]['test_name'],
                    "class_name": elem['states'][conclusion][i]['class_name'],
                    "result_file": elem['states'][conclusion][i]['result_file'],
                    "time": elem['states'][conclusion][i]['time'],
                    "state": conclusion,
                    "check_run_id": check_run_id,
                    "workflow_run_id": args.runid,
                    "job_id": args.jobid,
                    "repo": "airbytehq/airbyte"
                }
                out.append(output)

    with open(args.json + "l", 'w') as f:
        for o in out:
            json.dump(o, f)
            f.write('\n')


if __name__ == '__main__':
    main()