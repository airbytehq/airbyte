### How to Start Nessie Server with Keycloak and Test Against It

#### 1. Start the Nessie Server
- Navigate to the `nessie-server-startup` directory:
  ```bash
  cd nessie-server-startup
  ```
- Start the Nessie server and other dependencies with Docker:
  ```bash
  docker-compose up
  ```

#### 2. Obtain an Access Token
- Once the containers are up and running, retrieve a Keycloak access token:
  ```bash
  curl http://127.0.0.1:8080/realms/iceberg/protocol/openid-connect/token \
  --user client1:s3cr3t \
  -d 'grant_type=client_credentials' \
  -d 'scope=profile' | jq -r .access_token
  ```
- Copy the resulting token for the next step.

#### 3. Update the Test Class with the Token
- Open the test class [IcebergWithNessieExample.kt](src/test/kotlin/io/airbyte/integrations/destination/iceberg/v2/IcebergWithNessieExample.kt).
- In the `getToken()` method, replace the token value with the token obtained in step 2.

#### 4. Run Tests to Validate Data Writing
- Execute the `test()` in [IcebergWithNessieExample.kt](src/test/kotlin/io/airbyte/integrations/destination/iceberg/v2/IcebergWithNessieExample.kt) to verify data is written correctly.
- After running the test, confirm the data in the MinIO bucket:
    - Access MinIO via the UI at [http://localhost:9092](http://localhost:9092)
    - Login credentials: **Username**: `minioadmin`, **Password**: `minioadmin`

#### 5. Install Apache Spark
- Install Apache Spark via Homebrew:
  ```bash
  brew install apache-spark
  ```

#### 6. Configure and Run Spark-SQL with Nessie and Iceberg
- Launch Spark-SQL with the required Nessie and Iceberg packages:
  ```bash
  spark-sql \
  --packages "org.projectnessie.nessie-integrations:nessie-spark-extensions-3.5_2.12:0.100.0,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2,org.apache.iceberg:iceberg-aws-bundle:1.5.2" \
  --conf spark.sql.catalog.nessie=org.apache.iceberg.spark.SparkCatalog \
  --conf spark.sql.catalog.nessie.catalog-impl=org.apache.iceberg.nessie.NessieCatalog \
  --conf spark.sql.catalog.nessie.uri=http://127.0.0.1:19120/api/v1 \
  --conf spark.sql.catalog.nessie.ref=main \
  --conf spark.sql.catalog.nessie.warehouse=s3://demobucket/ \
  --conf spark.sql.catalog.nessie.authentication.type=OAUTH2 \
  --conf spark.sql.catalog.nessie.authentication.oauth2.client-id=client1 \
  --conf spark.sql.catalog.nessie.authentication.oauth2.client-secret=s3cr3t \
  --conf spark.sql.catalog.nessie.authentication.oauth2.token-endpoint=http://127.0.0.1:8080/realms/iceberg/protocol/openid-connect/token \
  --conf spark.sql.catalog.nessie.authentication.oauth2.scope=profile \
  --conf spark.sql.catalog.nessie.io-impl=org.apache.iceberg.aws.s3.S3FileIO \
  --conf spark.sql.catalog.nessie.s3.endpoint=http://127.0.0.1:9002 \
  --conf spark.sql.catalog.nessie.s3.access-key-id=minioadmin \
  --conf spark.sql.catalog.nessie.s3.secret-access-key=minioadmin \
  --conf spark.sql.catalog.nessie.s3.path-style-access=true \
  --conf spark.sql.catalog.nessie.s3.connection.ssl.enabled=false \
  --conf spark.sql.extensions=org.projectnessie.spark.extensions.NessieSparkSessionExtensions,org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
  ```

#### 7. Run SQL Commands in Spark-SQL CLI
- Inside the Spark-SQL CLI:
    - Set the catalog:
      ```sql
      USE nessie.default;
      ```
    - Show tables:
      ```sql
      SHOW TABLES;
      ```
        - You should see `my_table` listed.
    - Query the table:
      ```sql
      SELECT * FROM my_table;
      ```
        - Expected output:
          ```
          +---+-----+
          | id| name|
          +---+-----+
          |  1|  foo|
          |  2|  bar|
          +---+-----+
          Time taken: 0.168 seconds, Fetched 2 row(s)
          ```

#### 8. Experiment with Data in IcebergWithNessieExample.kt
- Modify the [IcebergWithNessieExample.kt](src/test/kotlin/io/airbyte/integrations/destination/iceberg/v2/IcebergWithNessieExample.kt) class to write, update, or delete data.
- Confirm the changes in Spark SQL by rerunning queries, which should reflect the updates.