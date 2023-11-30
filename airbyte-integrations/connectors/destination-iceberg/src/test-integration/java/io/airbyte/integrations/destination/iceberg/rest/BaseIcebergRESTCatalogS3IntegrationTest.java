/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.rest;

import static io.airbyte.integrations.destination.iceberg.IcebergIntegrationTestUtil.ICEBERG_IMAGE_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.destination.iceberg.IcebergIntegrationTestUtil;
import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;
import io.airbyte.integrations.destination.iceberg.container.RESTServerWithMinioCompose;
import java.util.HashSet;
import java.util.List;
import org.junit.jupiter.api.AfterAll;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class BaseIcebergRESTCatalogS3IntegrationTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseIcebergRESTCatalogS3IntegrationTest.class);

  private static RESTServerWithMinioCompose composeContainer;
  private static JsonNode config;

  static void startCompose(final DataFileFormat fileFormat) {
    composeContainer = new RESTServerWithMinioCompose();
    composeContainer.start();
    config = composeContainer.getComposeConfig(fileFormat);
    IcebergIntegrationTestUtil.createS3WarehouseBucket(config);
    LOGGER.info("==> Started REST Server with Minio - Docker Compose...");
  }

  @AfterAll
  public static void stopCompose() {
    IcebergIntegrationTestUtil.stopAndCloseContainer(composeContainer, "REST Server with Minio - Docker Compose");
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
    return composeContainer.getWrongConfig();
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return IcebergIntegrationTestUtil.retrieveRecords(getConfig(), namespace, streamName);
  }

}
