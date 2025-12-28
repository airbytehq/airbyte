# Local Setup?

uv tool install poethepoet
uv tool install --upgrade 'airbyte-cdk[dev]'
airbyte-ci connectors --name destination-s3-data-lake build
poe connector destination-s3-data-lake run-cat-tests
poe get-modified-connectors
poe connector destination-s3-data-lake get-connector-name
cd /Users/prabhatika/projects/airbyte/airbyte-integrations/connectors/destination-s3-data-lake && poe install 

poe connector destination-s3-data-lake gradle build # report empty

./gradlew :airbyte-integrations:connectors:destination-s3-data-lake:build
airbyte-cdk image build destination-s3-data-lake

./gradlew :airbyte-cdk:bulk:toolkits:bulk-cdk-toolkit-load-s3:build

1. While clearing gradle cache (to build cdk), stop gradle daemon first (./gradlew --stop && rm ~/.gradle/cache).
2. Build and run publishToMavenLocal task
2. Modify cdk version used by connector.
3. 


--
./gradlew :airbyte-cdk:bulk:bulkCdkBuild

./gradlew clean :airbyte-cdk:bulk:bulkCdkBuild -x test


./gradlew :airbyte-cdk:bulk:publishToMavenLocal -x test

// decompile class
docker run -it --rm --platform linux/amd64 -v `pwd`:/mnt --user $(id -u):$(id -g) kwart/jd-cli /mnt/airbyte-cdk/bulk/toolkits/load-s3/build/libs/io.airbyte.airbyte-cdk.bulk.toolkits-bulk-cdk-toolkit-load-s3-0.1.88.jar -od /mnt/deccompiled-src

---
./gradlew :airbyte-integrations:connectors:destination-s3-data-lake:build -x test

---

./gradlew :airbyte-integrations:connectors:destination-s3-data-lake:build -x compileTestKotlin -x compileIntegrationTestKotlin
kind load docker-image airbyte/destination-s3-data-lake:dev -n airbyte-abctl

# ToDo

1. Build the project
