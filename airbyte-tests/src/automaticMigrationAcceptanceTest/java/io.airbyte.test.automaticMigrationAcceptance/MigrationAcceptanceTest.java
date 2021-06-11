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

import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.common.io.Resources;
import io.airbyte.api.client.HealthApi;
import io.airbyte.api.client.invoker.ApiClient;
import io.airbyte.api.client.invoker.ApiException;
import io.airbyte.api.client.model.HealthCheckRead;
import io.airbyte.api.client.model.ImportRead;
import io.airbyte.api.client.model.ImportRead.StatusEnum;
import io.airbyte.commons.version.AirbyteVersion;
import java.io.File;
import java.lang.reflect.InvocationTargetException;
import java.net.URISyntaxException;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.DockerComposeContainer;
import org.testcontainers.containers.output.OutputFrame;

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
    AirbyteVersion airbyteVersion = new AirbyteVersion(targetVersion);
    return "" + airbyteVersion.getMajorVersion()
        + "."
        + airbyteVersion.getMinorVersion()
        + ".0-"
        + airbyteVersion.getVersion().replace("\n", "").strip().split("-")[1];

  }

  private void secondRun(String targetVersion)
      throws URISyntaxException, InterruptedException, ApiException {

    Map<String, String> environmentVariables = getEnvironmentVariables(targetVersion);
    final File firstRun = Path
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

    DockerComposeContainer dockerComposeContainer = new DockerComposeContainer(firstRun)
        .withLogConsumer("server", logConsumerForServer(logsToExpect))
        .withEnv(environmentVariables);

    try {
      dockerComposeContainer.start();

      Thread.sleep(50000);

      healthCheck(getApiClient());

      assertTrue(logsToExpect.isEmpty());
      // Should I assert data as well using the API?
    } finally {
      dockerComposeContainer.stop();
    }
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
