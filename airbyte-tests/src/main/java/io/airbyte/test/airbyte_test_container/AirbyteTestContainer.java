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

package io.airbyte.test.airbyte_test_container;

import com.google.api.client.util.Preconditions;
import com.google.common.collect.Maps;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.HealthApi;
import io.airbyte.api.client.invoker.ApiClient;
import io.airbyte.api.client.invoker.ApiException;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;
import java.util.Scanner;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.DockerComposeContainer;
import org.testcontainers.containers.SocatContainer;
import org.testcontainers.containers.output.OutputFrame;

/**
 * The goal of this class is to make it easy to run the Airbyte docker-compose configuration from
 * test containers. This helps make it easy to stop the test container without deleting the volumes
 * { @link AirbyteTestContainer#stopRetainVolumes() }. It waits for Airbyte to be ready. It also
 * handles the nuances of configuring the Airbyte docker-compose configuration in test containers.
 */
public class AirbyteTestContainer {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteTestContainer.class);

  private final File dockerComposeFile;
  private final Map<String, String> env;
  private final Map<String, Consumer<String>> customServiceLogListeners;

  private DockerComposeContainer<?> dockerComposeContainer;

  public AirbyteTestContainer(final File dockerComposeFile,
                              final Map<String, String> env,
                              final Map<String, Consumer<String>> customServiceLogListeners) {
    this.dockerComposeFile = dockerComposeFile;
    this.env = env;
    this.customServiceLogListeners = customServiceLogListeners;
  }

  /**
   * Starts Airbyte docker-compose configuration. Will block until the server is reachable or it times
   * outs.
   */
  @SuppressWarnings({"unchecked", "rawtypes"})
  public void start() throws IOException, InterruptedException {
    final File cleanedDockerComposeFile = prepareDockerComposeFile(dockerComposeFile);
    dockerComposeContainer = new DockerComposeContainer(cleanedDockerComposeFile).withEnv(env);
    serviceLogConsumer(dockerComposeContainer, "init");
    serviceLogConsumer(dockerComposeContainer, "db");
    serviceLogConsumer(dockerComposeContainer, "seed");
    serviceLogConsumer(dockerComposeContainer, "scheduler");
    serviceLogConsumer(dockerComposeContainer, "server");
    serviceLogConsumer(dockerComposeContainer, "webapp");
    serviceLogConsumer(dockerComposeContainer, "worker");
    serviceLogConsumer(dockerComposeContainer, "airbyte-temporal");

    dockerComposeContainer.start();

    waitForAirbyte();
  }

  private static Map<String, String> prepareDockerComposeEnvVariables(File envFile) throws IOException {
    LOGGER.info("Searching for environment in {}", envFile);
    Preconditions.checkArgument(envFile.exists(), "could not find docker compose environment");

    final Properties prop = new Properties();
    prop.load(new FileInputStream(envFile));
    return Maps.fromProperties(prop);
  }

  /**
   * TestContainers docker compose files cannot have container_names, so we filter them.
   */
  private static File prepareDockerComposeFile(File originalDockerComposeFile) throws IOException {
    final File cleanedDockerComposeFile = Files.createTempFile(Path.of("/tmp"), "docker_compose", "acceptance_test").toFile();

    try (final Scanner scanner = new Scanner(originalDockerComposeFile)) {
      try (final FileWriter fileWriter = new FileWriter(cleanedDockerComposeFile)) {
        while (scanner.hasNextLine()) {
          final String s = scanner.nextLine();
          if (s.contains("container_name")) {
            continue;
          }
          fileWriter.write(s);
          fileWriter.write('\n');
        }
      }
    }
    return cleanedDockerComposeFile;
  }

  @SuppressWarnings("BusyWait")
  private static void waitForAirbyte() throws InterruptedException {
    // todo (cgardens) - assumes port 8001 which is misleading since we can start airbyte on other
    // ports. need to make this configurable.
    final AirbyteApiClient apiClient = new AirbyteApiClient(
        new ApiClient().setScheme("http")
            .setHost("localhost")
            .setPort(8001)
            .setBasePath("/api"));

    final HealthApi healthApi = apiClient.getHealthApi();

    ApiException lastException;
    int i = 0;
    while (true) {
      try {
        healthApi.getHealthCheck();
        break;
      } catch (ApiException e) {
        lastException = e;
        LOGGER.info("airbyte not ready yet. attempt: {}", i);
      }
      if (i == 10) {
        throw new IllegalStateException("Airbyte took too long to start. Including last exception.", lastException);
      }
      Thread.sleep(5000);
      i++;
    }
  }

  private void serviceLogConsumer(DockerComposeContainer<?> composeContainer, String service) {
    composeContainer.withLogConsumer(service, logConsumer(customServiceLogListeners.get(service)));
  }

  /**
   * Exposes logs generated by docker containers in docker compose temporal test container.
   *
   * @param customConsumer - each line output by the service in docker compose will be passed ot the
   *        consumer. if null do nothing.
   * @return log consumer
   */
  private Consumer<OutputFrame> logConsumer(Consumer<String> customConsumer) {
    return c -> {
      if (c != null && c.getBytes() != null) {
        final String log = new String(c.getBytes());
        if (customConsumer != null) {
          customConsumer.accept(log);
        }
        LOGGER.info(log.replace("\n", ""));
      }
    };
  }

  /**
   * This stop method will delete any underlying volumes for the docker compose setup.
   */
  public void stop() {
    if (dockerComposeContainer != null) {
      dockerComposeContainer.stop();
    }
  }

  /**
   * This method is hacked from {@link org.testcontainers.containers.DockerComposeContainer#stop()} We
   * needed to do this to avoid removing the volumes when the container is stopped so that the data
   * persists and can be tested against in the second run
   */
  public void stopRetainVolumes() {
    if (dockerComposeContainer == null) {
      return;
    }

    try {
      stopRetainVolumesInternal();
    } catch (InvocationTargetException | IllegalAccessException | NoSuchMethodException | NoSuchFieldException e) {
      throw new RuntimeException(e);
    }
  }

  @SuppressWarnings("rawtypes")
  private void stopRetainVolumesInternal() throws InvocationTargetException, IllegalAccessException, NoSuchMethodException, NoSuchFieldException {
    final Class<? extends DockerComposeContainer> dockerComposeContainerClass = dockerComposeContainer.getClass();
    try {
      final Field ambassadorContainerField = dockerComposeContainerClass.getDeclaredField("ambassadorContainer");
      ambassadorContainerField.setAccessible(true);
      final SocatContainer ambassadorContainer = (SocatContainer) ambassadorContainerField.get(dockerComposeContainer);
      ambassadorContainer.stop();

      final String cmd = "down ";

      final Method runWithComposeMethod = dockerComposeContainerClass.getDeclaredMethod("runWithCompose", String.class);
      runWithComposeMethod.setAccessible(true);
      runWithComposeMethod.invoke(dockerComposeContainer, cmd);

    } finally {
      final Field projectField = dockerComposeContainerClass.getDeclaredField("project");
      projectField.setAccessible(true);

      final Method randomProjectId = dockerComposeContainerClass.getDeclaredMethod("randomProjectId");
      randomProjectId.setAccessible(true);
      final String newProjectValue = (String) randomProjectId.invoke(dockerComposeContainer);

      projectField.set(dockerComposeContainer, newProjectValue);
    }
  }

  public static class Builder {

    private final File dockerComposeFile;
    private final Map<String, String> env;
    private final Map<String, Consumer<String>> customServiceLogListeners;

    public Builder(File dockerComposeFile) {
      this.dockerComposeFile = dockerComposeFile;
      this.customServiceLogListeners = new HashMap<>();
      this.env = new HashMap<>();
    }

    public Builder setEnv(File envFile) throws IOException {
      this.env.putAll(prepareDockerComposeEnvVariables(envFile));
      return this;
    }

    public Builder setEnv(Map<String, String> env) {
      this.env.putAll(env);
      return this;
    }

    public Builder setEnvVariable(String propertyName, String propertyValue) {
      this.env.put(propertyName, propertyValue);
      return this;
    }

    public Builder setLogListener(String serviceName, Consumer<String> logConsumer) {
      this.customServiceLogListeners.put(serviceName, logConsumer);
      return this;
    }

    public AirbyteTestContainer build() {
      // override .env file so that we never report to segment while testing.
      env.put("TRACKING_STRATEGY", "logging");

      LOGGER.info("Using env: {}", env);
      return new AirbyteTestContainer(dockerComposeFile, env, customServiceLogListeners);
    }

  }

}
