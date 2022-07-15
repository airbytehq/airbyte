# Step 2: Install dependencies

Let's create a python virtual environment for our source.


```
cd $AIRBYTE_ROOT
python tools/bin/update_intellij_venv.py -modules source-exchange-rates-tutorial --install-venv
cd airbyte-integrations/connectors/source-exchange-rates-tutorial
source .venv/bin/activate
```
These steps create an initial python environment, and install the dependencies required to run an API Source connector.

Let's verify everything works as expected by running the Airbyte `spec` command: #FIXME: There should be a link to the spec doc
```
python main.py spec

```

You should see an output similar to the one below:
```
{"type": "SPEC", "spec": {"documentationUrl": "https://docsurl.com", "connectionSpecification": {"$schema": "http://json-schema.org/draft-07/schema#", "title": "Python Http Tutorial Spec", "type": "object", "required": ["TODO"], "additionalProperties": false, "properties": {"TODO: This schema defines the configuration required for the source. This usually involves metadata such as database and/or authentication information.": {"type": "string", "description": "describe me"}}}}}
```

We'll come back to what the `spec` command does later on.
For now, note that the `main.py` file is a convenience wrapper to help run the connector.
Its invocation format is `python main.py <command> [args]`.
The module's generated `README.md` contains more details on the supported commands.



### Note to self: I'm skipping the dependencies and dev env parts here because I wouldn't expect a typical config-base developer to need additional dependencies.
### Note to self: same for iterating on your implementation. I think i'll just point to the python base for simplicity. running with the docker image can be briefly mentioned. or not.
### Note to self: maybe just need to point to https://docs.airbyte.com/connector-developmt/cdk-tutorial-python-http/install-dependencies#iterating-on-your-implementation

## Next steps
Next, we'll [connect to the API source](./3-connecting.md)