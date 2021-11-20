/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.concurrency.WaitFor;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreProperties;
import io.airbyte.test.airbyte_test_container.AirbyteTestContainer;
import java.io.File;
import java.net.URISyntaxException;
import java.nio.file.Path;
import java.time.Duration;
import java.util.List;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * In order to run this test from intellij, build the docker images via SUB_BUILD=PLATFORM ./gradlew
 * composeBuild and set VERSION in .env to the pertinent version.
 */
public class MigrationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationAcceptanceTest.class);

  // assume env file is one directory level up from airbyte-tests.
  private static final File ENV_FILE = Path.of(System.getProperty("user.dir")).getParent().resolve(".env").toFile();

  private static final String TEST_DATA_DOCKER_MOUNT = "airbyte_data_migration_test";
  private static final String TEST_DB_DOCKER_MOUNT = "airbyte_db_migration_test";
  private static final String TEST_WORKSPACE_DOCKER_MOUNT = "airbyte_workspace_migration_test";
  private static final String TEST_LOCAL_ROOT = "/tmp/airbyte_local_migration_test";
  private static final String TEST_LOCAL_DOCKER_MOUNT = "/tmp/airbyte_local_migration_test";

  @Test
  public void testAutomaticMigration() throws Exception {
    // run version 17 (oldest version of airbyte that supports auto migration)
    final File version17DockerComposeFile = MoreResources.readResourceAsFile("docker-compose-migration-test-0-17-0-alpha.yaml");
    final Properties version17EnvVariables = MoreProperties
        .envFileToProperties(MoreResources.readResourceAsFile("env-file-migration-test-0-17-0.env"));
    runAirbyte(version17DockerComposeFile, version17EnvVariables, () -> {
      populateDataForFirstRun();
      healthCheck(getApiClient());
    });

    // attempt to run from pre-version bump version to post-version bump version. expect failure.
    final File currentDockerComposeFile = MoreResources.readResourceAsFile("docker-compose.yaml");
    final Properties envFileProperties = overrideDirectoriesForTest(MoreProperties.envFileToProperties(ENV_FILE));
    runAirbyteAndWaitForUpgradeException(currentDockerComposeFile, envFileProperties);

    // run "faux" major version bump version
    final File version32DockerComposeFile = MoreResources.readResourceAsFile("docker-compose.yaml");
    final Properties version32EnvFileProperties = MoreProperties
        .envFileToProperties(MoreResources.readResourceAsFile("env-file-migration-test-0-32-0.env"));
    runAirbyte(version32DockerComposeFile, version32EnvFileProperties, MigrationAcceptanceTest::assertHealthy);

    // run from last major version bump to current version.
    runAirbyte(currentDockerComposeFile, envFileProperties, MigrationAcceptanceTest::assertHealthy, false);
  }

  private Consumer<String> logConsumerForServer(final Set<String> expectedLogs) {
    return logLine -> expectedLogs.removeIf(entry -> {
      if (logLine.contains("Migrating from version")) {
        System.out.println("logLine = " + logLine);
      }
      return logLine.contains(entry);
    });
  }

  private Properties overrideDirectoriesForTest(final Properties properties) {
    final Properties propertiesWithOverrides = new Properties(properties);
    propertiesWithOverrides.put("DATA_DOCKER_MOUNT", TEST_DATA_DOCKER_MOUNT);
    propertiesWithOverrides.put("DB_DOCKER_MOUNT", TEST_DB_DOCKER_MOUNT);
    propertiesWithOverrides.put("WORKSPACE_DOCKER_MOUNT", TEST_WORKSPACE_DOCKER_MOUNT);
    propertiesWithOverrides.put("LOCAL_ROOT", TEST_LOCAL_ROOT);
    propertiesWithOverrides.put("LOCAL_DOCKER_MOUNT", TEST_LOCAL_DOCKER_MOUNT);
    return propertiesWithOverrides;
  }

  private void runAirbyte(final File dockerComposeFile, final Properties env, final VoidCallable assertionExecutable) throws Exception {
    runAirbyte(dockerComposeFile, env, assertionExecutable, true);
  }

  private void runAirbyte(final File dockerComposeFile,
                          final Properties env,
                          final VoidCallable assertionExecutable,
                          final boolean retainVolumesOnStop)
      throws Exception {
    LOGGER.info("Start up Airbyte at version {}", env.get("VERSION"));
    final AirbyteTestContainer airbyteTestContainer = new AirbyteTestContainer.Builder(dockerComposeFile)
        .setEnv(env)
        .build();

    airbyteTestContainer.startBlocking();
    assertionExecutable.call();
    if (retainVolumesOnStop) {
      airbyteTestContainer.stopRetainVolumes();
    } else {
      airbyteTestContainer.stop();
    }
  }

  private static class WaitForLogLine {

    AtomicBoolean hasSeenLine = new AtomicBoolean();

    public Consumer<String> getListener(final String stringToListenFor) {
      return (logLine) -> {
        if (logLine.contains(stringToListenFor)) {
          hasSeenLine.set(true);
        }
      };
    }

    public Supplier<Boolean> hasSeenLine() {
      return () -> hasSeenLine.get();
    }

  }

  private void runAirbyteAndWaitForUpgradeException(final File dockerComposeFile, final Properties env) throws Exception {
    final WaitForLogLine waitForLogLine = new WaitForLogLine();
    LOGGER.info("Start up Airbyte at version {}", env.get("VERSION"));
    final AirbyteTestContainer airbyteTestContainer = new AirbyteTestContainer.Builder(dockerComposeFile)
        .setEnv(env)
        .setLogListener("server", waitForLogLine.getListener("After that upgrade is complete, you may upgrade to version"))
        .build();

    airbyteTestContainer.startAsync();

    final Supplier<Boolean> condition = waitForLogLine.hasSeenLine();
    final boolean loggedUpgradeException = WaitFor.waitForCondition(Duration.ofSeconds(5), Duration.ofMinutes(1), condition);
    airbyteTestContainer.stopRetainVolumes();
    assertTrue(loggedUpgradeException, "Airbyte failed to throw upgrade exception.");
  }

  private static void assertHealthy() throws ApiException {
    final ApiClient apiClient = getApiClient();
    healthCheck(apiClient);
    assertDataFromApi(apiClient);
  }

  private static void assertDataFromApi(final ApiClient apiClient) throws ApiException {
    final WorkspaceIdRequestBody workspaceIdRequestBody = assertWorkspaceInformation(apiClient);
    assertSourceDefinitionInformation(apiClient);
    assertDestinationDefinitionInformation(apiClient);
    assertConnectionInformation(apiClient, workspaceIdRequestBody);
  }

  private static void assertSourceDefinitionInformation(final ApiClient apiClient) throws ApiException {
    final SourceDefinitionApi sourceDefinitionApi = new SourceDefinitionApi(apiClient);
    final List<SourceDefinitionRead> sourceDefinitions = sourceDefinitionApi.listSourceDefinitions().getSourceDefinitions();
    assertTrue(sourceDefinitions.size() >= 58);
    boolean foundMysqlSourceDefinition = false;
    boolean foundPostgresSourceDefinition = false;
    for (final SourceDefinitionRead sourceDefinitionRead : sourceDefinitions) {
      if (sourceDefinitionRead.getSourceDefinitionId().toString().equals("435bb9a5-7887-4809-aa58-28c27df0d7ad")) {
        assertEquals(sourceDefinitionRead.getName(), "MySQL");
        assertEquals(sourceDefinitionRead.getDockerImageTag(), "0.2.0");
        foundMysqlSourceDefinition = true;
      } else if (sourceDefinitionRead.getSourceDefinitionId().toString().equals("decd338e-5647-4c0b-adf4-da0e75f5a750")) {
        final String[] tagBrokenAsArray = sourceDefinitionRead.getDockerImageTag().replace(".", ",").split(",");
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

  private static void assertDestinationDefinitionInformation(final ApiClient apiClient) throws ApiException {
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
          final String[] tagBrokenAsArray = destinationDefinitionRead.getDockerImageTag().replace(".", ",").split(",");
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

  private static void assertConnectionInformation(final ApiClient apiClient, final WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ApiException {
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

  private static WorkspaceIdRequestBody assertWorkspaceInformation(final ApiClient apiClient) throws ApiException {
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
  private static void populateDataForFirstRun() throws ApiException, URISyntaxException {
    final ImportApi deploymentApi = new ImportApi(getApiClient());
    final File file = Path
        .of(Resources.getResource("03a4c904-c91d-447f-ab59-27a43b52c2fd.gz").toURI())
        .toFile();
    final ImportRead importRead = deploymentApi.importArchive(file);
    assertEquals(importRead.getStatus(), StatusEnum.SUCCEEDED);
  }

  private static void healthCheck(final ApiClient apiClient) {
    final HealthApi healthApi = new HealthApi(apiClient);
    try {
      final HealthCheckRead healthCheck = healthApi.getHealthCheck();
      assertTrue(healthCheck.getDb());
    } catch (final ApiException e) {
      throw new RuntimeException("Health check failed, usually due to auto migration failure. Please check the logs for details.");
    }
  }

  private static ApiClient getApiClient() {
    return new ApiClient().setScheme("http")
        .setHost("localhost")
        .setPort(8001)
        .setBasePath("/api");
  }

}
