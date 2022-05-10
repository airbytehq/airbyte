/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.field;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest;
import com.amazonaws.services.s3.model.DeleteObjectsRequest.KeyVersion;
import com.amazonaws.services.s3.model.DeleteObjectsResult;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.avro.JsonFieldNameUpdater;
import io.airbyte.integrations.destination.s3.util.AvroRecordHelper;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.LinkedList;
import java.util.List;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabricksDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksDestinationAcceptanceTest.class);
  private static final String SECRETS_CONFIG_JSON = "secrets/config.json";

  private final ExtendedNameTransformer nameTransformer = new DatabricksNameTransformer();
  private JsonNode configJson;
  private DatabricksDestinationConfig databricksConfig;
  private S3DestinationConfig s3Config;
  private AmazonS3 s3Client;

  @Override
  protected String getImageName() {
    return "airbyte/destination-databricks:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return configJson;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode failCheckJson = Jsons.clone(configJson);
    // set invalid credential
    ((ObjectNode) failCheckJson.get("data_source"))
        .put("s3_access_key_id", "fake-key")
        .put("s3_secret_access_key", "fake-secret");
    return failCheckJson;
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws SQLException {
    final String tableName = nameTransformer.getIdentifier(streamName);
    final String schemaName = StreamCopierFactory.getSchema(namespace, databricksConfig.getDatabaseSchema(), nameTransformer);
    final JsonFieldNameUpdater nameUpdater = AvroRecordHelper.getFieldNameUpdater(streamName, namespace, streamSchema);

    try (final DSLContext dslContext = DSLContextFactory.create(DatabricksConstants.DATABRICKS_USERNAME,
        databricksConfig.getDatabricksPersonalAccessToken(), DatabricksConstants.DATABRICKS_DRIVER_CLASS,
        DatabricksDestination.getDatabricksConnectionString(databricksConfig), SQLDialect.DEFAULT)) {
      final Database database = new Database(dslContext);
      return database.query(ctx -> ctx.select(asterisk())
          .from(String.format("%s.%s", schemaName, tableName))
          .orderBy(field(JavaBaseConstants.COLUMN_NAME_EMITTED_AT).asc())
          .fetch().stream()
          .map(record -> {
            final JsonNode json = Jsons.deserialize(record.formatJSON(JdbcUtils.getDefaultJSONFormat()));
            final JsonNode jsonWithOriginalFields = nameUpdater.getJsonWithOriginalFieldNames(json);
            return AvroRecordHelper.pruneAirbyteJson(jsonWithOriginalFields);
          })
          .collect(Collectors.toList()));
    }
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    final JsonNode baseConfigJson = Jsons.deserialize(IOs.readFile(Path.of(SECRETS_CONFIG_JSON)));

    // Set a random s3 bucket path and database schema for each integration test
    final String randomString = RandomStringUtils.randomAlphanumeric(5);
    final JsonNode configJson = Jsons.clone(baseConfigJson);
    ((ObjectNode) configJson).put("database_schema", "integration_test_" + randomString);
    final JsonNode dataSource = configJson.get("data_source");
    ((ObjectNode) dataSource).put("s3_bucket_path", "test_" + randomString);

    this.configJson = configJson;
    this.databricksConfig = DatabricksDestinationConfig.get(configJson);
    this.s3Config = databricksConfig.getS3DestinationConfig();
    LOGGER.info("Test full path: s3://{}/{}", s3Config.getBucketName(), s3Config.getBucketPath());

    this.s3Client = s3Config.getS3Client();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws SQLException {
    // clean up s3
    final List<KeyVersion> keysToDelete = new LinkedList<>();
    final List<S3ObjectSummary> objects = s3Client
        .listObjects(s3Config.getBucketName(), s3Config.getBucketPath())
        .getObjectSummaries();
    for (final S3ObjectSummary object : objects) {
      keysToDelete.add(new KeyVersion(object.getKey()));
    }

    if (keysToDelete.size() > 0) {
      LOGGER.info("Tearing down test bucket path: {}/{}", s3Config.getBucketName(),
          s3Config.getBucketPath());
      final DeleteObjectsResult result = s3Client
          .deleteObjects(new DeleteObjectsRequest(s3Config.getBucketName()).withKeys(keysToDelete));
      LOGGER.info("Deleted {} file(s).", result.getDeletedObjects().size());
    }
    s3Client.shutdown();

    // clean up database
    LOGGER.info("Dropping database schema {}", databricksConfig.getDatabaseSchema());
    try (final DSLContext dslContext = DSLContextFactory.create(DatabricksConstants.DATABRICKS_USERNAME,
        databricksConfig.getDatabricksPersonalAccessToken(), DatabricksConstants.DATABRICKS_DRIVER_CLASS,
        DatabricksDestination.getDatabricksConnectionString(databricksConfig), SQLDialect.DEFAULT)) {
      final Database database = new Database(dslContext);
      // we cannot use jooq dropSchemaIfExists method here because there is no proper dialect for
      // Databricks, and it incorrectly quotes the schema name
      database.query(ctx -> ctx.execute(String.format("DROP SCHEMA IF EXISTS %s CASCADE;", databricksConfig.getDatabaseSchema())));
    } catch (final Exception e) {
      throw new SQLException(e);
    }
  }
}
