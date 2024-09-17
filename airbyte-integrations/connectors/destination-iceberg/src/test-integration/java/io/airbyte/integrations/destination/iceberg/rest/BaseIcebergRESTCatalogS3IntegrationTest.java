/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.rest;

import static io.airbyte.integrations.destination.iceberg.IcebergIntegrationTestUtil.ICEBERG_IMAGE_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.destination.iceberg.IcebergIntegrationTestUtil;
import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;
import io.airbyte.integrations.destination.iceberg.container.TabularRestCatalogContainer;
import java.util.HashSet;
import java.util.List;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Disabled;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class BaseIcebergRESTCatalogS3IntegrationTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseIcebergRESTCatalogS3IntegrationTest.class);

  private static TabularRestCatalogContainer restCatalogContainer;
  private static JsonNode config;

  static void startCompose(final DataFileFormat fileFormat) {
    restCatalogContainer = new TabularRestCatalogContainer();
    restCatalogContainer.startAll();
    config = restCatalogContainer.getConfigWithResolvedHostPort(fileFormat);
    IcebergIntegrationTestUtil.createS3WarehouseBucket(restCatalogContainer.getConfig(fileFormat));
    LOGGER.info("==> Started REST Server with Minio");
  }

  @AfterAll
  public static void stopCompose() {
    restCatalogContainer.stopAll();
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
    return config;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return restCatalogContainer.getWrongConfig();
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    // TODO: create another method to get config for retrieving records.
    return IcebergIntegrationTestUtil.retrieveRecords(restCatalogContainer.getConfig(DataFileFormat.PARQUET), namespace, streamName);
  }

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
