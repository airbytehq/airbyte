/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.s3;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperations;
import io.airbyte.cdk.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.cdk.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.cdk.integrations.destination.s3.parquet.S3ParquetWriter;
import io.airbyte.cdk.integrations.destination.s3.writer.ProductionWriterFactory;
import io.airbyte.integrations.destination.databricks.DatabricksDestinationConfig;
import io.airbyte.integrations.destination.databricks.DatabricksNameTransformer;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import org.junit.jupiter.api.Test;

import java.util.UUID;

import static io.airbyte.protocol.models.v0.CatalogHelpers.createAirbyteStream;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class DatabricksS3StreamCopierTest {

  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
  final String bucketName = UUID.randomUUID().toString();
  final String bucketPath = UUID.randomUUID().toString();
  final String bucketRegion = UUID.randomUUID().toString();
  final String stagingFolder = UUID.randomUUID().toString();

  @Test
  public void testGetStagingS3DestinationConfig() {
    final S3DestinationConfig config = S3DestinationConfig.create("", bucketPath, "").get();
    final S3DestinationConfig stagingConfig = DatabricksS3StreamCopier.getStagingS3DestinationConfig(config, stagingFolder);
    assertEquals(String.format("%s/%s", bucketPath, stagingFolder), stagingConfig.getBucketPath());
  }

  @Test
  public void testGetDestinationTablePath() {
    final String namespace = UUID.randomUUID().toString();
    final String tableName = UUID.randomUUID().toString();

    ConfiguredAirbyteStream configuredAirbyteStream = new ConfiguredAirbyteStream()
            .withStream(createAirbyteStream(tableName, namespace))
            .withSyncMode(SyncMode.FULL_REFRESH);

    final ObjectNode dataS3Config = OBJECT_MAPPER.createObjectNode()
            .put("data_source_type", "S3_STORAGE")
            .put("s3_bucket_name", bucketName)
            .put("s3_bucket_path", bucketPath)
            .put("s3_bucket_region", bucketRegion)
            .put("s3_access_key_id", "access_key_id")
            .put("s3_secret_access_key", "secret_access_key");

    final ObjectNode config = OBJECT_MAPPER.createObjectNode()
            .put("accept_terms", true)
            .put("databricks_server_hostname", "server_hostname")
            .put("databricks_http_path", "http_path")
            .put("databricks_personal_access_token", "pak")
            .set("data_source", dataS3Config);

    DatabricksDestinationConfig databricksConfig = DatabricksDestinationConfig.get(config);
    DatabricksS3StreamCopierFactory factory = new DatabricksS3StreamCopierFactory() {
      @Override
      public StreamCopier create(String configuredSchema, DatabricksDestinationConfig databricksConfig, String stagingFolder, ConfiguredAirbyteStream configuredStream, StandardNameTransformer nameTransformer, JdbcDatabase database, SqlOperations sqlOperations) {
        try {
          final AirbyteStream stream = configuredStream.getStream();
          final String catalogName = databricksConfig.catalog();
          final String schema = StreamCopierFactory.getSchema(stream.getNamespace(), configuredSchema, nameTransformer);

          S3ParquetWriter writer = mock(S3ParquetWriter.class);
          final ProductionWriterFactory writerFactory = mock(ProductionWriterFactory.class);
          when(writerFactory.create(any(), any(), any(), any())).thenReturn(writer);

          return new DatabricksS3StreamCopier(stagingFolder, catalogName, schema, configuredStream, null, null,
                  databricksConfig, nameTransformer, null, writerFactory, null);
        } catch (final Exception e) {
          throw new RuntimeException(e);
        }
      }
    };

    final StandardNameTransformer nameTransformer = new DatabricksNameTransformer();
    DatabricksS3StreamCopier streamCopier = (DatabricksS3StreamCopier) factory.create(databricksConfig.schema(), databricksConfig, stagingFolder, configuredAirbyteStream, nameTransformer, null, null);
    assertEquals(String.format("s3://%s/%s/%s/%s", bucketName, bucketPath, nameTransformer.getNamespace(namespace), tableName), streamCopier.getDestTableLocation());
  }

}