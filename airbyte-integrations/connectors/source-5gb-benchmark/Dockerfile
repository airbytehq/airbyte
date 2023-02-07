FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION source-5gb-benchmark

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

RUN mkdir /airbyte/seed_data
RUN gsutil cp gs://airbyte-performance-testing-public/sample-data/faker_20m/products.csv /airbyte/seed_data/

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-5gb-benchmark

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-5gb-benchmark
