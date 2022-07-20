# Config Models

This module uses `jsonschema2pojo` to generate Java config objects from [json schema](https://json-schema.org/) definitions. See [build.gradle](./build.gradle) for details.

## How to use
- Update json schema under:
  ```
  src/main/resources/types/
  ```
- Run the following command under the project root:
  ```sh
  SUB_BUILD=PLATFORM ./gradlew airbyte-config:config-models:generateJsonSchema2Pojo
  ```
  The generated file is under:
  ```
  build/generated/src/gen/java/io/airbyte/config/
  ```

## Reference
- [`jsonschema2pojo` plugin](https://github.com/joelittlejohn/jsonschema2pojo/tree/master/jsonschema2pojo-gradle-plugin).
