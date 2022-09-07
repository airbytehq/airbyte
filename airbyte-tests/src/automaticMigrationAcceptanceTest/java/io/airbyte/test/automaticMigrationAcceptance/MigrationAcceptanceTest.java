/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.automaticMigrationAcceptance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.api.client.generated.DestinationDefinitionApi;
import io.airbyte.api.client.generated.HealthApi;
import io.airbyte.api.client.generated.SourceDefinitionApi;
import io.airbyte.api.client.generated.WorkspaceApi;
import io.airbyte.api.client.invoker.generated.ApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.DestinationDefinitionRead;
import io.airbyte.api.client.model.generated.SourceDefinitionRead;
import io.airbyte.api.client.model.generated.WorkspaceIdRequestBody;
import io.airbyte.api.client.model.generated.WorkspaceRead;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreProperties;
import io.airbyte.test.airbyte_test_container.AirbyteTestContainer;
import java.io.File;
import java.nio.file.Path;
import java.util.List;
import java.util.Properties;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;
import java.util.function.Supplier;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class contains an e2e test simulating what a user encounter when trying to upgrade Airybte.
 * - upgrading from 0.32.0 to the latest version should work. - This test previously tested
 * upgrading from even older versions, which has since been removed
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

  private static WorkspaceIdRequestBody workspaceIdRequestBody = null;

  @Test
  @Disabled
  void testAutomaticMigration() throws Exception {
    // start at "faux" major version bump version. This was the last version that required db data
    // migrations.
    final File version32DockerComposeFile = MoreResources.readResourceAsFile("docker-compose-migration-test-0-32-0-alpha.yaml");
    final Properties version32EnvFileProperties = MoreProperties
        .envFileToProperties(MoreResources.readResourceAsFile("env-file-migration-test-0-32-0.env"));
    runAirbyte(version32DockerComposeFile, version32EnvFileProperties, MigrationAcceptanceTest::assertHealthy);

    final File currentDockerComposeFile = MoreResources.readResourceAsFile("docker-compose.yaml");
    // piggybacks off of whatever the existing .env file is, so override default filesystem values in to
    // point at test paths.
    final Properties envFileProperties = overrideDirectoriesForTest(MoreProperties.envFileToProperties(ENV_FILE));
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

  @SuppressWarnings("PMD.NonThreadSafeSingleton")
  private static void assertDataFromApi(final ApiClient apiClient) throws ApiException {
    if (workspaceIdRequestBody != null) {
      assertEquals(assertWorkspaceInformation(apiClient).getWorkspaceId(), workspaceIdRequestBody.getWorkspaceId());
    } else {
      workspaceIdRequestBody = assertWorkspaceInformation(apiClient);
    }

    assertSourceDefinitionInformation(apiClient);
    assertDestinationDefinitionInformation(apiClient);
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
        foundMysqlSourceDefinition = true;
      } else if ("decd338e-5647-4c0b-adf4-da0e75f5a750".equals(sourceDefinitionRead.getSourceDefinitionId().toString())) {
        assertEquals(sourceDefinitionRead.getName(), "Postgres");
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
        foundPostgresDestinationDefinition = true;
      } else if ("8be1cf83-fde1-477f-a4ad-318d23c9f3c6".equals(destinationId)) {
        assertTrue(destinationDefinitionRead.getName().contains("Local CSV"));
        foundLocalCSVDestinationDefinition = true;
      } else if ("424892c4-daac-4491-b35d-c6688ba547ba".equals(destinationId)) {
        assertTrue(destinationDefinitionRead.getName().contains("Snowflake"));
        foundSnowflakeDestinationDefinition = true;
      }
    }

    assertTrue(foundPostgresDestinationDefinition);
    assertTrue(foundLocalCSVDestinationDefinition);
    assertTrue(foundSnowflakeDestinationDefinition);
  }

  private static WorkspaceIdRequestBody assertWorkspaceInformation(final ApiClient apiClient) throws ApiException {
    final WorkspaceApi workspaceApi = new WorkspaceApi(apiClient);
    final WorkspaceRead workspace = workspaceApi.listWorkspaces().getWorkspaces().get(0);
    assertNotNull(workspace.getWorkspaceId().toString());
    assertNotNull(workspace.getName());
    assertNotNull(workspace.getSlug());
    assertEquals(false, workspace.getInitialSetupComplete());

    return new WorkspaceIdRequestBody().workspaceId(workspace.getWorkspaceId());
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
