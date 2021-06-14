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
import io.airbyte.api.client.DestinationApi;
import io.airbyte.api.client.HealthApi;
import io.airbyte.api.client.SourceApi;
import io.airbyte.api.client.WorkspaceApi;
import io.airbyte.api.client.invoker.ApiClient;
import io.airbyte.api.client.invoker.ApiException;
import io.airbyte.api.client.model.DestinationRead;
import io.airbyte.api.client.model.DestinationReadList;
import io.airbyte.api.client.model.HealthCheckRead;
import io.airbyte.api.client.model.ImportRead;
import io.airbyte.api.client.model.ImportRead.StatusEnum;
import io.airbyte.api.client.model.SourceRead;
import io.airbyte.api.client.model.SourceReadList;
import io.airbyte.api.client.model.WorkspaceIdRequestBody;
import io.airbyte.api.client.model.WorkspaceRead;
import io.airbyte.commons.version.AirbyteVersion;
import java.io.File;
import java.lang.reflect.InvocationTargetException;
import java.net.URISyntaxException;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.HashSet;
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
 * In order to run this test from intellij, build the docker images via ./gradlew composeBuild and
 * replace System.getenv("MIGRATION_TEST_VERSION") with the version in your .env file
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

      Thread.sleep(10000);

      assertTrue(logsToExpect.isEmpty());
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
    logsToExpect.add("Successful import of airbyte configs");
    logsToExpect.add("Deleting directory /data/config/STANDARD_SYNC_SCHEDULE");

    DockerComposeContainer dockerComposeContainer = new DockerComposeContainer(secondRun)
        .withLogConsumer("server", logConsumerForServer(logsToExpect))
        .withEnv(environmentVariables);

    try {
      dockerComposeContainer.start();

      Thread.sleep(50000);

      ApiClient apiClient = getApiClient();
      healthCheck(apiClient);

      assertTrue(logsToExpect.isEmpty());
      assertDataFromApi(apiClient);
    } finally {
      dockerComposeContainer.stop();
    }
  }

  private void assertDataFromApi(ApiClient apiClient) throws ApiException {
    WorkspaceIdRequestBody workspaceIdRequestBody = assertWorkspaceInformation(apiClient);
    assertDestinationInformation(apiClient, workspaceIdRequestBody);
    assertSourceInformation(apiClient, workspaceIdRequestBody);
  }

  private void assertSourceInformation(ApiClient apiClient, WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ApiException {
    SourceApi sourceApi = new SourceApi(apiClient);
    SourceReadList sourceReadList = sourceApi.listSourcesForWorkspace(workspaceIdRequestBody);
    assertEquals(sourceReadList.getSources().size(), 1);
    SourceRead sourceRead = sourceReadList.getSources().get(0);
    assertEquals(sourceRead.getName(), "MySQL localhost");
    assertEquals(sourceRead.getSourceDefinitionId().toString(), "435bb9a5-7887-4809-aa58-28c27df0d7ad");
    assertEquals(sourceRead.getWorkspaceId().toString(), "5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6");
    assertEquals(sourceRead.getSourceId().toString(), "28ffee2b-372a-4f72-9b95-8ed56a8b99c5");
    assertEquals(sourceRead.getConnectionConfiguration().get("username").asText(), "root");
    assertEquals(sourceRead.getConnectionConfiguration().get("password").asText(), "password");
    assertEquals(sourceRead.getConnectionConfiguration().get("database").asText(), "localhost_test");
    assertEquals(sourceRead.getConnectionConfiguration().get("port").asInt(), 3306);
    assertEquals(sourceRead.getConnectionConfiguration().get("host").asText(), "host.docker.internal");
  }

  private void assertDestinationInformation(ApiClient apiClient, WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ApiException {
    DestinationApi destinationApi = new DestinationApi(apiClient);
    DestinationReadList destinationReadList = destinationApi.listDestinationsForWorkspace(
        workspaceIdRequestBody);
    assertEquals(destinationReadList.getDestinations().size(), 2);
    for (DestinationRead destination : destinationReadList.getDestinations()) {
      if (destination.getDestinationId().toString().equals("4e00862d-5484-4f50-9860-f3bbb4317397")) {
        assertEquals(destination.getName(), "Postgres Docker");
        assertEquals(destination.getDestinationDefinitionId().toString(), "25c5221d-dce2-4163-ade9-739ef790f503");
        assertEquals(destination.getWorkspaceId().toString(), "5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6");
        assertEquals(destination.getConnectionConfiguration().get("username").asText(), "postgres");
        assertEquals(destination.getConnectionConfiguration().get("password").asText(), "password");
        assertEquals(destination.getConnectionConfiguration().get("database").asText(), "database");
        assertEquals(destination.getConnectionConfiguration().get("schema").asText(), "public");
        assertEquals(destination.getConnectionConfiguration().get("port").asInt(), 3000);
        assertEquals(destination.getConnectionConfiguration().get("host").asText(), "localhost");
        assertNull(destination.getConnectionConfiguration().get("basic_normalization"));
      } else if (destination.getDestinationId().toString().equals("5434615d-a3b7-4351-bc6b-a9a695555a30")) {
        assertEquals(destination.getName(), "CSV");
        assertEquals(destination.getDestinationDefinitionId().toString(), "8be1cf83-fde1-477f-a4ad-318d23c9f3c6");
        assertEquals(destination.getWorkspaceId().toString(), "5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6");
        assertEquals(destination.getConnectionConfiguration().get("destination_path").asText(), "csv_data");
      } else {
        fail("Unknown destination found with dsetination id : " + destination.getDestinationId().toString());
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
    HealthCheckRead healthCheck = healthApi.getHealthCheck();
    assertTrue(healthCheck.getDb());
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
    env.put("TEMPORAL_HOST", "airbyte-temporal:6233");
    env.put("INTERNAL_API_HOST", "airbyte-server:7001");
    return env;
  }

}
