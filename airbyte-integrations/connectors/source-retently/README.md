## [Quickrun](https://docs.airbyte.io/connector-development/tutorials/cdk-speedrun)

1. `python -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt` (Alter path in requirements.txt)
4. `python main.py check --config sample_files/config.json` should report SUCCESS
5. `python main.py check --config sample_files/invalid_config.json` should report FAILED
6. `python main.py discover --config sample_files/config.json` presents schema
7. `python main.py read --config sample_files/config.json --catalog sample_files/configured_catalog.json` runs source
8. `docker build . -t <repo>/source-retently:<n>` builds docker image
10. `docker push <repo>/source-retently:<n>` .. and push 
11. Add connector from http://localhost:8000/settings/source
12. `pip install .[tests]`
13. `python -m pytest unit_tests`
14. `python -m pytest integration_tests`
15. `python -m pytest integration_tests -p integration_tests.acceptance`

