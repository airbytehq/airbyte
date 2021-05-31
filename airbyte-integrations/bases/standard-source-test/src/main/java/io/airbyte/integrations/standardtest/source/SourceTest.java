package io.airbyte.integrations.standardtest.source;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.*;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.DefaultCheckConnectionWorker;
import io.airbyte.workers.DefaultDiscoverCatalogWorker;
import io.airbyte.workers.DefaultGetSpecWorker;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.DockerProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.protocols.airbyte.AirbyteSource;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteSource;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public abstract class SourceTest {

    private TestDestinationEnv testEnv;
    private Path jobRoot;
    protected Path localRoot;
    private ProcessFactory processFactory;

    private static final long JOB_ID = 0L;
    private static final int JOB_ATTEMPT = 0;

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
     * @param testEnv - information about the test environment.
     * @throws Exception - can throw any exception, test framework will handle.
     */
    protected abstract void setup(TestDestinationEnv testEnv) throws Exception;

    /**
     * Function that performs any clean up of external resources required for the test. e.g. delete a
     * postgres database. This function will be called after EACH test. It MUST remove all data in the
     * destination so that there is no contamination across tests.
     *
     * @param testEnv - information about the test environment.
     * @throws Exception - can throw any exception, test framework will handle.
     */
    protected abstract void tearDown(TestDestinationEnv testEnv) throws Exception;

    @BeforeEach
    public void setUpInternal() throws Exception {
        final Path testDir = Path.of("/tmp/airbyte_tests/");
        Files.createDirectories(testDir);
        final Path workspaceRoot = Files.createTempDirectory(testDir, "test");
        jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"));
        localRoot = Files.createTempDirectory(testDir, "output");
        testEnv = new TestDestinationEnv(localRoot);

        setup(testEnv);

        processFactory = new DockerProcessFactory(
                workspaceRoot,
                workspaceRoot.toString(),
                localRoot.toString(),
                "host");
    }

    @AfterEach
    public void tearDownInternal() throws Exception {
        tearDown(testEnv);
    }

    protected ConnectorSpecification runSpec() throws WorkerException {
        return new DefaultGetSpecWorker(new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory))
                .run(new JobGetSpecConfig().withDockerImage(getImageName()), jobRoot);
    }

    protected StandardCheckConnectionOutput runCheck() throws Exception {
        return new DefaultCheckConnectionWorker(new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory))
                .run(new StandardCheckConnectionInput().withConnectionConfiguration(getConfig()), jobRoot);
    }

    protected AirbyteCatalog runDiscover() throws Exception {
        return new DefaultDiscoverCatalogWorker(new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory))
                .run(new StandardDiscoverCatalogInput().withConnectionConfiguration(getConfig()), jobRoot);
    }

    protected List<AirbyteMessage> runRead(ConfiguredAirbyteCatalog configuredCatalog) throws Exception {
        return runRead(configuredCatalog, null);
    }

    // todo (cgardens) - assume no state since we are all full refresh right now.
    protected List<AirbyteMessage> runRead(ConfiguredAirbyteCatalog catalog, JsonNode state) throws Exception {
        final StandardTapConfig sourceConfig = new StandardTapConfig()
                .withSourceConnectionConfiguration(getConfig())
                .withState(state == null ? null : new State().withState(state))
                .withCatalog(catalog);

        final AirbyteSource source = new DefaultAirbyteSource(new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory));
        final List<AirbyteMessage> messages = new ArrayList<>();
        source.start(sourceConfig, jobRoot);
        while (!source.isFinished()) {
            source.attemptRead().ifPresent(messages::add);
        }
        source.close();

        return messages;
    }

    public static class TestDestinationEnv {

        private final Path localRoot;

        public TestDestinationEnv(Path localRoot) {
            this.localRoot = localRoot;
        }

        public Path getLocalRoot() {
            return localRoot;
        }

    }
}
