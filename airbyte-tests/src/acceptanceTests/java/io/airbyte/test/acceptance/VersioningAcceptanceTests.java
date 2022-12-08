/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.acceptance;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.generated.ApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.CustomDestinationDefinitionCreate;
import io.airbyte.api.client.model.generated.CustomSourceDefinitionCreate;
import io.airbyte.api.client.model.generated.DestinationDefinitionCreate;
import io.airbyte.api.client.model.generated.DestinationDefinitionIdRequestBody;
import io.airbyte.api.client.model.generated.DestinationDefinitionRead;
import io.airbyte.api.client.model.generated.SourceDefinitionCreate;
import io.airbyte.api.client.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.client.model.generated.SourceDefinitionRead;
import io.airbyte.test.utils.AirbyteAcceptanceTestHarness;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.sql.SQLException;
import java.util.UUID;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class VersioningAcceptanceTests {

  private static AirbyteApiClient apiClient;
  private static UUID workspaceId;

  private static AirbyteAcceptanceTestHarness testHarness;

  @BeforeAll
  static void init() throws ApiException, URISyntaxException, IOException, InterruptedException {
    apiClient = new AirbyteApiClient(
        new ApiClient().setScheme("http")
            .setHost("localhost")
            .setPort(8001)
            .setBasePath("/api"));

    workspaceId = apiClient.getWorkspaceApi().listWorkspaces().getWorkspaces().get(0).getWorkspaceId();

    testHarness = new AirbyteAcceptanceTestHarness(apiClient, workspaceId);
  }

  @AfterAll
  static void afterAll() {
    testHarness.stopDbAndContainers();
  }

  @BeforeEach
  void setup() throws SQLException, URISyntaxException, IOException {
    testHarness.setup();
  }

  @AfterEach
  void tearDown() {
    testHarness.cleanup();
  }

  @ParameterizedTest
  @CsvSource({
    "2.1.1, 0.2.0",
    "2.1.2, 0.2.1",
  })
  void testCreateSourceSpec(final String dockerImageTag, final String expectedProtocolVersion)
      throws ApiException, URISyntaxException {
    final CustomSourceDefinitionCreate sourceDefinitionCreate = new CustomSourceDefinitionCreate()
        .workspaceId(workspaceId)
        .sourceDefinition(new SourceDefinitionCreate()
            .dockerImageTag(dockerImageTag)
            .dockerRepository("airbyte/source-e2e-test")
            .documentationUrl(new URI("https://hub.docker.com/r/airbyte/source-e2e-test"))
            .name("Source E2E Test Connector"));

    final SourceDefinitionRead sourceDefinitionRead = apiClient.getSourceDefinitionApi().createCustomSourceDefinition(sourceDefinitionCreate);
    assertEquals(expectedProtocolVersion, sourceDefinitionRead.getProtocolVersion());

    final SourceDefinitionIdRequestBody sourceDefinitionReq = new SourceDefinitionIdRequestBody()
        .sourceDefinitionId(sourceDefinitionRead.getSourceDefinitionId());
    final SourceDefinitionRead sourceDefinitionReadSanityCheck =
        apiClient.getSourceDefinitionApi().getSourceDefinition(sourceDefinitionReq);
    assertEquals(sourceDefinitionRead.getProtocolVersion(), sourceDefinitionReadSanityCheck.getProtocolVersion());

    // Clean up the source
    apiClient.getSourceDefinitionApi().deleteSourceDefinition(sourceDefinitionReq);
  }

  @ParameterizedTest
  @CsvSource({
    "2.1.1, 0.2.0",
    "2.1.2, 0.2.1",
  })
  void testCreateDestinationSpec(final String dockerImageTag, final String expectedProtocolVersion)
      throws ApiException, URISyntaxException {
    final CustomDestinationDefinitionCreate destDefinitionCreate =
        new CustomDestinationDefinitionCreate()
            .workspaceId(workspaceId)
            .destinationDefinition(new DestinationDefinitionCreate()
                .dockerImageTag(dockerImageTag)
                // We are currently using source because the destination-e2e-test connector is facing a regression
                // For the purpose of the test, at this moment, using source works because we only check version
                .dockerRepository("airbyte/source-e2e-test")
                .documentationUrl(new URI("https://hub.docker.com/r/airbyte/destination-e2e-test"))
                .name("Dest E2E Test Connector"));

    final DestinationDefinitionRead destDefinitionRead =
        apiClient.getDestinationDefinitionApi().createCustomDestinationDefinition(destDefinitionCreate);
    assertEquals(expectedProtocolVersion, destDefinitionRead.getProtocolVersion());

    final DestinationDefinitionIdRequestBody destDefinitionReq = new DestinationDefinitionIdRequestBody()
        .destinationDefinitionId(destDefinitionRead.getDestinationDefinitionId());
    final DestinationDefinitionRead destDefinitionReadSanityCheck =
        apiClient.getDestinationDefinitionApi().getDestinationDefinition(destDefinitionReq);
    assertEquals(destDefinitionRead.getProtocolVersion(), destDefinitionReadSanityCheck.getProtocolVersion());

    // Clean up the destination
    apiClient.getDestinationDefinitionApi().deleteDestinationDefinition(destDefinitionReq);
  }

}
