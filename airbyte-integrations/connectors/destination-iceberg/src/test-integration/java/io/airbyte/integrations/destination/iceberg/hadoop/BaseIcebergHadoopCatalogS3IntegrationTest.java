/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.hadoop;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.DEFAULT_DATABASE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_CATALOG_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_CATALOG_TYPE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_FORMAT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_STORAGE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergIntegrationTestUtil.ICEBERG_IMAGE_NAME;
import static java.util.Map.entry;
import static java.util.Map.ofEntries;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.iceberg.IcebergIntegrationTestUtil;
import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;
import io.airbyte.integrations.destination.iceberg.container.MinioContainer;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Disabled;

/**
 * @author Leibniz on 2022/11/3.
 */
public abstract class BaseIcebergHadoopCatalogS3IntegrationTest extends DestinationAcceptanceTest {

  private static final String WAREHOUSE_URI = "s3a://warehouse/hadoop";
  private static MinioContainer minioContainer;

  static void start(DataFileFormat fileFormat) {
    minioContainer = new MinioContainer();
    minioContainer.start();
    IcebergIntegrationTestUtil.createS3WarehouseBucket(getConfigForTestRunner());
  }

  private static JsonNode getConfigForTestRunner() {
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_CATALOG_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_CATALOG_TYPE_CONFIG_KEY, "Hadoop"),
                entry(DEFAULT_DATABASE_CONFIG_KEY, "default")))),
        entry(ICEBERG_STORAGE_CONFIG_KEY, minioContainer.getConfig(WAREHOUSE_URI)),
        // Doesn't matter what format since this config is used for Test execution code not the connector.
        entry(ICEBERG_FORMAT_CONFIG_KEY, Jsons.jsonNode(Map.of("format", DataFileFormat.PARQUET)))));
  }

  @AfterAll
  public static void stop() {
    minioContainer.stop();
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) {}

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {}

  @Override
  protected String getImageName() {
    return ICEBERG_IMAGE_NAME;
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_CATALOG_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_CATALOG_TYPE_CONFIG_KEY, "Hadoop"),
                entry(DEFAULT_DATABASE_CONFIG_KEY, "default")))),
        entry(ICEBERG_STORAGE_CONFIG_KEY, minioContainer.getConfigWithResolvedHostPort(WAREHOUSE_URI)),
        entry(ICEBERG_FORMAT_CONFIG_KEY, Jsons.jsonNode(Map.of("format", fileFormat().getConfigValue())))));
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_CATALOG_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_CATALOG_TYPE_CONFIG_KEY, "Hadoop"),
                entry(DEFAULT_DATABASE_CONFIG_KEY, "default")))),
        entry(ICEBERG_STORAGE_CONFIG_KEY, minioContainer.getWrongConfig(WAREHOUSE_URI)),
        entry(ICEBERG_FORMAT_CONFIG_KEY, Jsons.jsonNode(Map.of("format", fileFormat().getConfigValue())))));
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return IcebergIntegrationTestUtil.retrieveRecords(getConfigForTestRunner(), namespace, streamName);
  }

  abstract DataFileFormat fileFormat();

  @Nullable
  @Override
  protected String getDefaultSchema(@NotNull JsonNode config) throws Exception {
    // TODO: This was NPE'ing without this return value because of Kotlin's non-null in base,
    // but whats the actual value to pass instead of empty ?
    return "";
  }

  @Disabled("Existing connector does not support flattened rows yet")
  @Override
  public void testAirbyteFields() throws Exception {}

}
