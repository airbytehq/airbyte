/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.automaticMigrationAcceptance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import com.google.common.io.Resources;
import io.airbyte.api.client.generated.ConnectionApi;
import io.airbyte.api.client.generated.DestinationDefinitionApi;
import io.airbyte.api.client.generated.HealthApi;
import io.airbyte.api.client.generated.SourceDefinitionApi;
import io.airbyte.api.client.generated.WorkspaceApi;
import io.airbyte.api.client.invoker.generated.ApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.ConnectionRead;
import io.airbyte.api.client.model.generated.ConnectionStatus;
import io.airbyte.api.client.model.generated.DestinationDefinitionRead;
import io.airbyte.api.client.model.generated.ImportRead;
import io.airbyte.api.client.model.generated.ImportRead.StatusEnum;
import io.airbyte.api.client.model.generated.SourceDefinitionRead;
import io.airbyte.api.client.model.generated.WorkspaceIdRequestBody;
import io.airbyte.api.client.model.generated.WorkspaceRead;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.concurrency.WaitingUtils;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreProperties;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.test.airbyte_test_container.AirbyteTestContainer;
import java.io.File;
import java.net.URISyntaxException;
import java.nio.file.Path;
import java.time.Duration;
import java.util.List;
import java.util.Properties;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.utility.ComparableVersion;

/**
 * This class contains an e2e test simulating what a user encounter when trying to upgrade Airybte.
 * <p>
 * Three invariants are tested:
 * <p>
 * - upgrading pass 0.32.0 without first upgrading to 0.32.0 should error.
 * <p>
 * - upgrading pass 0.32.0 without first upgrading to 0.32.0 should not put the db in a bad state.
 * <p>
 * - upgrading from 0.32.0 to the latest version should work.
 * <p>
 * This test runs on the current code version and expects local images with the `dev` tag to be
 * available. To do so, run SUB_BUILD=PLATFORM ./gradlew build.
 * <p>
 * When running this test consecutively locally, it might be necessary to run `docker volume prune`
 * to remove hanging volumes.
 */
@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class MigrationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationAcceptanceTest.class);

  // assume env file is one directory level up from airbyte-tests.
  private static final File ENV_FILE = Path.of(System.getProperty("user.dir")).getParent().resolve(".env").toFile();

  private static final String TEST_DATA_DOCKER_MOUNT = "airbyte_data_migration_test";
  private static final String TEST_DB_DOCKER_MOUNT = "airbyte_db_migration_test";
  private static final String TEST_WORKSPACE_DOCKER_MOUNT = "airbyte_workspace_migration_test";
  private static final String TEST_LOCAL_ROOT = "/tmp/airbyte_local_migration_test";
  private static final String TEST_LOCAL_DOCKER_MOUNT = "/tmp/airbyte_local_migration_test";

  @Test
  void testAutomaticMigration() throws Exception {
    // run version 17 (the oldest version of airbyte that supports auto migration)
    final File version17DockerComposeFile = MoreResources.readResourceAsFile("docker-compose-migration-test-0-17-0-alpha.yaml");
    final Properties version17EnvVariables = MoreProperties
        .envFileToProperties(MoreResources.readResourceAsFile("env-file-migration-test-0-17-0.env"));
    runAirbyte(version17DockerComposeFile, version17EnvVariables, () -> {
      populateDataForFirstRun();
      healthCheck(getApiClient());
    });

    LOGGER.info("Finish initial 0.17.0-alpha start..");

    // attempt to run from pre-version bump version to post-version bump version. expect failure.
    final File currentDockerComposeFile = MoreResources.readResourceAsFile("docker-compose.yaml");
    // piggybacks off of whatever the existing .env file is, so override default filesystem values in to
    // point at test paths.
    final Properties envFileProperties = overrideDirectoriesForTest(MoreProperties.envFileToProperties(ENV_FILE));
    // use the dev version so the test is run on the current code version.
    envFileProperties.setProperty("VERSION", "dev");
    runAirbyteAndWaitForUpgradeException(currentDockerComposeFile, envFileProperties);
    LOGGER.info("Finished testing upgrade exception..");

    // run "faux" major version bump version
    final File version32DockerComposeFile = MoreResources.readResourceAsFile("docker-compose-migration-test-0-32-0-alpha.yaml");

    final Properties version32EnvFileProperties = MoreProperties
        .envFileToProperties(MoreResources.readResourceAsFile("env-file-migration-test-0-32-0.env"));
    runAirbyte(version32DockerComposeFile, version32EnvFileProperties, MigrationAcceptanceTest::assertHealthy);

    // run from last major version bump to current version.
    runAirbyte(currentDockerComposeFile, envFileProperties, MigrationAcceptanceTest::assertHealthy, false);
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
                          final VoidCallable postStartupExecutable,
                          final boolean retainVolumesOnStop)
      throws Exception {
    LOGGER.info("Start up Airbyte at version {}", env.get("VERSION"));
    final AirbyteTestContainer airbyteTestContainer = new AirbyteTestContainer.Builder(dockerComposeFile)
        .setEnv(env)
        .build();

    airbyteTestContainer.startBlocking();
    postStartupExecutable.call();
    if (retainVolumesOnStop) {
      airbyteTestContainer.stopRetainVolumes();
    } else {
      airbyteTestContainer.stop();
    }
  }

  private void runAirbyteAndWaitForUpgradeException(final File dockerComposeFile, final Properties env) throws Exception {
    final WaitForLogLine waitForLogLine = new WaitForLogLine();
    LOGGER.info("Start up Airbyte at version {}", env.get("VERSION"));
    final AirbyteTestContainer airbyteTestContainer = new AirbyteTestContainer.Builder(dockerComposeFile)
        .setEnv(env)
        .setLogListener("bootloader", waitForLogLine.getListener("After that upgrade is complete, you may upgrade to version"))
        .build();

    airbyteTestContainer.startAsync();

    final Supplier<Boolean> condition = waitForLogLine.hasSeenLine();
    final boolean loggedUpgradeException = WaitingUtils.waitForCondition(Duration.ofSeconds(5), Duration.ofMinutes(1), condition);
    airbyteTestContainer.stopRetainVolumes();
    assertTrue(loggedUpgradeException, "Airbyte failed to throw upgrade exception.");
  }

  /**
   * Allows the test to listen for a specific log line so that the test can end as soon as that log
   * line has been encountered.
   */
  private static class WaitForLogLine {

    final AtomicBoolean hasSeenLine = new AtomicBoolean();

    public Consumer<String> getListener(final String stringToListenFor) {
      return (logLine) -> {
        if (logLine.contains(stringToListenFor)) {
          hasSeenLine.set(true);
        }
      };
    }

    public Supplier<Boolean> hasSeenLine() {
      return hasSeenLine::get;
    }

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
      if ("435bb9a5-7887-4809-aa58-28c27df0d7ad".equals(sourceDefinitionRead.getSourceDefinitionId().toString())) {
        assertEquals(sourceDefinitionRead.getName(), "MySQL");
        assertEquals(sourceDefinitionRead.getDockerImageTag(), "0.2.0");
        foundMysqlSourceDefinition = true;
      } else if ("decd338e-5647-4c0b-adf4-da0e75f5a750".equals(sourceDefinitionRead.getSourceDefinitionId().toString())) {
        final String[] tagBrokenAsArray = sourceDefinitionRead.getDockerImageTag().replace(".", ",").split(",");
        assertEquals(3, tagBrokenAsArray.length);
        // todo (cgardens) - this is very brittle. depending on when this connector gets updated in
        // source_definitions.yaml this test can start to break. for now just doing quick fix, but we should
        // be able to do an actual version comparison like we do with AirbyteVersion.
        assertTrue(Integer.parseInt(tagBrokenAsArray[0]) >= 0, "actual tag: " + sourceDefinitionRead.getDockerImageTag());
        assertTrue(Integer.parseInt(tagBrokenAsArray[1]) >= 3, "actual tag: " + sourceDefinitionRead.getDockerImageTag());
        assertTrue(Integer.parseInt(tagBrokenAsArray[2]) >= 0, "actual tag: " + sourceDefinitionRead.getDockerImageTag());
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
    boolean foundSnowflakeDestinationDefinition = false;
    String destinationId;
    for (final DestinationDefinitionRead destinationDefinitionRead : destinationDefinitions) {
      destinationId = destinationDefinitionRead.getDestinationDefinitionId().toString();
      if ("25c5221d-dce2-4163-ade9-739ef790f503".equals(destinationId)) {
        assertEquals("Postgres", destinationDefinitionRead.getName());
        assertEquals("0.2.0", destinationDefinitionRead.getDockerImageTag());
        foundPostgresDestinationDefinition = true;
      } else if ("8be1cf83-fde1-477f-a4ad-318d23c9f3c6".equals(destinationId)) {
        final String tag = destinationDefinitionRead.getDockerImageTag();
        final AirbyteVersion currentVersion = new AirbyteVersion(tag);
        final AirbyteVersion previousVersion = new AirbyteVersion("0.2.0");
        final AirbyteVersion finalVersion =
            (currentVersion.checkOnlyPatchVersionIsUpdatedComparedTo(previousVersion) ? currentVersion : previousVersion);
        assertEquals(finalVersion.toString(), currentVersion.toString());
        assertTrue(destinationDefinitionRead.getName().contains("Local CSV"));
        foundLocalCSVDestinationDefinition = true;
      } else if ("424892c4-daac-4491-b35d-c6688ba547ba".equals(destinationId)) {
        final String tag = destinationDefinitionRead.getDockerImageTag();
        final ComparableVersion version = new ComparableVersion(tag);
        assertTrue(version.compareTo(new ComparableVersion("0.3.9")) >= 0);
        assertTrue(destinationDefinitionRead.getName().contains("Snowflake"));
        foundSnowflakeDestinationDefinition = true;
      }
    }

    assertTrue(foundPostgresDestinationDefinition);
    assertTrue(foundLocalCSVDestinationDefinition);
    assertTrue(foundSnowflakeDestinationDefinition);
  }

  private static void assertConnectionInformation(final ApiClient apiClient, final WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ApiException {
    final ConnectionApi connectionApi = new ConnectionApi(apiClient);
    final List<ConnectionRead> connections = connectionApi.listConnectionsForWorkspace(workspaceIdRequestBody).getConnections();
    assertEquals(connections.size(), 2);
    for (final ConnectionRead connection : connections) {
      if ("a294256f-1abe-4837-925f-91602c7207b4".equals(connection.getConnectionId().toString())) {
        assertEquals("", connection.getPrefix());
        assertEquals("28ffee2b-372a-4f72-9b95-8ed56a8b99c5", connection.getSourceId().toString());
        assertEquals("4e00862d-5484-4f50-9860-f3bbb4317397", connection.getDestinationId().toString());
        assertEquals(ConnectionStatus.ACTIVE, connection.getStatus());
        assertNull(connection.getSchedule());
      } else if ("49dae3f0-158b-4737-b6e4-0eed77d4b74e".equals(connection.getConnectionId().toString())) {
        assertEquals("", connection.getPrefix());
        assertEquals("28ffee2b-372a-4f72-9b95-8ed56a8b99c5", connection.getSourceId().toString());
        assertEquals("5434615d-a3b7-4351-bc6b-a9a695555a30", connection.getDestinationId().toString());
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
      healthApi.getHealthCheck();
    } catch (final ApiException e) {
      throw new RuntimeException("Health check failed, usually due to auto migration failure. Please check the logs for details.", e);
    }
  }

  private static ApiClient getApiClient() {
    return new ApiClient().setScheme("http")
        .setHost("localhost")
        .setPort(8001)
        .setBasePath("/api");
  }

}
