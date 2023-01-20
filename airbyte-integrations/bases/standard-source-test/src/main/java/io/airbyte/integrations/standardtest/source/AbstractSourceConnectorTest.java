/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.State;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.general.DefaultCheckConnectionWorker;
import io.airbyte.workers.general.DefaultDiscoverCatalogWorker;
import io.airbyte.workers.general.DefaultGetSpecWorker;
import io.airbyte.workers.helper.ConnectorConfigUpdater;
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
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.mockito.ArgumentCaptor;
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

  private static final UUID SOURCE_ID = UUID.randomUUID();

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

  private ConfigRepository mConfigRepository;
  private ConnectorConfigUpdater mConnectorConfigUpdater;

  // This has to be using the protocol version of the platform in order to capture the arg
  private final ArgumentCaptor<io.airbyte.protocol.models.AirbyteCatalog> lastPersistedCatalog =
      ArgumentCaptor.forClass(io.airbyte.protocol.models.AirbyteCatalog.class);

  protected AirbyteCatalog getLastPersistedCatalog() {
    return convertProtocolObject(lastPersistedCatalog.getValue(), AirbyteCatalog.class);
  }

  @BeforeEach
  public void setUpInternal() throws Exception {
    final Path testDir = Path.of("/tmp/airbyte_tests/");
    Files.createDirectories(testDir);
    final Path workspaceRoot = Files.createTempDirectory(testDir, "test");
    jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"));
    localRoot = Files.createTempDirectory(testDir, "output");
    environment = new TestDestinationEnv(localRoot);
    setupEnvironment(environment);
    workerConfigs = new WorkerConfigs(new EnvConfigs());
    mConfigRepository = mock(ConfigRepository.class);
    mConnectorConfigUpdater = mock(ConnectorConfigUpdater.class);
    processFactory = new DockerProcessFactory(
        workerConfigs,
        workspaceRoot,
        workspaceRoot.toString(),
        localRoot.toString(),
        "host");

    postSetup();
  }

  /**
   * Override this method if you want to do any per-test setup that depends on being able to e.g.
   * {@link #runRead(ConfiguredAirbyteCatalog)}.
   */
  protected void postSetup() throws Exception {}

  @AfterEach
  public void tearDownInternal() throws Exception {
    tearDown(environment);
  }

  protected ConnectorSpecification runSpec() throws WorkerException {
    final io.airbyte.protocol.models.ConnectorSpecification spec = new DefaultGetSpecWorker(
        new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, workerConfigs.getResourceRequirements(), null, false,
            new EnvVariableFeatureFlags()))
                .run(new JobGetSpecConfig().withDockerImage(getImageName()), jobRoot).getSpec();
    return convertProtocolObject(spec, ConnectorSpecification.class);
  }

  protected StandardCheckConnectionOutput runCheck() throws Exception {
    return new DefaultCheckConnectionWorker(
        new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, workerConfigs.getResourceRequirements(), null, false,
            new EnvVariableFeatureFlags()),
        mConnectorConfigUpdater)
            .run(new StandardCheckConnectionInput().withConnectionConfiguration(getConfig()), jobRoot).getCheckConnection();
  }

  protected String runCheckAndGetStatusAsString(final JsonNode config) throws Exception {
    return new DefaultCheckConnectionWorker(
        new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, workerConfigs.getResourceRequirements(), null, false,
            new EnvVariableFeatureFlags()),
        mConnectorConfigUpdater)
            .run(new StandardCheckConnectionInput().withConnectionConfiguration(config), jobRoot).getCheckConnection().getStatus().toString();
  }

  protected UUID runDiscover() throws Exception {
    final UUID toReturn = new DefaultDiscoverCatalogWorker(
        mConfigRepository,
        new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, workerConfigs.getResourceRequirements(), null, false,
            new EnvVariableFeatureFlags()),
        mConnectorConfigUpdater)
            .run(new StandardDiscoverCatalogInput().withSourceId(SOURCE_ID.toString()).withConnectionConfiguration(getConfig()), jobRoot)
            .getDiscoverCatalogId();
    verify(mConfigRepository).writeActorCatalogFetchEvent(lastPersistedCatalog.capture(), any(), any(), any());
    return toReturn;
  }

  protected void checkEntrypointEnvVariable() throws Exception {
    final String entrypoint = EntrypointEnvChecker.getEntrypointEnvVariable(
        processFactory,
        JOB_ID,
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
        .withCatalog(convertProtocolObject(catalog, io.airbyte.protocol.models.ConfiguredAirbyteCatalog.class));

    final var featureFlags = new EnvVariableFeatureFlags();

    final AirbyteSource source = new DefaultAirbyteSource(
        new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, workerConfigs.getResourceRequirements(), null, false,
            featureFlags),
        featureFlags);
    final List<AirbyteMessage> messages = new ArrayList<>();
    source.start(sourceConfig, jobRoot);
    while (!source.isFinished()) {
      source.attemptRead().ifPresent(m -> messages.add(convertProtocolObject(m, AirbyteMessage.class)));
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
        .withCatalog(convertProtocolObject(catalog, io.airbyte.protocol.models.ConfiguredAirbyteCatalog.class));

    final Map<String, String> mapOfResourceRequirementsParams = prepareResourceRequestMapBySystemProperties();
    final AirbyteSource source =
        prepareAirbyteSource(!mapOfResourceRequirementsParams.isEmpty() ? prepareResourceRequirements(mapOfResourceRequirementsParams) : null);
    source.start(sourceConfig, jobRoot);

    while (!source.isFinished()) {
      final Optional<AirbyteMessage> airbyteMessageOptional = source.attemptRead().map(m -> convertProtocolObject(m, AirbyteMessage.class));
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
    final var featureFlags = new EnvVariableFeatureFlags();
    final var integrationLauncher = resourceRequirements == null
        ? new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, workerConfigs.getResourceRequirements(), null, false,
            featureFlags)
        : new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, resourceRequirements, null, false, featureFlags);
    return new DefaultAirbyteSource(integrationLauncher, featureFlags);
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

  private static <V0, V1> V0 convertProtocolObject(final V1 v1, final Class<V0> klass) {
    return Jsons.object(Jsons.jsonNode(v1), klass);
  }

}
