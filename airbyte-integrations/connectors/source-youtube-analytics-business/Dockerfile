FROM airbyte/source-youtube-analytics:0.1.3

WORKDIR /airbyte/integration_code
COPY source_youtube_analytics_business ./source_youtube_analytics_business
COPY main.py ./
COPY setup.py ./
RUN pip install .

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-youtube-analytics-business
