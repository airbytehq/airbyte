/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.airbyte_test_container;

import com.google.api.client.util.Preconditions;
import com.google.common.collect.Maps;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.generated.HealthApi;
import io.airbyte.api.client.invoker.generated.ApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.commons.concurrency.WaitingUtils;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;
import java.util.Scanner;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Consumer;
import java.util.function.Supplier;
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
  public void startBlocking() throws IOException, InterruptedException {
    startAsync();
    waitForAirbyte();
  }

  @SuppressWarnings({"unchecked", "rawtypes"})
  public void startAsync() throws IOException, InterruptedException {
    final File cleanedDockerComposeFile = prepareDockerComposeFile(dockerComposeFile);
    dockerComposeContainer = new DockerComposeContainer(cleanedDockerComposeFile).withEnv(env);
    // Only expose logs related to db migrations.
    serviceLogConsumer(dockerComposeContainer, "init");
    serviceLogConsumer(dockerComposeContainer, "bootloader");
    serviceLogConsumer(dockerComposeContainer, "db");
    serviceLogConsumer(dockerComposeContainer, "seed");
    serviceLogConsumer(dockerComposeContainer, "server");

    dockerComposeContainer.start();
  }

  private static Map<String, String> prepareDockerComposeEnvVariables(final File envFile) throws IOException {
    LOGGER.info("Searching for environment in {}", envFile);
    Preconditions.checkArgument(envFile.exists(), "could not find docker compose environment");

    final Properties prop = new Properties();
    prop.load(new FileInputStream(envFile));
    return Maps.fromProperties(prop);
  }

  /**
   * TestContainers docker compose files cannot have container_names, so we filter them.
   */
  private static File prepareDockerComposeFile(final File originalDockerComposeFile) throws IOException {
    final File cleanedDockerComposeFile = Files.createTempFile(Path.of("/tmp"), "docker_compose", "acceptance_test").toFile();

    try (final Scanner scanner = new Scanner(originalDockerComposeFile, StandardCharsets.UTF_8)) {
      try (final FileWriter fileWriter = new FileWriter(cleanedDockerComposeFile, StandardCharsets.UTF_8)) {
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

    final AtomicReference<ApiException> lastException = new AtomicReference<>();
    final AtomicInteger attempt = new AtomicInteger();
    final Supplier<Boolean> condition = () -> {
      try {
        healthApi.getHealthCheck();
        return true;
      } catch (final ApiException e) {
        lastException.set(e);
        LOGGER.info("airbyte not ready yet. attempt: {}", attempt.incrementAndGet());
        return false;
      }
    };

    if (!WaitingUtils.waitForCondition(Duration.ofSeconds(5), Duration.ofMinutes(2), condition)) {
      throw new IllegalStateException("Airbyte took too long to start. Including last exception.", lastException.get());
    }
  }

  private void serviceLogConsumer(final DockerComposeContainer<?> composeContainer, final String service) {
    composeContainer.withLogConsumer(service, logConsumer(service, customServiceLogListeners.get(service)));
  }

  /**
   * Exposes logs generated by docker containers in docker compose temporal test container.
   *
   *
   * @param service - name of docker container from which log is emitted.
   * @param customConsumer - each line output by the service in docker compose will be passed ot the
   *        consumer. if null do nothing.
   * @return log consumer
   */
  private Consumer<OutputFrame> logConsumer(final String service, final Consumer<String> customConsumer) {
    return c -> {
      if (c != null && c.getBytes() != null) {
        final String log = new String(c.getBytes(), StandardCharsets.UTF_8);
        if (customConsumer != null) {
          customConsumer.accept(log);
        }

        final String message = prependService(service, log.replace("\n", ""));
        switch (c.getType()) {
          // prefer matching log levels from docker containers with log levels in logger.
          case STDOUT -> LOGGER.info(message);
          case STDERR -> LOGGER.error(message);
          // assumption that this is an empty frame that connotes the container exiting.
          case END -> LOGGER.error(service + " stopped!!!");
        }
      }
    };
  }

  private String prependService(final String service, final String message) {
    return service + " - " + message;
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
    } catch (final InvocationTargetException | IllegalAccessException | NoSuchMethodException | NoSuchFieldException e) {
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

    public Builder(final File dockerComposeFile) {
      this.dockerComposeFile = dockerComposeFile;
      this.customServiceLogListeners = new HashMap<>();
      this.env = new HashMap<>();
    }

    public Builder setEnv(final Properties env) {
      this.env.putAll(Maps.fromProperties(env));
      return this;
    }

    public Builder setEnv(final Map<String, String> env) {
      this.env.putAll(env);
      return this;
    }

    public Builder setEnvVariable(final String propertyName, final String propertyValue) {
      this.env.put(propertyName, propertyValue);
      return this;
    }

    public Builder setLogListener(final String serviceName, final Consumer<String> logConsumer) {
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
