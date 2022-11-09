/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.acceptance;

import static io.airbyte.config.helpers.CloudLogs.LOGGER;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.waitForSuccessfulJob;

import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.generated.ApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.AirbyteCatalog;
import io.airbyte.api.client.model.generated.ConnectionScheduleType;
import io.airbyte.api.client.model.generated.DestinationDefinitionIdRequestBody;
import io.airbyte.api.client.model.generated.DestinationDefinitionRead;
import io.airbyte.api.client.model.generated.DestinationSyncMode;
import io.airbyte.api.client.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.client.model.generated.SourceDefinitionRead;
import io.airbyte.api.client.model.generated.SyncMode;
import io.airbyte.public_api.client.generated.ConnectionApi;
import io.airbyte.test.utils.AirbyteAcceptanceTestHarness;
import java.io.IOException;
import java.net.URISyntaxException;
import java.sql.SQLException;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class PublicApiAcceptanceTests {

  private static AirbyteAcceptanceTestHarness testHarness;
  private static AirbyteApiClient internalApiClient;
  private static ConnectionApi publicApiClient;
  private static UUID workspaceId;

  @SuppressWarnings("UnstableApiUsage")
  @BeforeAll
  static void init() throws URISyntaxException, IOException, InterruptedException, ApiException {
    internalApiClient = new AirbyteApiClient(
        new ApiClient().setScheme("http")
            .setHost("localhost")
            .setPort(8001)
            .setBasePath("/api"));

    publicApiClient = new ConnectionApi(
        new io.airbyte.public_api.client.invoker.generated.ApiClient().setScheme("http")
            .setHost("localhost")
            .setPort(8080));

    // work in whatever default workspace is present.
    workspaceId = internalApiClient.getWorkspaceApi().listWorkspaces().getWorkspaces().get(0).getWorkspaceId();
    LOGGER.info("workspaceId = " + workspaceId);

    // log which connectors are being used.
    final SourceDefinitionRead sourceDef = internalApiClient.getSourceDefinitionApi()
        .getSourceDefinition(new SourceDefinitionIdRequestBody()
            .sourceDefinitionId(UUID.fromString("decd338e-5647-4c0b-adf4-da0e75f5a750")));
    final DestinationDefinitionRead destinationDef = internalApiClient.getDestinationDefinitionApi()
        .getDestinationDefinition(new DestinationDefinitionIdRequestBody()
            .destinationDefinitionId(UUID.fromString("25c5221d-dce2-4163-ade9-739ef790f503")));
    LOGGER.info("pg source definition: {}", sourceDef.getDockerImageTag());
    LOGGER.info("pg destination definition: {}", destinationDef.getDockerImageTag());

    testHarness = new AirbyteAcceptanceTestHarness(internalApiClient, workspaceId);
  }

  @AfterAll
  static void end() {
    testHarness.stopDbAndContainers();
  }

  @BeforeEach
  void setup() throws URISyntaxException, IOException, SQLException {
    testHarness.setup();
  }

  @AfterEach
  void tearDown() {
    testHarness.cleanup();
  }

  @Test
  void testManualSync() throws Exception {
    final String connectionName = "test-connection";
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();

    publicApiClient.syncConnection(connectionId, "unused");

    waitForSuccessfulJob(internalApiClient.getJobsApi(), testHarness.getMostRecentSyncJobId(connectionId));
    testHarness.assertSourceAndDestinationDbInSync(false);
  }

}
