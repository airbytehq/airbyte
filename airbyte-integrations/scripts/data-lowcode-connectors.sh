#!/bin/bash

set -e

if [[ `git status --porcelain` ]]; then
  # everything is not up to date!
  echo ""
  echo "ERROR: There are changes left to commit!"
  echo ""
  exit 1
fi

BRANCH_NAME="$(git symbolic-ref HEAD 2>/dev/null)" ||
BRANCH_NAME="(unnamed branch)"     # detached HEAD
BRANCH_NAME=${BRANCH_NAME##refs/heads/}

OUTPUT_FILE="num_lowcode_connectors.csv"
echo "date,num_lowcode_connectors,num_python_connectors" > $OUTPUT_FILE

# get every date between sep 1 and today (so we can keep consistent results when generating this sheet)
dates=$(python << EOM 
from datetime import date, timedelta

start_date = date(2022, 10, 1)
end_date = date.today()
delta = timedelta(days=1)
results = []
while start_date <= end_date:
    results.append(start_date.strftime("%Y-%m-%d"))
    start_date += delta

print(" ".join(results))
EOM
)

for d in $dates
do
git checkout $(git rev-list -n 1 --first-parent --before="$d" master)

# count how many lowcode connectors there are

num_lowcode=$(python << EOM
import os

connectors = [f.path for f in os.scandir("airbyte-integrations/connectors/") if f.is_dir()]
declarative_connectors = []
num_python_connectors = 0
connectors_file = "lowcode_connector_names.txt"
open(connectors_file, "w").write("")
for full_path in connectors:
    files = os.listdir(full_path)
    connector_name = full_path.split("/")[-1]
    # clear the file so the last day is the only one that writes to it 
    python_files = [x for x in files if ".py" in x]
    if len(python_files) > 0:
        sourcepy_dir = f"{full_path}/{connector_name.replace('-','_')}/source.py"
        try:
            sourcepy = open(sourcepy_dir, "r").read()
            if "declarative YAML" in sourcepy:
                declarative_connectors.append(full_path)
                open(connectors_file, "a").write(connector_name + "\n")
            else:
                num_python_connectors += 1
        except FileNotFoundError: 
            pass
            #print(f"Couldn't find a source.py in {sourcepy_dir}. Skipping.")
print(f"{len(declarative_connectors)},{num_python_connectors}")
EOM
)

# print with date
echo $d,$num_lowcode >> $OUTPUT_FILE
done



git checkout $BRANCH_NAME
git checkout -- .

#uncomment to upload to GCS 
#gcloud storage cp num_lowcode_connectors.csv gs://sherif-airbyte-metabase-backing-bucket/