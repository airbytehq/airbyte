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

package io.airbyte.server.migration;

import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.common.io.Resources;
import io.airbyte.api.client.DeploymentApi;
import io.airbyte.api.client.HealthApi;
import io.airbyte.api.client.invoker.ApiClient;
import io.airbyte.api.client.invoker.ApiException;
import io.airbyte.api.client.model.HealthCheckRead;
import io.airbyte.api.client.model.ImportRead;
import io.airbyte.api.client.model.ImportRead.StatusEnum;
import java.io.File;
import java.lang.reflect.InvocationTargetException;
import java.net.URISyntaxException;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;
import org.jetbrains.annotations.NotNull;
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
    firstRun();
    secondRun();
  }

  private Consumer<OutputFrame> logConsumerForServer(String versionToCompare,
                                                     AtomicBoolean foundVersion) {
    return c -> {
      if (c != null && c.getBytes() != null) {
        String log = new String(c.getBytes());
        if (log.contains(versionToCompare)) {
          foundVersion.set(true);
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
        .of(Resources.getResource("migration/docker-compose-migration-test-first-run.yaml").toURI())
        .toFile();

    AtomicBoolean foundVersion17 = new AtomicBoolean(false);

    DockerComposeContainer dockerComposeContainer = new DockerComposeContainer(firstRun)
        .withLogConsumer("server", logConsumerForServer("Version: 0.17.0-alpha", foundVersion17))
        .withEnv(environmentVariables);

    CustomDockerComposeContainer customDockerComposeContainer = new CustomDockerComposeContainer(
        dockerComposeContainer);

    customDockerComposeContainer.start();

    Thread.sleep(10000);

    assertTrue(foundVersion17.get());
    ApiClient apiClient = getApiClient();
    healthCheck(apiClient);
    populateDataForFirstRun(apiClient);
    customDockerComposeContainer.stop();
  }

  private void secondRun()
      throws URISyntaxException, InterruptedException, ApiException {

    // Starting migrations. Current version: 0.17.0-alpha, Target version: 0.24.0-alpha
    // Migrating from version: 0.17.0-alpha to version 0.18.0-alpha.
    // Migrating from version: 0.17.0-alpha to version 0.18.0-alpha.
    // Migrating from version: 0.18.0-alpha to version 0.19.0-alpha.
    // Migrating from version: 0.19.0-alpha to version 0.20.0-alpha.
    // Migrating from version: 0.20.0-alpha to version 0.21.0-alpha.
    // Migrating from version: 0.21.0-alpha to version 0.22.0-alpha.
    // Migrating from version: 0.22.0-alpha to version 0.23.0-alpha.
    // Migrating from version: 0.23.0-alpha to version 0.24.0-alpha.
    // Migrations complete. Now on version: 0.24.0-alpha

    Map<String, String> environmentVariables = getEnvironmentVariables("0.24.3-alpha");
    final File firstRun = Path
        .of(Resources.getResource("migration/docker-compose-migration-test-second-run.yaml")
            .toURI())
        .toFile();

    AtomicBoolean foundVersion24 = new AtomicBoolean(false);

    DockerComposeContainer dockerComposeContainer = new DockerComposeContainer(firstRun)
        .withLogConsumer("server", logConsumerForServer("Version: 0.24.3-alpha", foundVersion24))
        .withEnv(environmentVariables);

    dockerComposeContainer.start();

    Thread.sleep(50000);

    healthCheck(getApiClient());

    assertTrue(foundVersion24.get());
    dockerComposeContainer.stop();
  }

  private void populateDataForFirstRun(ApiClient apiClient)
      throws ApiException, URISyntaxException {
    DeploymentApi deploymentApi = new DeploymentApi(apiClient);
    final File file = Path
        .of(Resources.getResource("migration/03a4c904-c91d-447f-ab59-27a43b52c2fd.gz").toURI())
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

  @NotNull
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
