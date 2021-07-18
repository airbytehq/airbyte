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

package io.airbyte.test.automaticMigrationAcceptance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import com.google.common.io.Resources;
import io.airbyte.api.client.ConnectionApi;
import io.airbyte.api.client.DestinationDefinitionApi;
import io.airbyte.api.client.HealthApi;
import io.airbyte.api.client.SourceDefinitionApi;
import io.airbyte.api.client.WorkspaceApi;
import io.airbyte.api.client.invoker.ApiClient;
import io.airbyte.api.client.invoker.ApiException;
import io.airbyte.api.client.model.ConnectionRead;
import io.airbyte.api.client.model.ConnectionStatus;
import io.airbyte.api.client.model.DestinationDefinitionRead;
import io.airbyte.api.client.model.HealthCheckRead;
import io.airbyte.api.client.model.ImportRead;
import io.airbyte.api.client.model.ImportRead.StatusEnum;
import io.airbyte.api.client.model.SourceDefinitionRead;
import io.airbyte.api.client.model.WorkspaceIdRequestBody;
import io.airbyte.api.client.model.WorkspaceRead;
import io.airbyte.commons.version.AirbyteVersion;
import java.io.File;
import java.lang.reflect.InvocationTargetException;
import java.net.URISyntaxException;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.DockerComposeContainer;
import org.testcontainers.containers.output.OutputFrame;

/**
 * In order to run this test from intellij, build the docker images via SUB_BUILD=PLATFORM ./gradlew
 * composeBuild and replace System.getenv("MIGRATION_TEST_VERSION") with the version in your .env
 * file
 */
public class MigrationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationAcceptanceTest.class);

  @Test
  public void testAutomaticMigration()
      throws URISyntaxException, NoSuchFieldException, InvocationTargetException, IllegalAccessException, NoSuchMethodException, ApiException,
      InterruptedException {
    String targetVersion = System.getenv("MIGRATION_TEST_VERSION");
    firstRun();
    secondRun(targetVersion);
  }

  private Consumer<OutputFrame> logConsumerForServer(Set<String> logs) {
    return c -> {
      if (c != null && c.getBytes() != null) {
        String log = new String(c.getBytes());

        String keyToRemove = "";
        for (String expected : logs) {
          if (log.contains(expected)) {
            keyToRemove = expected;
          }
        }
        if (!keyToRemove.isEmpty()) {
          logs.remove(keyToRemove);
        }

        LOGGER.info(log);
      }
    };
  }

  private void firstRun()
      throws URISyntaxException, InterruptedException, ApiException, NoSuchFieldException, IllegalAccessException, NoSuchMethodException,
      InvocationTargetException {
    Map<String, String> environmentVariables = getEnvironmentVariables("0.17.0-alpha");
    final File firstRun = Path
        .of(Resources.getResource("docker-compose-migration-test-first-run.yaml").toURI())
        .toFile();

    Set<String> logsToExpect = new HashSet<>();
    logsToExpect.add("Version: 0.17.0-alpha");

    DockerComposeContainer dockerComposeContainer = new DockerComposeContainer(firstRun)
        .withLogConsumer("server", logConsumerForServer(logsToExpect))
        .withEnv(environmentVariables);
    try {
      /**
       * We are using CustomDockerComposeContainer cause the
       * {@link org.testcontainers.containers.DockerComposeContainer#stop()} method also deletes the
       * volume but we dont want to delete the volume to test the automatic migration
       */
      CustomDockerComposeContainer customDockerComposeContainer = new CustomDockerComposeContainer(
          dockerComposeContainer);

      customDockerComposeContainer.start();

      Thread.sleep(50000);

      assertTrue(logsToExpect.isEmpty(), "Missing logs: " + logsToExpect);
      ApiClient apiClient = getApiClient();
      healthCheck(apiClient);
      populateDataForFirstRun(apiClient);
      customDockerComposeContainer.stop();
    } catch (Exception e) {
      dockerComposeContainer.stop();
      throw e;
    }
  }

  private String targetVersionWithoutPatch(String targetVersion) {
    return AirbyteVersion.versionWithoutPatch(targetVersion).getVersion();
  }

  private void secondRun(String targetVersion)
      throws URISyntaxException, InterruptedException, ApiException {

    Map<String, String> environmentVariables = getEnvironmentVariables(targetVersion);
    final File secondRun = Path
        .of(Resources.getResource("docker-compose-migration-test-second-run.yaml")
            .toURI())
        .toFile();

    Set<String> logsToExpect = new HashSet<>();
    logsToExpect.add("Version: " + targetVersion);
    logsToExpect.add("Starting migrations. Current version: 0.17.0-alpha, Target version: "
        + targetVersionWithoutPatch(targetVersion));
    logsToExpect.add("Migrating from version: 0.17.0-alpha to version 0.18.0-alpha.");
    logsToExpect.add("Migrating from version: 0.18.0-alpha to version 0.19.0-alpha.");
    logsToExpect.add("Migrating from version: 0.19.0-alpha to version 0.20.0-alpha.");
    logsToExpect.add("Migrating from version: 0.20.0-alpha to version 0.21.0-alpha.");
    logsToExpect.add("Migrating from version: 0.22.0-alpha to version 0.23.0-alpha.");
    logsToExpect.add("Migrations complete. Now on version: " + targetVersionWithoutPatch(targetVersion));

    DockerComposeContainer dockerComposeContainer = new DockerComposeContainer(secondRun)
        .withLogConsumer("server", logConsumerForServer(logsToExpect))
        .withEnv(environmentVariables);

    try {
      dockerComposeContainer.start();

      Thread.sleep(50000);

      ApiClient apiClient = getApiClient();
      healthCheck(apiClient);

      assertTrue(logsToExpect.isEmpty(), "Missing logs: " + logsToExpect);
      assertDataFromApi(apiClient);
    } finally {
      dockerComposeContainer.stop();
    }
  }

  private void assertDataFromApi(ApiClient apiClient) throws ApiException {
    WorkspaceIdRequestBody workspaceIdRequestBody = assertWorkspaceInformation(apiClient);
    assertSourceDefinitionInformation(apiClient);
    assertDestinationDefinitionInformation(apiClient);
    assertConnectionInformation(apiClient, workspaceIdRequestBody);
  }

  private void assertSourceDefinitionInformation(ApiClient apiClient) throws ApiException {
    SourceDefinitionApi sourceDefinitionApi = new SourceDefinitionApi(apiClient);
    List<SourceDefinitionRead> sourceDefinitions = sourceDefinitionApi.listSourceDefinitions()
        .getSourceDefinitions();
    assertTrue(sourceDefinitions.size() >= 58);
    boolean foundMysqlSourceDefinition = false;
    boolean foundPostgresSourceDefinition = false;
    for (SourceDefinitionRead sourceDefinitionRead : sourceDefinitions) {
      if (sourceDefinitionRead.getSourceDefinitionId().toString()
          .equals("435bb9a5-7887-4809-aa58-28c27df0d7ad")) {
        assertEquals(sourceDefinitionRead.getName(), "MySQL");
        assertEquals(sourceDefinitionRead.getDockerImageTag(), "0.2.0");
        foundMysqlSourceDefinition = true;
      } else if (sourceDefinitionRead.getSourceDefinitionId().toString()
          .equals("decd338e-5647-4c0b-adf4-da0e75f5a750")) {
        String[] tagBrokenAsArray = sourceDefinitionRead.getDockerImageTag().replace(".", ",").split(",");
        assertEquals(3, tagBrokenAsArray.length);
        assertTrue(Integer.parseInt(tagBrokenAsArray[0]) >= 0);
        assertTrue(Integer.parseInt(tagBrokenAsArray[1]) >= 3);
        assertTrue(Integer.parseInt(tagBrokenAsArray[2]) >= 4);
        assertTrue(sourceDefinitionRead.getName().contains("Postgres"));
        foundPostgresSourceDefinition = true;
      }
    }

    assertTrue(foundMysqlSourceDefinition);
    assertTrue(foundPostgresSourceDefinition);
  }

  private void assertDestinationDefinitionInformation(ApiClient apiClient) throws ApiException {
    DestinationDefinitionApi destinationDefinitionApi = new DestinationDefinitionApi(apiClient);
    List<DestinationDefinitionRead> destinationDefinitions = destinationDefinitionApi
        .listDestinationDefinitions().getDestinationDefinitions();
    assertTrue(destinationDefinitions.size() >= 10);
    boolean foundPostgresDestinationDefinition = false;
    boolean foundLocalCSVDestinationDefinition = false;
    boolean foundSnowflakeDestinationDefintion = false;
    for (DestinationDefinitionRead destinationDefinitionRead : destinationDefinitions) {
      switch (destinationDefinitionRead.getDestinationDefinitionId().toString()) {
        case "25c5221d-dce2-4163-ade9-739ef790f503" -> {
          assertEquals(destinationDefinitionRead.getName(), "Postgres");
          assertEquals(destinationDefinitionRead.getDockerImageTag(), "0.2.0");
          foundPostgresDestinationDefinition = true;
        }
        case "8be1cf83-fde1-477f-a4ad-318d23c9f3c6" -> {
          assertEquals(destinationDefinitionRead.getDockerImageTag(), "0.2.0");
          assertTrue(destinationDefinitionRead.getName().contains("Local CSV"));
          foundLocalCSVDestinationDefinition = true;
        }
        case "424892c4-daac-4491-b35d-c6688ba547ba" -> {
          String[] tagBrokenAsArray = destinationDefinitionRead.getDockerImageTag().replace(".", ",").split(",");
          assertEquals(3, tagBrokenAsArray.length);
          assertTrue(Integer.parseInt(tagBrokenAsArray[0]) >= 0);
          assertTrue(Integer.parseInt(tagBrokenAsArray[1]) >= 3);
          assertTrue(Integer.parseInt(tagBrokenAsArray[2]) >= 9);
          assertTrue(destinationDefinitionRead.getName().contains("Snowflake"));
          foundSnowflakeDestinationDefintion = true;
        }
      }
    }

    assertTrue(foundPostgresDestinationDefinition);
    assertTrue(foundLocalCSVDestinationDefinition);
    assertTrue(foundSnowflakeDestinationDefintion);
  }

  private void assertConnectionInformation(ApiClient apiClient,
                                           WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ApiException {
    ConnectionApi connectionApi = new ConnectionApi(apiClient);
    List<ConnectionRead> connections = connectionApi
        .listConnectionsForWorkspace(workspaceIdRequestBody).getConnections();
    assertEquals(connections.size(), 2);
    for (ConnectionRead connection : connections) {
      if (connection.getConnectionId().toString()
          .equals("a294256f-1abe-4837-925f-91602c7207b4")) {
        assertEquals(connection.getPrefix(), "");
        assertEquals(connection.getSourceId().toString(), "28ffee2b-372a-4f72-9b95-8ed56a8b99c5");
        assertEquals(connection.getDestinationId().toString(),
            "4e00862d-5484-4f50-9860-f3bbb4317397");
        assertEquals(connection.getName(), "default");
        assertEquals(connection.getStatus(), ConnectionStatus.ACTIVE);
        assertNull(connection.getSchedule());
      } else if (connection.getConnectionId().toString()
          .equals("49dae3f0-158b-4737-b6e4-0eed77d4b74e")) {
        assertEquals(connection.getPrefix(), "");
        assertEquals(connection.getSourceId().toString(), "28ffee2b-372a-4f72-9b95-8ed56a8b99c5");
        assertEquals(connection.getDestinationId().toString(),
            "5434615d-a3b7-4351-bc6b-a9a695555a30");
        assertEquals(connection.getName(), "default");
        assertEquals(connection.getStatus(), ConnectionStatus.ACTIVE);
        assertNull(connection.getSchedule());
      } else {
        fail("Unknown sync " + connection.getConnectionId().toString());
      }
    }
  }

  private WorkspaceIdRequestBody assertWorkspaceInformation(ApiClient apiClient)
      throws ApiException {
    WorkspaceApi workspaceApi = new WorkspaceApi(apiClient);
    WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody()
        .workspaceId(UUID.fromString("5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6"));
    WorkspaceRead workspace = workspaceApi.getWorkspace(workspaceIdRequestBody);
    assertEquals(workspace.getWorkspaceId().toString(), "5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6");
    assertEquals(workspace.getCustomerId().toString(), "17f90b72-5ae4-40b7-bc49-d6c2943aea57");
    assertEquals(workspace.getName(), "default");
    assertEquals(workspace.getSlug(), "default");
    assertEquals(workspace.getInitialSetupComplete(), true);
    assertEquals(workspace.getAnonymousDataCollection(), false);
    assertEquals(workspace.getNews(), false);
    assertEquals(workspace.getSecurityUpdates(), false);
    assertEquals(workspace.getDisplaySetupWizard(), false);
    return workspaceIdRequestBody;
  }

  private void populateDataForFirstRun(ApiClient apiClient)
      throws ApiException, URISyntaxException {
    ImportApi deploymentApi = new ImportApi(apiClient);
    final File file = Path
        .of(Resources.getResource("03a4c904-c91d-447f-ab59-27a43b52c2fd.gz").toURI())
        .toFile();
    ImportRead importRead = deploymentApi.importArchive(file);
    assertTrue(importRead.getStatus() == StatusEnum.SUCCEEDED);
  }

  private void healthCheck(ApiClient apiClient) throws ApiException {
    HealthApi healthApi = new HealthApi(apiClient);
    try {
      HealthCheckRead healthCheck = healthApi.getHealthCheck();
      assertTrue(healthCheck.getDb());
    } catch (ApiException e) {
      throw new RuntimeException("Health check failed, usually due to auto migration failure. Please check the logs for details.");
    }
  }

  private ApiClient getApiClient() {
    ApiClient apiClient = new ApiClient().setScheme("http")
        .setHost("localhost")
        .setPort(7001)
        .setBasePath("/api");
    return apiClient;
  }

  private Map<String, String> getEnvironmentVariables(String version) {
    Map<String, String> env = new HashMap<>();
    env.put("VERSION", version);
    env.put("DATABASE_USER", "docker");
    env.put("DATABASE_PASSWORD", "docker");
    env.put("DATABASE_DB", "airbyte");
    env.put("CONFIG_ROOT", "/data");
    env.put("WORKSPACE_ROOT", "/tmp/workspace");
    env.put("DATA_DOCKER_MOUNT", "airbyte_data_migration_test");
    env.put("DB_DOCKER_MOUNT", "airbyte_db_migration_test");
    env.put("WORKSPACE_DOCKER_MOUNT", "airbyte_workspace_migration_test");
    env.put("LOCAL_ROOT", "/tmp/airbyte_local_migration_test");
    env.put("LOCAL_DOCKER_MOUNT", "/tmp/airbyte_local_migration_test");
    env.put("TRACKING_STRATEGY", "logging");
    env.put("HACK_LOCAL_ROOT_PARENT", "/tmp");
    env.put("WEBAPP_URL", "http://localhost:7000/");
    env.put("API_URL", "http://localhost:7001/api/v1/");
    env.put("TEMPORAL_HOST", "airbyte-temporal:7233");
    env.put("INTERNAL_API_HOST", "airbyte-server:7001");
    env.put("S3_LOG_BUCKET", "");
    env.put("S3_LOG_BUCKET_REGION", "");
    env.put("AWS_ACCESS_KEY_ID", "");
    env.put("AWS_SECRET_ACCESS_KEY", "");
    env.put("GCP_STORAGE_BUCKET", "");
    return env;
  }

}
