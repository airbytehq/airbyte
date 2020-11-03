FROM fishtownanalytics/dbt:0.18.1
COPY --from=airbyte/base-airbyte-protocol-python:dev /airbyte /airbyte

WORKDIR /airbyte
COPY entrypoint.sh .
COPY normalization ./normalization_code/normalization
COPY setup.py ./normalization_code
# we need to install airbyte protocol structs manually since we copied them from their container but did not inherit the container.
# todo (cgardens) - find a better way of doing pip install that doesn't involve cd-ing to the directory.
WORKDIR /airbyte/base_python_structs
RUN pip install .
WORKDIR /airbyte/normalization_code
RUN pip install .
WORKDIR /airbyte

ENTRYPOINT ["/airbyte/entrypoint.sh"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/normalization
