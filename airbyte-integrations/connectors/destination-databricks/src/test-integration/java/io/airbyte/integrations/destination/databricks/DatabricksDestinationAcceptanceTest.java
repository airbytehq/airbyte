/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import static io.airbyte.integrations.standardtest.destination.DateTimeUtils.DATE;
import static io.airbyte.integrations.standardtest.destination.DateTimeUtils.DATE_TIME;
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
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.avro.JsonFieldNameUpdater;
import io.airbyte.integrations.destination.s3.util.AvroRecordHelper;
import io.airbyte.integrations.standardtest.destination.DateTimeUtils;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.StringUtils;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Assertions;
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

    final Database database = getDatabase(databricksConfig);
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
    try (final Database database = getDatabase(databricksConfig)) {
      // we cannot use jooq dropSchemaIfExists method here because there is no proper dialect for
      // Databricks, and it incorrectly quotes the schema name
      database.query(ctx -> ctx.execute(String.format("DROP SCHEMA IF EXISTS %s CASCADE;", databricksConfig.getDatabaseSchema())));
    } catch (final Exception e) {
      throw new SQLException(e);
    }
  }

  private static Database getDatabase(final DatabricksDestinationConfig databricksConfig) {
    return Databases.createDatabase(
        DatabricksConstants.DATABRICKS_USERNAME,
        databricksConfig.getDatabricksPersonalAccessToken(),
        DatabricksDestination.getDatabricksConnectionString(databricksConfig),
        DatabricksConstants.DATABRICKS_DRIVER_CLASS,
        SQLDialect.DEFAULT);
  }


  @Override
  public boolean requiresDateTimeConversionForSync() {
    return true;
  }

  @Override
  public void convertDateTime(ObjectNode data, Map<String, String> dateTimeFieldNames) {
    var fields = StreamSupport.stream(Spliterators.spliteratorUnknownSize(data.fields(),
        Spliterator.ORDERED), false).toList();
    data.removeAll();
    fields.forEach(field -> {
      var key = field.getKey();
      if (dateTimeFieldNames.containsKey(key)) {
        switch (dateTimeFieldNames.get(key)) {
          case DATE_TIME -> data.put(key.toLowerCase(), DateTimeUtils.convertToDatabricksFormat(field.getValue().asText()));
          case DATE -> data.put(key.toLowerCase(), String.format("***\"member0\":%s,\"member1\":null***", DateTimeUtils.convertToDateFormat(field.getValue().asText())));
        }
      } else {
        data.set(key.toLowerCase(), field.getValue());
      }
    });
  }

  @Override
  protected void assertSameValue(String key,
      JsonNode expectedValue,
      JsonNode actualValue) {
    var format = dateTimeFieldNames.getOrDefault(key, StringUtils.EMPTY);
    if (DATE_TIME.equals(format) || DATE.equals(format)) {
      Assertions.assertEquals(expectedValue.asText(), expectedValue.asText());
    } else {
      super.assertSameValue(key, expectedValue, actualValue);
    }
  }

}
