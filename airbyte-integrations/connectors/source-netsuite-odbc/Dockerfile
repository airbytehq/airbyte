FROM airbyte/python-connector-base:1.1.0

COPY . ./airbyte/integration_code
COPY ./NetsuiteLinux64ODBC /opt/netsuite/odbcclient
RUN ["chmod", "+x", "/opt/netsuite/odbcclient/oaodbc64.csh"]
RUN ["chmod", "+x", "/opt/netsuite/odbcclient/oaodbc64.sh"]
RUN ["chmod", "777", "/opt/netsuite/odbcclient/cert/ca3.cer"]
RUN apt-get update && apt-get install -y unixodbc && apt-get install -y odbcinst

RUN pip install ./airbyte/integration_code

ENV LD_LIBRARY_PATH /opt/netsuite/odbcclient/lib64
ENV OASDK_ODBC_HOME /opt/netsuite/odbcclient/lib64
ENV ODBCINI /opt/netsuite/odbcclient/odbc64.ini

RUN odbcinst -i -d -f /opt/netsuite/odbcclient/odbcinst.ini

# The entrypoint and default env vars are already set in the base image
ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-netsuite-odbc