/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.integrations.destination.snowflake.SnowflakeS3StagingDestination.isPurgeStagingData;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.storage.BlobId;
import com.google.cloud.storage.BlobInfo;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsConfig;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.s3.csv.CsvSerializedBuffer;
import io.airbyte.integrations.destination.staging.StagingConsumerFactory;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.Map;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeGcsStagingDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeGcsStagingDestination.class);
  private String airbyteEnvironment;

  public SnowflakeGcsStagingDestination(final String airbyteEnvironment) {
    this(new SnowflakeSQLNameTransformer(), airbyteEnvironment);
  }

  public SnowflakeGcsStagingDestination(final SnowflakeSQLNameTransformer nameTransformer, final String airbyteEnvironment) {
    super("", nameTransformer, new SnowflakeSqlOperations());
    this.airbyteEnvironment = airbyteEnvironment;
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    GcsConfig gcsConfig = GcsConfig.getGcsConfig(config);
    final NamingConventionTransformer nameTransformer = getNamingResolver();
    final SnowflakeGcsStagingSqlOperations snowflakeGcsStagingSqlOperations =
        new SnowflakeGcsStagingSqlOperations(nameTransformer, gcsConfig);
    final DataSource dataSource = getDataSource(config);

    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final String outputSchema = super.getNamingResolver().getIdentifier(config.get("schema").asText());

      attemptTableOperations(outputSchema, database, nameTransformer, snowflakeGcsStagingSqlOperations,
          true);
      attemptWriteAndDeleteGcsObject(gcsConfig, outputSchema);

      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    } finally {
      try {
        DataSourceFactory.close(dataSource);
      } catch (final Exception e) {
        LOGGER.warn("Unable to close data source.", e);
      }
    }
  }

  private static void attemptWriteAndDeleteGcsObject(final GcsConfig gcsConfig, final String outputTableName) throws IOException {
    final var storage = getStorageClient(gcsConfig);
    final var blobId = BlobId.of(gcsConfig.getBucketName(), "check-content/" + outputTableName);
    final var blobInfo = BlobInfo.newBuilder(blobId).build();

    storage.create(blobInfo, "".getBytes(StandardCharsets.UTF_8));
    storage.delete(blobId);
  }

  public static Storage getStorageClient(final GcsConfig gcsConfig) throws IOException {
    final InputStream credentialsInputStream = new ByteArrayInputStream(gcsConfig.getCredentialsJson().getBytes(StandardCharsets.UTF_8));
    final GoogleCredentials credentials = GoogleCredentials.fromStream(credentialsInputStream);
    return StorageOptions.newBuilder()
        .setCredentials(credentials)
        .setProjectId(gcsConfig.getProjectId())
        .build()
        .getService();
  }

  @Override
  protected DataSource getDataSource(final JsonNode config) {
    return SnowflakeDatabase.createDataSource(config, airbyteEnvironment);
  }

  @Override
  protected JdbcDatabase getDatabase(final DataSource dataSource) {
    return SnowflakeDatabase.getDatabase(dataSource);
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(JsonNode config) {
    return Collections.emptyMap();
  }

  // this is a no op since we override getDatabase.
  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    return Jsons.emptyObject();
  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog catalog,
                                            Consumer<AirbyteMessage> outputRecordCollector) {
    GcsConfig gcsConfig = GcsConfig.getGcsConfig(config);
    return new StagingConsumerFactory().create(
        outputRecordCollector,
        getDatabase(getDataSource(config)),
        new SnowflakeGcsStagingSqlOperations(getNamingResolver(), gcsConfig),
        getNamingResolver(),
        CsvSerializedBuffer.createFunction(null, () -> new FileBuffer(CsvSerializedBuffer.CSV_GZ_SUFFIX)),
        config,
        catalog,
        isPurgeStagingData(config));

  }

}
