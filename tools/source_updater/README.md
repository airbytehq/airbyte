# Source update
CLI tooling to update the repository following a change in a low-code source. 

## Set up

### Install dependencies
```
cd tools/source_updater
python -m venv .venv
source .venv/bin/activate
python -m pip install .
cd ../..
```

### GSM setup
This script will update the source secrets in GSM. In order to allow that, please setup your GSM key following the `tools/ci_credentials/README.md` file.

### Git
This script will run git commands which means you should be able to run commands like `git checkout -b <branch>`

## Usage
Now that all the dependencies are installed, change directory to be at the root of your local airbyte repository and run:
`python tools/source_updater/updater/main.py --source <source-name> --manifest <new manifest path> --config <new config file> --debug`

For more information about the parameters, you can run `python tools/source_updater/updater/main.py --help`:
```
(.venv) airbyte% python tools/source_updater/updater/main.py --help
usage: main.py [-h] --source SOURCE --manifest MANIFEST [--debug]

Source updated

optional arguments:
  -h, --help           show this help message and exit
  --source SOURCE      Name of the source. For example, 'source-jira'
  --manifest MANIFEST  Path to the new yaml manifest file
  --debug              Enable debug logs
```
