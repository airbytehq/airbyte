# Migration guide for 

Basic outline of changes for each module:

1. Update `setup.py` to pull airbyte-cdk and remove legacy packages
2. rename `main_dev.py` to `main.py` 
3. add `main.py` to `.dockerignore` with the inclusion pattern `!main.py`
4. Update Dockerfile to inherit python docker image directly, remove dead code, and use main.py as entrypoint
5. Remove `requirements.txt`
6. Update imports in python code to use the new CDK package. No code has been removed, only reorganized, so this be as simple as removing all imports from `base_python`, `base_singer`, and `airbyte_protocol` and using the appropriate import paths from the CDK. 

## Example
See this PR for an example of migrating a module to the new CDK structure: https://github.com/airbytehq/airbyte/pull/3302
