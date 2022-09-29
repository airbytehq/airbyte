/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iomete;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest;
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
import java.io.IOException;
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

import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.field;

public class IometeDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(IometeDestinationAcceptanceTest.class);

  private static final String SECRETS_CONFIG_JSON = "secrets/config.json";

  private final ExtendedNameTransformer nameTransformer = new IometeNameTransformer();
  private JsonNode configJson;
  private IometeDestinationConfig iometeConfig;
  private S3DestinationConfig s3Config;
  private AmazonS3 s3Client;

  @Override
  protected String getImageName() {
    return "airbyte/destination-iomete:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return configJson;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode failCheckJson = Jsons.clone(configJson);

    ((ObjectNode) failCheckJson.get("staging"))
            .put("s3_access_key_id", "fake_key")
            .put("s3_secret_access_key", "fake-secret");
    return failCheckJson;
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
          throws SQLException {
    final String tableName = nameTransformer.getIdentifier(streamName);
    final String schemaName = StreamCopierFactory.getSchema(namespace, iometeConfig.getDatabaseSchema(), nameTransformer);
    final JsonFieldNameUpdater nameUpdater = AvroRecordHelper.getFieldNameUpdater(streamName, namespace, streamSchema);

    try (final DSLContext dslContext = getDslContext(iometeConfig)) {
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
  protected void setup(TestDestinationEnv testEnv) {
    final JsonNode baseConfigJson = Jsons.deserialize(IOs.readFile(Path.of(SECRETS_CONFIG_JSON)));

    // Set a random s3 bucket path and database schema for each integration test
    final String randomString = RandomStringUtils.randomAlphanumeric(5);
    final JsonNode configJson = Jsons.clone(baseConfigJson);
    ((ObjectNode) configJson).put("database_schema", "integration_test_" + randomString);
    final JsonNode staging = configJson.get("staging");
    ((ObjectNode) staging).put("s3_bucket_path", "test_" + randomString);

    this.configJson = configJson;
    this.iometeConfig = IometeDestinationConfig.get(configJson);
    this.s3Config = iometeConfig.getS3DestinationConfig();
    LOGGER.info("Test full path: s3://{}/{}", s3Config.getBucketName(), s3Config.getBucketPath());

    this.s3Client = s3Config.getS3Client();
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws SQLException {
    // clean up s3
    final List<DeleteObjectsRequest.KeyVersion> keysToDelete = new LinkedList<>();
    final List<S3ObjectSummary> objects = s3Client
            .listObjects(s3Config.getBucketName(), s3Config.getBucketPath())
            .getObjectSummaries();
    for (final S3ObjectSummary object : objects) {
      keysToDelete.add(new DeleteObjectsRequest.KeyVersion(object.getKey()));
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
    LOGGER.info("Dropping database schema {}", iometeConfig.getDatabaseSchema());
    try (final DSLContext dslContext = getDslContext(iometeConfig)) {
      final Database database = new Database(dslContext);
      // we cannot use jooq dropSchemaIfExists method here because there is no proper dialect for
      // Databricks, and it incorrectly quotes the schema name
      database.query(ctx -> ctx.execute(String.format("DROP SCHEMA IF EXISTS %s CASCADE;", iometeConfig.getDatabaseSchema())));
    } catch (final Exception e) {
      throw new SQLException(e);
    }
  }

  private static DSLContext getDslContext(final IometeDestinationConfig iometeConfig) {
    return DSLContextFactory.create(iometeConfig.getIometeUsername(),
            iometeConfig.getIometePassword(), IometeConstants.IOMETE_DRIVER_CLASS,
            IometeDestination.getIometeConnectionString(iometeConfig), SQLDialect.DEFAULT);
  }

}
