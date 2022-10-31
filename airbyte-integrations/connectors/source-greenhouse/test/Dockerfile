FROM airbyte/source-greenhouse:dev

RUN pip uninstall -y airbyte_cdk

COPY ./airbyte-cdk/python ./cdk
RUN pip install -e ./cdk