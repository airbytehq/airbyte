/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.InitiateMultipartUploadRequest;
import com.amazonaws.services.s3.model.InitiateMultipartUploadResult;
import com.amazonaws.services.s3.model.UploadPartRequest;
import com.amazonaws.services.s3.model.UploadPartResult;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfig;
import io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfigFactory;
import io.airbyte.integrations.destination.iceberg.config.catalog.RESTCatalogConfig;
import io.airbyte.integrations.destination.iceberg.config.format.FormatConfig;
import io.airbyte.integrations.destination.iceberg.config.storage.S3Config;
import io.airbyte.integrations.destination.iceberg.config.storage.credential.S3AccessKeyCredentialConfig;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import lombok.extern.slf4j.Slf4j;
import org.apache.hadoop.fs.s3a.S3AFileSystem;
import org.apache.iceberg.Table;
import org.apache.iceberg.TableScan;
import org.apache.iceberg.aws.s3.S3FileIO;
import org.apache.iceberg.catalog.Catalog;
import org.apache.iceberg.data.IcebergGenerics;
import org.apache.iceberg.data.IcebergGenerics.ScanBuilder;
import org.apache.iceberg.rest.RESTCatalog;
import org.apache.iceberg.spark.SparkCatalog;
import org.jetbrains.annotations.NotNull;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;

import java.util.Map;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.FORMAT_TYPE_CONFIG_KEY;
import static java.util.Map.entry;
import static java.util.Map.ofEntries;
import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockStatic;
import static org.mockito.Mockito.when;

@Slf4j
class IcebergRESTCatalogConfigTest
{

  private static final String FAKE_WAREHOUSE_URI = "s3://fake-bucket";
  private static final String FAKE_ENDPOINT = "fake-endpoint";
  private static final String FAKE_ENDPOINT_WITH_SCHEMA = "https://fake-endpoint";
  private static final String FAKE_ACCESS_KEY_ID = "fake-accessKeyId";
  private static final String FAKE_SECRET_ACCESS_KEY = "fake-secretAccessKey";
  private static final String FAKE_REST_URI = "http://fake-rest-uri";
  private static MockedStatic<IcebergGenerics> mockedIcebergGenerics;

  private AmazonS3 s3;
  private RESTCatalogConfig config;
  private Catalog catalog;
  private IcebergCatalogConfigFactory factory;

  @BeforeAll
  static void staticSetup() {
    IcebergRESTCatalogConfigTest.mockedIcebergGenerics = mockStatic(IcebergGenerics.class);
  }

  @AfterAll
  static void staticStop() {
    IcebergRESTCatalogConfigTest.mockedIcebergGenerics.close();
  }

  @BeforeEach
  void setup() {
    s3 = mock(AmazonS3.class);
    final InitiateMultipartUploadResult uploadResult = mock(InitiateMultipartUploadResult.class);
    final UploadPartResult uploadPartResult = mock(UploadPartResult.class);
    when(s3.uploadPart(any(UploadPartRequest.class))).thenReturn(uploadPartResult);
    when(s3.initiateMultipartUpload(any(InitiateMultipartUploadRequest.class))).thenReturn(uploadResult);

    TableScan tableScan = mock(TableScan.class);
    when(tableScan.schema()).thenReturn(null);
    Table tempTable = mock(Table.class);
    when(tempTable.newScan()).thenReturn(tableScan);
    ScanBuilder scanBuilder = mock(ScanBuilder.class);
    when(scanBuilder.build()).thenReturn(new EmptyIterator());
    when(IcebergGenerics.read(tempTable)).thenReturn(scanBuilder);

    catalog = mock(Catalog.class);
    when(catalog.createTable(any(), any())).thenReturn(tempTable);
    when(catalog.dropTable(any())).thenReturn(true);

    JsonNode jsonNode = Jsons.jsonNode(ofEntries(entry(IcebergConstants.REST_CATALOG_URI_CONFIG_KEY, FAKE_REST_URI)));

    config = new RESTCatalogConfig(jsonNode);
    config.setStorageConfig(S3Config.builder()
        .warehouseUri(FAKE_WAREHOUSE_URI)
        .bucketRegion("fake-region")
        .endpoint(FAKE_ENDPOINT)
        .endpointWithSchema(FAKE_ENDPOINT_WITH_SCHEMA)
        .accessKeyId(FAKE_ACCESS_KEY_ID)
        .secretKey(FAKE_SECRET_ACCESS_KEY)
        .credentialConfig(new S3AccessKeyCredentialConfig(FAKE_ACCESS_KEY_ID, FAKE_SECRET_ACCESS_KEY))
        .s3Client(s3)
        .build());
    config.setFormatConfig(new FormatConfig(Jsons.jsonNode(ImmutableMap.of(FORMAT_TYPE_CONFIG_KEY, "Parquet"))));
    config.setDefaultOutputDatabase("default");

    factory = new IcebergCatalogConfigFactory() {

      @Override
      public IcebergCatalogConfig fromJsonNodeConfig(final @NotNull JsonNode jsonConfig) {
        return config;
      }
    };
  }

  @Test
  public void checksRESTServerUri() {
    final IcebergDestination destinationFail = new IcebergDestination();
    final AirbyteConnectionStatus status = destinationFail.check(Jsons.deserialize("""
                                                                                   {
                                                                                     "catalog_config": {
                                                                                       "catalog_type": "REST",
                                                                                       "database": "test"
                                                                                     },
                                                                                     "storage_config": {
                                                                                       "storage_type": "S3",
                                                                                       "access_key_id": "xxxxxxxxxxx",
                                                                                       "secret_access_key": "yyyyyyyyyyyy",
                                                                                       "s3_warehouse_uri": "s3://warehouse/hive",
                                                                                       "s3_bucket_region": "us-east-1",
                                                                                       "s3_endpoint": "your-own-minio-host:9000"
                                                                                     },
                                                                                     "format_config": {
                                                                                       "format": "Parquet"
                                                                                     }
                                                                                   }"""));
    log.info("status={}", status);
    assertThat(status.getStatus()).isEqualTo(Status.FAILED);
    assertThat(status.getMessage()).contains("rest_uri is required");
  }

  @Test
  public void restCatalogSparkConfigTest() {
    Map<String, String> sparkConfig = config.sparkConfigMap();
    log.info("Spark Config for REST catalog: {}", sparkConfig);

    // Catalog config
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.catalog-impl")).isEqualTo(RESTCatalog.class.getName());
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.uri")).isEqualTo(FAKE_REST_URI);
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg")).isEqualTo(SparkCatalog.class.getName());
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.io-impl")).isEqualTo(S3FileIO.class.getName());
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.warehouse")).isEqualTo(FAKE_WAREHOUSE_URI);
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.s3.access-key-id")).isEqualTo(FAKE_ACCESS_KEY_ID);
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.s3.secret-access-key")).isEqualTo(FAKE_SECRET_ACCESS_KEY);
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.s3.endpoint")).isEqualTo(FAKE_ENDPOINT_WITH_SCHEMA);
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.s3.path-style-access")).isEqualTo("false");

    // Hadoop config
    assertThat(sparkConfig.get("spark.hadoop.fs.s3a.endpoint")).isEqualTo(FAKE_ENDPOINT);
    assertThat(sparkConfig.get("spark.hadoop.fs.s3a.access.key")).isEqualTo(FAKE_ACCESS_KEY_ID);
    assertThat(sparkConfig.get("spark.hadoop.fs.s3a.secret.key")).isEqualTo(FAKE_SECRET_ACCESS_KEY);
    assertThat(sparkConfig.get("spark.hadoop.fs.s3a.impl")).isEqualTo(S3AFileSystem.class.getName());
    assertThat(sparkConfig.get("spark.hadoop.fs.s3a.connection.ssl.enabled")).isEqualTo("false");
  }

  @Test
  public void s3ConfigForCatalogInitializeTest() {
    Map<String, String> properties = config.getStorageConfig().catalogInitializeProperties();
    log.info("S3 Config for RESTCatalog Initialize: {}", properties);

    assertThat(properties.get("io-impl")).isEqualTo(S3FileIO.class.getName());
    assertThat(properties.get("s3.endpoint")).isEqualTo(FAKE_ENDPOINT_WITH_SCHEMA);
    assertThat(properties.get("s3.access-key-id")).isEqualTo(FAKE_ACCESS_KEY_ID);
    assertThat(properties.get("s3.secret-access-key")).isEqualTo(FAKE_SECRET_ACCESS_KEY);
    assertThat(properties.get("s3.path-style-access")).isEqualTo("false");
  }

}
