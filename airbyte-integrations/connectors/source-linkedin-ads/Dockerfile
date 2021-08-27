FROM python:3.7.11-alpine3.14 as base

# build and load all requirements 
FROM base as builder
WORKDIR /airbyte/integration_code

# upgrade pip to the latest version
RUN apk --no-cache upgrade && pip install --upgrade pip

COPY setup.py ./
# install necessary packages to a temporary folder 
RUN pip install --prefix=/install .

# build a clean environment  
FROM base
WORKDIR /airbyte/integration_code

# copy all loaded and built libraries to a pure basic image
COPY --from=builder /install /usr/local

# copy payload code only
COPY main.py ./
COPY source_linkedin_ads ./source_linkedin_ads

# set the default Timezone, for use with dependent libraries like: datetime, pendullum, etc.
ENV TZ "UTC"
ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-linkedin-ads
