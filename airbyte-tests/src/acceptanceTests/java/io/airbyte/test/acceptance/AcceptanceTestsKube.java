/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.test.acceptance;

import static io.airbyte.api.client.model.ConnectionSchedule.TimeUnitEnum.MINUTES;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.ApiClient;
import io.airbyte.api.client.invoker.ApiException;
import io.airbyte.api.client.model.CheckConnectionRead;
import io.airbyte.api.client.model.ConnectionCreate;
import io.airbyte.api.client.model.ConnectionIdRequestBody;
import io.airbyte.api.client.model.ConnectionRead;
import io.airbyte.api.client.model.ConnectionSchedule;
import io.airbyte.api.client.model.ConnectionStatus;
import io.airbyte.api.client.model.ConnectionUpdate;
import io.airbyte.api.client.model.DestinationCreate;
import io.airbyte.api.client.model.DestinationIdRequestBody;
import io.airbyte.api.client.model.DestinationRead;
import io.airbyte.api.client.model.JobInfoRead;
import io.airbyte.api.client.model.JobStatus;
import io.airbyte.api.client.model.SourceCreate;
import io.airbyte.api.client.model.SourceIdRequestBody;
import io.airbyte.api.client.model.SourceRead;
import io.airbyte.api.client.model.SourceSchema;
import io.airbyte.api.client.model.SyncMode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.persistence.PersistenceConstants;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.Before;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.testcontainers.shaded.org.apache.commons.lang.RandomStringUtils;

/**
 * These tests are a limited form of the tests in {@link AcceptanceTests}. They are only testing for
 * a lack of API failures. For now, we aren't re-using {@link AcceptanceTests} because we would need
 * to either provide a tunnel for the Kube service to access a non-Kube DB or we would need to
 * switch the Docker db operations to Kube.
 *
 * Since what we need most is a sanity check that we aren't getting failures, this is an interim
 * solution.
 */
@SuppressWarnings("rawtypes")
// We order tests such that earlier tests test more basic behavior that is relied upon in later
// tests.
// e.g. We test that we can create a destination before we test whether we can sync data to it.
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class AcceptanceTestsKube {

  private static final String OUTPUT_DIR = "/local/kube_test_output_" + RandomStringUtils.randomAlphabetic(5);
  private final AirbyteApiClient apiClient = new AirbyteApiClient(
      new ApiClient().setScheme("http")
          .setHost("localhost")
          .setPort(8001)
          .setBasePath("/api"));

  private List<UUID> sourceIds;
  private List<UUID> connectionIds;
  private List<UUID> destinationIds;

  @Before
  public void before() {}

  @BeforeEach
  public void setup() {
    sourceIds = Lists.newArrayList();
    connectionIds = Lists.newArrayList();
    destinationIds = Lists.newArrayList();
  }

  @AfterEach
  public void tearDown() throws ApiException {
    for (UUID sourceId : sourceIds) {
      deleteSource(sourceId);
    }

    for (UUID connectionId : connectionIds) {
      disableConnection(connectionId);
    }

    for (UUID destinationId : destinationIds) {
      deleteDestination(destinationId);
    }
  }

  @Test
  @Order(1)
  public void testCreateDestination() throws ApiException {
    final UUID destinationDefId = getDestinationDefId();
    final JsonNode destinationConfig = getDestinationConfig();
    final UUID workspaceId = PersistenceConstants.DEFAULT_WORKSPACE_ID;
    final String name = "AccTestDestinationExRate-" + UUID.randomUUID().toString();

    final DestinationRead createdDestination = createDestination(
        name,
        workspaceId,
        destinationDefId,
        destinationConfig);

    assertEquals(name, createdDestination.getName());
    assertEquals(destinationDefId, createdDestination.getDestinationDefinitionId());
    assertEquals(workspaceId, createdDestination.getWorkspaceId());
    assertEquals(destinationConfig, createdDestination.getConnectionConfiguration());
  }

  @Test
  @Order(2)
  public void testDestinationCheckConnection() throws ApiException {
    final UUID destinationId = createCsvDestination().getDestinationId();

    final CheckConnectionRead.StatusEnum checkOperationStatus = apiClient.getDestinationApi()
        .checkConnectionToDestination(new DestinationIdRequestBody().destinationId(destinationId))
        .getStatus();

    assertEquals(CheckConnectionRead.StatusEnum.SUCCEEDED, checkOperationStatus);
  }

  @Test
  @Order(3)
  public void testCreateSource() throws ApiException {
    final String name = "acc-test-ex-rate";
    final UUID postgresSourceDefinitionId = getExchangeRateApiSourceId();
    final UUID defaultWorkspaceId = PersistenceConstants.DEFAULT_WORKSPACE_ID;
    final Map<Object, Object> sourceConfig = getSourceConfig();

    final SourceRead response = createSource(
        name,
        defaultWorkspaceId,
        postgresSourceDefinitionId,
        sourceConfig);

    final JsonNode expectedConfig = Jsons.jsonNode(sourceConfig);
    assertEquals(name, response.getName());
    assertEquals(defaultWorkspaceId, response.getWorkspaceId());
    assertEquals(postgresSourceDefinitionId, response.getSourceDefinitionId());
    assertEquals(expectedConfig, response.getConnectionConfiguration());
  }

  @Test
  @Order(4)
  public void testSourceCheckConnection() throws ApiException {
    final UUID sourceId = createSource().getSourceId();

    final CheckConnectionRead checkConnectionRead = apiClient.getSourceApi().checkConnectionToSource(new SourceIdRequestBody().sourceId(sourceId));

    assertEquals(CheckConnectionRead.StatusEnum.SUCCEEDED, checkConnectionRead.getStatus());
  }

  @Test
  @Order(5)
  public void testCreateConnection() throws ApiException {
    final UUID sourceId = createSource().getSourceId();
    final SourceSchema schema = discoverSourceSchema(sourceId);
    final UUID destinationId = createCsvDestination().getDestinationId();
    final String name = "test-connection-" + UUID.randomUUID().toString();
    final ConnectionSchedule schedule = new ConnectionSchedule().timeUnit(MINUTES).units(100L);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;

    final ConnectionRead createdConnection = createConnection(name, sourceId, destinationId, schema, schedule, syncMode);

    assertEquals(sourceId, createdConnection.getSourceId());
    assertEquals(destinationId, createdConnection.getDestinationId());
    assertEquals(SyncMode.FULL_REFRESH, createdConnection.getSyncMode());
    assertEquals(schema, createdConnection.getSyncSchema());
    assertEquals(schedule, createdConnection.getSchedule());
    assertEquals(name, createdConnection.getName());
  }

  @Test
  @Order(6)
  public void testManualSync() throws Exception {
    final String connectionName = "test-connection";
    final UUID sourceId = createSource().getSourceId();
    final UUID destinationId = createCsvDestination().getDestinationId();
    final SourceSchema schema = discoverSourceSchema(sourceId);
    schema.getStreams().forEach(table -> table.getFields().forEach(c -> c.setSelected(true))); // select all fields
    final SyncMode syncMode = SyncMode.FULL_REFRESH;

    final UUID connectionId = createConnection(connectionName, sourceId, destinationId, schema, null, syncMode).getConnectionId();

    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    assertEquals(JobStatus.SUCCEEDED, connectionSyncRead.getJob().getStatus());
  }

  private SourceSchema discoverSourceSchema(UUID sourceId) throws ApiException {
    return apiClient.getSourceApi().discoverSchemaForSource(new SourceIdRequestBody().sourceId(sourceId)).getSchema();
  }

  private ConnectionRead createConnection(String name,
                                          UUID sourceId,
                                          UUID destinationId,
                                          SourceSchema schema,
                                          ConnectionSchedule schedule,
                                          SyncMode syncMode)
      throws ApiException {
    final ConnectionRead connection = apiClient.getConnectionApi().createConnection(
        new ConnectionCreate()
            .status(ConnectionStatus.ACTIVE)
            .sourceId(sourceId)
            .destinationId(destinationId)
            .syncMode(syncMode)
            .syncSchema(schema)
            .schedule(schedule)
            .name(name));
    connectionIds.add(connection.getConnectionId());
    return connection;
  }

  private DestinationRead createCsvDestination() throws ApiException {
    return createDestination(
        "AccTestDestination-" + UUID.randomUUID().toString(),
        PersistenceConstants.DEFAULT_WORKSPACE_ID,
        getDestinationDefId(),
        getDestinationConfig());
  }

  private DestinationRead createDestination(String name, UUID workspaceId, UUID destinationId, JsonNode destinationConfig) throws ApiException {
    final DestinationRead destination =
        apiClient.getDestinationApi().createDestination(new DestinationCreate()
            .name(name)
            .connectionConfiguration(Jsons.jsonNode(destinationConfig))
            .workspaceId(workspaceId)
            .destinationDefinitionId(destinationId));
    destinationIds.add(destination.getDestinationId());
    return destination;
  }

  private UUID getDestinationDefId() throws ApiException {
    return apiClient.getDestinationDefinitionApi().listDestinationDefinitions().getDestinationDefinitions()
        .stream()
        .filter(dr -> dr.getName().toLowerCase().contains("csv"))
        .findFirst()
        .orElseThrow()
        .getDestinationDefinitionId();
  }

  private JsonNode getDestinationConfig() {
    return Jsons.jsonNode(ImmutableMap.of("destination_path", OUTPUT_DIR));
  }

  private Map<Object, Object> getSourceConfig() {
    final Map<Object, Object> config = new HashMap<>();
    config.put("base", "USD");
    config.put("start_date", "2021-01-01");
    return config;
  }

  private SourceRead createSource() throws ApiException {
    return createSource(
        "acceptanceTestExRate-" + UUID.randomUUID().toString(),
        PersistenceConstants.DEFAULT_WORKSPACE_ID,
        getExchangeRateApiSourceId(),
        getSourceConfig());
  }

  private SourceRead createSource(String name, UUID workspaceId, UUID sourceDefId, Map<Object, Object> sourceConfig) throws ApiException {
    final SourceRead source = apiClient.getSourceApi().createSource(new SourceCreate()
        .name(name)
        .sourceDefinitionId(sourceDefId)
        .workspaceId(workspaceId)
        .connectionConfiguration(Jsons.jsonNode(sourceConfig)));
    sourceIds.add(source.getSourceId());
    return source;
  }

  private UUID getExchangeRateApiSourceId() throws ApiException {
    return apiClient.getSourceDefinitionApi().listSourceDefinitions().getSourceDefinitions()
        .stream()
        .filter(sourceRead -> sourceRead.getName().toLowerCase().equals("exchange rates api"))
        .findFirst()
        .orElseThrow()
        .getSourceDefinitionId();
  }

  private void deleteSource(UUID sourceId) throws ApiException {
    apiClient.getSourceApi().deleteSource(new SourceIdRequestBody().sourceId(sourceId));
  }

  private void disableConnection(UUID connectionId) throws ApiException {
    final ConnectionRead connection = apiClient.getConnectionApi().getConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    final ConnectionUpdate connectionUpdate =
        new ConnectionUpdate()
            .connectionId(connectionId)
            .status(ConnectionStatus.DEPRECATED)
            .schedule(connection.getSchedule())
            .syncSchema(connection.getSyncSchema());
    apiClient.getConnectionApi().updateConnection(connectionUpdate);
  }

  private void deleteDestination(UUID destinationId) throws ApiException {
    apiClient.getDestinationApi().deleteDestination(new DestinationIdRequestBody().destinationId(destinationId));
  }

  private String adaptToCsvName(String streamName) {
    return streamName.replaceAll("public\\.", "public_");
  }

}
