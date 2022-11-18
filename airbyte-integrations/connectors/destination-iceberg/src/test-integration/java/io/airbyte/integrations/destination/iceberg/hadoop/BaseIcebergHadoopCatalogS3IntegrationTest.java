/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.hadoop;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.DEFAULT_DATABASE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_CATALOG_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_CATALOG_TYPE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_FORMAT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_STORAGE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_STORAGE_TYPE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_ACCESS_KEY_ID_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_BUCKET_REGION_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_ENDPOINT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_SECRET_KEY_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_WAREHOUSE_URI_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergIntegrationTestUtil.ICEBERG_IMAGE_NAME;
import static io.airbyte.integrations.destination.iceberg.IcebergIntegrationTestUtil.WAREHOUSE_BUCKET_NAME;
import static io.airbyte.integrations.destination.iceberg.container.MinioContainer.DEFAULT_ACCESS_KEY;
import static io.airbyte.integrations.destination.iceberg.container.MinioContainer.DEFAULT_SECRET_KEY;
import static java.util.Map.entry;
import static java.util.Map.ofEntries;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.iceberg.IcebergIntegrationTestUtil;
import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;
import io.airbyte.integrations.destination.iceberg.container.MinioContainer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.util.HostPortResolver;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * @author Leibniz on 2022/11/3.
 */
public abstract class BaseIcebergHadoopCatalogS3IntegrationTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseIcebergHadoopCatalogS3IntegrationTest.class);
  private MinioContainer s3Storage;

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    s3Storage = IcebergIntegrationTestUtil.createAndStartMinioContainer(null);
    IcebergIntegrationTestUtil.createS3WarehouseBucket(getConfig());
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    IcebergIntegrationTestUtil.stopAndCloseContainer(s3Storage, "Minio");
  }

  @Override
  protected String getImageName() {
    return ICEBERG_IMAGE_NAME;
  }

  @Override
  protected JsonNode getConfig() {
    String s3Endpoint = "http://" + s3Storage.getHostAddress();
    LOGGER.info("Configurate S3 endpoint to {}", s3Endpoint);
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_CATALOG_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_CATALOG_TYPE_CONFIG_KEY, "Hadoop"),
                entry(DEFAULT_DATABASE_CONFIG_KEY, "default")))),
        entry(ICEBERG_STORAGE_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(entry(ICEBERG_STORAGE_TYPE_CONFIG_KEY, "S3"),
                entry(S3_ACCESS_KEY_ID_CONFIG_KEY, DEFAULT_ACCESS_KEY),
                entry(S3_SECRET_KEY_CONFIG_KEY, DEFAULT_SECRET_KEY),
                entry(S3_WAREHOUSE_URI_CONFIG_KEY, "s3a://" + WAREHOUSE_BUCKET_NAME + "/hadoop"),
                entry(S3_BUCKET_REGION_CONFIG_KEY, "us-east-1"),
                entry(S3_ENDPOINT_CONFIG_KEY, s3Endpoint)))),
        entry(ICEBERG_FORMAT_CONFIG_KEY, Jsons.jsonNode(Map.of("format", fileFormat().getConfigValue())))));
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    String s3Endpoint = "http://%s:%s".formatted(HostPortResolver.resolveHost(s3Storage),
        HostPortResolver.resolvePort(s3Storage));
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_CATALOG_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_CATALOG_TYPE_CONFIG_KEY, "Hadoop"),
                entry(DEFAULT_DATABASE_CONFIG_KEY, "default")))),
        entry(ICEBERG_STORAGE_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(entry(ICEBERG_STORAGE_TYPE_CONFIG_KEY, "S3"),
                entry(S3_ACCESS_KEY_ID_CONFIG_KEY, DEFAULT_ACCESS_KEY),
                entry(S3_SECRET_KEY_CONFIG_KEY, "wrong_secret_key"),
                entry(S3_WAREHOUSE_URI_CONFIG_KEY, "s3a://warehouse/hadoop"),
                entry(S3_BUCKET_REGION_CONFIG_KEY, "us-east-1"),
                entry(S3_ENDPOINT_CONFIG_KEY, s3Endpoint)))),
        entry(ICEBERG_FORMAT_CONFIG_KEY, Jsons.jsonNode(Map.of("format", fileFormat().getConfigValue())))));
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws Exception {
    return IcebergIntegrationTestUtil.retrieveRecords(getConfig(), namespace, streamName);
  }

  abstract DataFileFormat fileFormat();

}
