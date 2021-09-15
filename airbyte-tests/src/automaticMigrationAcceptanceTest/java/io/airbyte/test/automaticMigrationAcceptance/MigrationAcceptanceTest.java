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
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
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
import io.airbyte.test.airbyte_test_container.AirbyteTestContainer;
import java.io.File;
import java.io.FileInputStream;
import java.net.URISyntaxException;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Set;
import java.util.function.Consumer;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * In order to run this test from intellij, build the docker images via SUB_BUILD=PLATFORM ./gradlew
 * composeBuild and replace System.getenv("MIGRATION_TEST_VERSION") with the version in your .env
 * file
 */
public class MigrationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationAcceptanceTest.class);

  // assume env file is one directory level up from airbyte-tests.
  private final static File ENV_FILE = Path.of(System.getProperty("user.dir")).getParent().resolve(".env").toFile();

  /**
   * This test is deprecated because it no longer works after the introduce of the Flyway migration.
   */
  @Test
  @Disabled
  public void testAutomaticMigration() throws Exception {
    // default to version in env file but can override it.
    final String targetVersion;
    if (System.getenv("MIGRATION_TEST_VERSION") != null) {
      targetVersion = System.getenv("MIGRATION_TEST_VERSION");
    } else {
      final Properties prop = new Properties();
      prop.load(new FileInputStream(ENV_FILE));
      targetVersion = prop.getProperty("VERSION");
    }
    LOGGER.info("Using version: {} as target version", targetVersion);

    firstRun();
    secondRun(targetVersion);
  }

  private Consumer<String> logConsumerForServer(Set<String> expectedLogs) {
    return logLine -> expectedLogs.removeIf(entry -> {
      if (logLine.contains("Migrating from version")) {
        System.out.println("logLine = " + logLine);
        System.out.println("logLine = " + logLine);
      }
      return logLine.contains(entry);
    });
  }

  @SuppressWarnings("UnstableApiUsage")
  private void firstRun() throws Exception {
    // 0.17.0-alpha-db-patch is specifically built for this test;
    // it connects to the database with retries to fix flaky connection issue
    // https://github.com/airbytehq/airbyte/issues/4955
    final Map<String, String> environmentVariables = getEnvironmentVariables("0.17.0-alpha-db-patch");

    final Set<String> logsToExpect = new HashSet<>();
    logsToExpect.add("Version: 0.17.0-alpha-db-patch");

    final AirbyteTestContainer airbyteTestContainer =
        new AirbyteTestContainer.Builder(new File(Resources.getResource("docker-compose-migration-test-0-17-0-alpha.yaml").toURI()))
            .setEnv(environmentVariables)
            .setLogListener("server", logConsumerForServer(logsToExpect))
            .build();

    airbyteTestContainer.start();

    assertTrue(logsToExpect.isEmpty(), "Missing logs: " + logsToExpect);
    final ApiClient apiClient = getApiClient();
    healthCheck(apiClient);
    populateDataForFirstRun(apiClient);
    airbyteTestContainer.stopRetainVolumes();
  }

  private String targetVersionWithoutPatch(String targetVersion) {
    return AirbyteVersion.versionWithoutPatch(targetVersion).getVersion();
  }

  @SuppressWarnings("UnstableApiUsage")
  private void secondRun(String targetVersion) throws Exception {
    final Set<String> logsToExpect = new HashSet<>();
    logsToExpect.add("Version: " + targetVersion);
    logsToExpect.add("Starting migrations. Current version: 0.17.0-alpha-db-patch, Target version: " + targetVersionWithoutPatch(targetVersion));
    logsToExpect.add("Migrating from version: 0.17.0-alpha to version 0.18.0-alpha.");
    logsToExpect.add("Migrating from version: 0.18.0-alpha to version 0.19.0-alpha.");
    logsToExpect.add("Migrating from version: 0.19.0-alpha to version 0.20.0-alpha.");
    logsToExpect.add("Migrating from version: 0.20.0-alpha to version 0.21.0-alpha.");
    logsToExpect.add("Migrating from version: 0.22.0-alpha to version 0.23.0-alpha.");
    logsToExpect.add("Migrations complete. Now on version: " + targetVersionWithoutPatch(targetVersion));

    final AirbyteTestContainer airbyteTestContainer = new AirbyteTestContainer.Builder(new File(Resources.getResource("docker-compose.yaml").toURI()))
        .setEnv(ENV_FILE)
        // override to use test mounts.
        .setEnvVariable("DATA_DOCKER_MOUNT", "airbyte_data_migration_test")
        .setEnvVariable("DB_DOCKER_MOUNT", "airbyte_db_migration_test")
        .setEnvVariable("WORKSPACE_DOCKER_MOUNT", "airbyte_workspace_migration_test")
        .setEnvVariable("LOCAL_ROOT", "/tmp/airbyte_local_migration_test")
        .setEnvVariable("LOCAL_DOCKER_MOUNT", "/tmp/airbyte_local_migration_test")
        .setLogListener("server", logConsumerForServer(logsToExpect))
        .build();

    airbyteTestContainer.start();

    ApiClient apiClient = getApiClient();
    healthCheck(apiClient);

    assertTrue(logsToExpect.isEmpty(), "Missing logs: " + logsToExpect);
    assertDataFromApi(apiClient);

    airbyteTestContainer.stop();
  }

  private void assertDataFromApi(ApiClient apiClient) throws ApiException {
    final WorkspaceIdRequestBody workspaceIdRequestBody = assertWorkspaceInformation(apiClient);
    assertSourceDefinitionInformation(apiClient);
    assertDestinationDefinitionInformation(apiClient);
    assertConnectionInformation(apiClient, workspaceIdRequestBody);
  }

  private void assertSourceDefinitionInformation(ApiClient apiClient) throws ApiException {
    final SourceDefinitionApi sourceDefinitionApi = new SourceDefinitionApi(apiClient);
    final List<SourceDefinitionRead> sourceDefinitions = sourceDefinitionApi.listSourceDefinitions().getSourceDefinitions();
    assertTrue(sourceDefinitions.size() >= 58);
    boolean foundMysqlSourceDefinition = false;
    boolean foundPostgresSourceDefinition = false;
    for (SourceDefinitionRead sourceDefinitionRead : sourceDefinitions) {
      if (sourceDefinitionRead.getSourceDefinitionId().toString().equals("435bb9a5-7887-4809-aa58-28c27df0d7ad")) {
        assertEquals(sourceDefinitionRead.getName(), "MySQL");
        assertEquals(sourceDefinitionRead.getDockerImageTag(), "0.2.0");
        foundMysqlSourceDefinition = true;
      } else if (sourceDefinitionRead.getSourceDefinitionId().toString().equals("decd338e-5647-4c0b-adf4-da0e75f5a750")) {
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
    final DestinationDefinitionApi destinationDefinitionApi = new DestinationDefinitionApi(apiClient);
    final List<DestinationDefinitionRead> destinationDefinitions = destinationDefinitionApi.listDestinationDefinitions().getDestinationDefinitions();
    assertTrue(destinationDefinitions.size() >= 10);
    boolean foundPostgresDestinationDefinition = false;
    boolean foundLocalCSVDestinationDefinition = false;
    boolean foundSnowflakeDestinationDefintion = false;
    for (final DestinationDefinitionRead destinationDefinitionRead : destinationDefinitions) {
      switch (destinationDefinitionRead.getDestinationDefinitionId().toString()) {
        case "25c5221d-dce2-4163-ade9-739ef790f503" -> {
          assertEquals("Postgres", destinationDefinitionRead.getName());
          assertEquals("0.2.0", destinationDefinitionRead.getDockerImageTag());
          foundPostgresDestinationDefinition = true;
        }
        case "8be1cf83-fde1-477f-a4ad-318d23c9f3c6" -> {
          assertEquals("0.2.0", destinationDefinitionRead.getDockerImageTag());
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

  private void assertConnectionInformation(ApiClient apiClient, WorkspaceIdRequestBody workspaceIdRequestBody) throws ApiException {
    final ConnectionApi connectionApi = new ConnectionApi(apiClient);
    final List<ConnectionRead> connections = connectionApi.listConnectionsForWorkspace(workspaceIdRequestBody).getConnections();
    assertEquals(connections.size(), 2);
    for (final ConnectionRead connection : connections) {
      if (connection.getConnectionId().toString().equals("a294256f-1abe-4837-925f-91602c7207b4")) {
        assertEquals("", connection.getPrefix());
        assertEquals("28ffee2b-372a-4f72-9b95-8ed56a8b99c5", connection.getSourceId().toString());
        assertEquals("4e00862d-5484-4f50-9860-f3bbb4317397", connection.getDestinationId().toString());
        assertEquals("default", connection.getName());
        assertEquals(ConnectionStatus.ACTIVE, connection.getStatus());
        assertNull(connection.getSchedule());
      } else if (connection.getConnectionId().toString().equals("49dae3f0-158b-4737-b6e4-0eed77d4b74e")) {
        assertEquals("", connection.getPrefix());
        assertEquals("28ffee2b-372a-4f72-9b95-8ed56a8b99c5", connection.getSourceId().toString());
        assertEquals("5434615d-a3b7-4351-bc6b-a9a695555a30", connection.getDestinationId().toString());
        assertEquals("default", connection.getName());
        assertEquals(ConnectionStatus.ACTIVE, connection.getStatus());
        assertNull(connection.getSchedule());
      } else {
        fail("Unknown sync " + connection.getConnectionId().toString());
      }
    }
  }

  private WorkspaceIdRequestBody assertWorkspaceInformation(ApiClient apiClient) throws ApiException {
    final WorkspaceApi workspaceApi = new WorkspaceApi(apiClient);
    final WorkspaceRead workspace = workspaceApi.listWorkspaces().getWorkspaces().get(0);
    // originally the default workspace started with a hardcoded id. the migration in version 0.29.0
    // took that id and randomized it. we want to check that the id is now NOT that hardcoded id and
    // that all related resources use the updated workspaceId as well.
    assertNotNull(workspace.getWorkspaceId().toString());
    assertNotEquals("5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6", workspace.getWorkspaceId().toString());
    assertEquals("17f90b72-5ae4-40b7-bc49-d6c2943aea57", workspace.getCustomerId().toString());
    assertEquals("default", workspace.getName());
    assertEquals("default", workspace.getSlug());
    assertEquals(true, workspace.getInitialSetupComplete());
    assertEquals(false, workspace.getAnonymousDataCollection());
    assertEquals(false, workspace.getNews());
    assertEquals(false, workspace.getSecurityUpdates());
    assertEquals(false, workspace.getDisplaySetupWizard());

    return new WorkspaceIdRequestBody().workspaceId(workspace.getWorkspaceId());
  }

  @SuppressWarnings("UnstableApiUsage")
  private void populateDataForFirstRun(ApiClient apiClient) throws ApiException, URISyntaxException {
    final ImportApi deploymentApi = new ImportApi(apiClient);
    final File file = Path
        .of(Resources.getResource("03a4c904-c91d-447f-ab59-27a43b52c2fd.gz").toURI())
        .toFile();
    final ImportRead importRead = deploymentApi.importArchive(file);
    assertEquals(importRead.getStatus(), StatusEnum.SUCCEEDED);
  }

  private void healthCheck(ApiClient apiClient) {
    final HealthApi healthApi = new HealthApi(apiClient);
    try {
      HealthCheckRead healthCheck = healthApi.getHealthCheck();
      assertTrue(healthCheck.getDb());
    } catch (ApiException e) {
      throw new RuntimeException("Health check failed, usually due to auto migration failure. Please check the logs for details.");
    }
  }

  private ApiClient getApiClient() {
    return new ApiClient().setScheme("http")
        .setHost("localhost")
        .setPort(8001)
        .setBasePath("/api");
  }

  private Map<String, String> getEnvironmentVariables(String version) {
    final Map<String, String> env = new HashMap<>();
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
    env.put("WEBAPP_URL", "http://localhost:8000/");
    env.put("API_URL", "http://localhost:8001/api/v1/");
    env.put("TEMPORAL_HOST", "airbyte-temporal:7233");
    env.put("INTERNAL_API_HOST", "airbyte-server:8001");
    env.put("S3_LOG_BUCKET", "");
    env.put("S3_LOG_BUCKET_REGION", "");
    env.put("AWS_ACCESS_KEY_ID", "");
    env.put("AWS_SECRET_ACCESS_KEY", "");
    env.put("GCP_STORAGE_BUCKET", "");
    return env;
  }

}
