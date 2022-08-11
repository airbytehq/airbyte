/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.State;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.general.DefaultCheckConnectionWorker;
import io.airbyte.workers.general.DefaultDiscoverCatalogWorker;
import io.airbyte.workers.general.DefaultGetSpecWorker;
import io.airbyte.workers.helper.EntrypointEnvChecker;
import io.airbyte.workers.internal.AirbyteSource;
import io.airbyte.workers.internal.DefaultAirbyteSource;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.DockerProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This abstract class contains helpful functionality and boilerplate for testing a source
 * connector.
 */
public abstract class AbstractSourceConnectorTest {

  protected static final Logger LOGGER = LoggerFactory.getLogger(AbstractSourceConnectorTest.class);
  private TestDestinationEnv environment;
  private Path jobRoot;
  protected Path localRoot;
  private ProcessFactory processFactory;

  private static final String JOB_ID = String.valueOf(0L);
  private static final int JOB_ATTEMPT = 0;

  private static final String CPU_REQUEST_FIELD_NAME = "cpuRequest";
  private static final String CPU_LIMIT_FIELD_NAME = "cpuLimit";
  private static final String MEMORY_REQUEST_FIELD_NAME = "memoryRequest";
  private static final String MEMORY_LIMIT_FIELD_NAME = "memoryLimit";

  /**
   * Name of the docker image that the tests will run against.
   *
   * @return docker image name
   */
  protected abstract String getImageName();

  /**
   * Configuration specific to the integration. Will be passed to integration where appropriate in
   * each test. Should be valid.
   *
   * @return integration-specific configuration
   */
  protected abstract JsonNode getConfig() throws Exception;

  /**
   * Function that performs any setup of external resources required for the test. e.g. instantiate a
   * postgres database. This function will be called before EACH test.
   *
   * @param environment - information about the test environment.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  protected abstract void setupEnvironment(TestDestinationEnv environment) throws Exception;

  /**
   * Function that performs any clean up of external resources required for the test. e.g. delete a
   * postgres database. This function will be called after EACH test. It MUST remove all data in the
   * destination so that there is no contamination across tests.
   *
   * @param testEnv - information about the test environment.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  protected abstract void tearDown(TestDestinationEnv testEnv) throws Exception;

  private WorkerConfigs workerConfigs;

  @BeforeEach
  public void setUpInternal() throws Exception {
    final Path testDir = Path.of("/tmp/airbyte_tests/");
    Files.createDirectories(testDir);
    final Path workspaceRoot = Files.createTempDirectory(testDir, "test");
    jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"));
    localRoot = Files.createTempDirectory(testDir, "output");
    environment = new TestDestinationEnv(localRoot);
    workerConfigs = new WorkerConfigs(new EnvConfigs());
    processFactory = new DockerProcessFactory(
        workerConfigs,
        workspaceRoot,
        workspaceRoot.toString(),
        localRoot.toString(),
        "host");

    setupEnvironment(environment);
  }

  @AfterEach
  public void tearDownInternal() throws Exception {
    tearDown(environment);
  }

  protected ConnectorSpecification runSpec() throws WorkerException {
    return new DefaultGetSpecWorker(
        workerConfigs,
        new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, workerConfigs.getResourceRequirements()))
            .run(new JobGetSpecConfig().withDockerImage(getImageName()), jobRoot).getSpec();
  }

  protected StandardCheckConnectionOutput runCheck() throws Exception {
    return new DefaultCheckConnectionWorker(
        workerConfigs,
        new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, workerConfigs.getResourceRequirements()))
            .run(new StandardCheckConnectionInput().withConnectionConfiguration(getConfig()), jobRoot).getCheckConnection();
  }

  protected String runCheckAndGetStatusAsString(final JsonNode config) throws Exception {
    return new DefaultCheckConnectionWorker(
        workerConfigs,
        new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, workerConfigs.getResourceRequirements()))
            .run(new StandardCheckConnectionInput().withConnectionConfiguration(config), jobRoot).getCheckConnection().getStatus().toString();
  }

  protected AirbyteCatalog runDiscover() throws Exception {
    return new DefaultDiscoverCatalogWorker(
        workerConfigs,
        new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, workerConfigs.getResourceRequirements()))
            .run(new StandardDiscoverCatalogInput().withConnectionConfiguration(getConfig()), jobRoot).getDiscoverCatalog();
  }

  protected void checkEntrypointEnvVariable() throws Exception {
    final String entrypoint = EntrypointEnvChecker.getEntrypointEnvVariable(
        processFactory,
        String.valueOf(JOB_ID),
        JOB_ATTEMPT,
        jobRoot,
        getImageName());

    assertNotNull(entrypoint);
    assertFalse(entrypoint.isBlank());
  }

  protected List<AirbyteMessage> runRead(final ConfiguredAirbyteCatalog configuredCatalog) throws Exception {
    return runRead(configuredCatalog, null);
  }

  // todo (cgardens) - assume no state since we are all full refresh right now.
  protected List<AirbyteMessage> runRead(final ConfiguredAirbyteCatalog catalog, final JsonNode state) throws Exception {
    final WorkerSourceConfig sourceConfig = new WorkerSourceConfig()
        .withSourceConnectionConfiguration(getConfig())
        .withState(state == null ? null : new State().withState(state))
        .withCatalog(catalog);

    final AirbyteSource source = new DefaultAirbyteSource(workerConfigs,
        new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, workerConfigs.getResourceRequirements()));
    final List<AirbyteMessage> messages = new ArrayList<>();
    source.start(sourceConfig, jobRoot);
    while (!source.isFinished()) {
      source.attemptRead().ifPresent(messages::add);
    }
    source.close();

    return messages;
  }

  protected Map<String, Integer> runReadVerifyNumberOfReceivedMsgs(final ConfiguredAirbyteCatalog catalog,
                                                                   final JsonNode state,
                                                                   final Map<String, Integer> mapOfExpectedRecordsCount)
      throws Exception {

    final WorkerSourceConfig sourceConfig = new WorkerSourceConfig()
        .withSourceConnectionConfiguration(getConfig())
        .withState(state == null ? null : new State().withState(state))
        .withCatalog(catalog);

    final Map<String, String> mapOfResourceRequirementsParams = prepareResourceRequestMapBySystemProperties();
    final AirbyteSource source =
        prepareAirbyteSource(!mapOfResourceRequirementsParams.isEmpty() ? prepareResourceRequirements(mapOfResourceRequirementsParams) : null);
    source.start(sourceConfig, jobRoot);

    while (!source.isFinished()) {
      final Optional<AirbyteMessage> airbyteMessageOptional = source.attemptRead();
      if (airbyteMessageOptional.isPresent() && airbyteMessageOptional.get().getType().equals(Type.RECORD)) {
        final AirbyteMessage airbyteMessage = airbyteMessageOptional.get();
        final AirbyteRecordMessage record = airbyteMessage.getRecord();

        final String streamName = record.getStream();
        mapOfExpectedRecordsCount.put(streamName, mapOfExpectedRecordsCount.get(streamName) - 1);
      }
    }
    source.close();
    return mapOfExpectedRecordsCount;
  }

  protected ResourceRequirements prepareResourceRequirements(final Map<String, String> mapOfResourceRequirementsParams) {
    return new ResourceRequirements().withCpuRequest(mapOfResourceRequirementsParams.get(CPU_REQUEST_FIELD_NAME))
        .withCpuLimit(mapOfResourceRequirementsParams.get(CPU_LIMIT_FIELD_NAME))
        .withMemoryRequest(mapOfResourceRequirementsParams.get(MEMORY_REQUEST_FIELD_NAME))
        .withMemoryLimit(mapOfResourceRequirementsParams.get(MEMORY_LIMIT_FIELD_NAME));
  }

  private AirbyteSource prepareAirbyteSource(final ResourceRequirements resourceRequirements) {
    final var workerConfigs = new WorkerConfigs(new EnvConfigs());
    final var integrationLauncher = resourceRequirements == null
        ? new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, workerConfigs.getResourceRequirements())
        : new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, resourceRequirements);
    return new DefaultAirbyteSource(workerConfigs, integrationLauncher);
  }

  private static Map<String, String> prepareResourceRequestMapBySystemProperties() {
    var cpuLimit = System.getProperty(CPU_LIMIT_FIELD_NAME);
    var memoryLimit = System.getProperty(MEMORY_LIMIT_FIELD_NAME);
    final var workerConfigs = new WorkerConfigs(new EnvConfigs());
    if (cpuLimit.isBlank() || cpuLimit.isEmpty()) {
      cpuLimit = workerConfigs.getResourceRequirements().getCpuLimit();
    }
    if (memoryLimit.isBlank() || memoryLimit.isEmpty()) {
      memoryLimit = workerConfigs.getResourceRequirements().getMemoryLimit();
    }
    LOGGER.info("Container CPU Limit = {}", cpuLimit);
    LOGGER.info("Container Memory Limit = {}", memoryLimit);
    final Map<String, String> result = new HashMap<>();
    result.put(CPU_REQUEST_FIELD_NAME, workerConfigs.getResourceRequirements().getCpuRequest());
    result.put(CPU_LIMIT_FIELD_NAME, cpuLimit);
    result.put(MEMORY_REQUEST_FIELD_NAME, workerConfigs.getResourceRequirements().getMemoryRequest());
    result.put(MEMORY_LIMIT_FIELD_NAME, memoryLimit);
    return result;
  }

}
