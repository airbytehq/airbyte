/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.standardtest.destination

import com.fasterxml.jackson.databind.JsonNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.extensions.grantAllPermissions
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.features.FeatureFlags
import io.airbyte.commons.features.FeatureFlagsWrapper
import io.airbyte.commons.lang.Exceptions
import io.airbyte.configoss.WorkerDestinationConfig
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.workers.exception.TestHarnessException
import io.airbyte.workers.helper.ConnectorConfigUpdater
import io.airbyte.workers.internal.AirbyteDestination
import io.airbyte.workers.internal.DefaultAirbyteDestination
import io.airbyte.workers.process.AirbyteIntegrationLauncher
import io.airbyte.workers.process.DockerProcessFactory
import io.airbyte.workers.process.ProcessFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.attribute.PosixFilePermission
import java.util.*
import java.util.function.Consumer
import kotlin.io.path.setPosixFilePermissions
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.mockito.Mockito

private val LOGGER = KotlinLogging.logger {}

@SuppressFBWarnings("NP_NONNULL_RETURN_VIOLATION")
abstract class BaseDestinationAcceptanceTest(
    // If false, ignore counts and only verify the final state message.
    protected val verifyIndividualStateAndCounts: Boolean = false,
) {
    protected lateinit var processFactory: ProcessFactory
        private set
    protected lateinit var jobRoot: Path
        private set
    protected var localRoot: Path? = null
        private set
    protected lateinit var testEnv: DestinationAcceptanceTest.TestDestinationEnv
        private set
    protected var fileTransferMountSource: Path? = null
        private set
    protected open val supportsFileTransfer: Boolean = false
    protected var testSchemas: HashSet<String> = HashSet()
    protected lateinit var mConnectorConfigUpdater: ConnectorConfigUpdater
        private set
    protected open val isCloudTest: Boolean = true
    protected val featureFlags: FeatureFlags =
        if (isCloudTest) {
            FeatureFlagsWrapper.overridingDeploymentMode(EnvVariableFeatureFlags(), "CLOUD")
        } else {
            FeatureFlagsWrapper.overridingDeploymentMode(EnvVariableFeatureFlags(), "OSS")
        }
    protected abstract val imageName: String
        /**
         * Name of the docker image that the tests will run against.
         *
         * @return docker image name
         */
        get

    /**
     * Configuration specific to the integration. Will be passed to integration where appropriate in
     * each test. Should be valid.
     *
     * @return integration-specific configuration
     */
    @Throws(Exception::class) protected abstract fun getConfig(): JsonNode

    protected open fun supportsInDestinationNormalization(): Boolean {
        return false
    }

    protected fun inDestinationNormalizationFlags(shouldNormalize: Boolean): Map<String, String> {
        if (shouldNormalize && supportsInDestinationNormalization()) {
            return java.util.Map.of("NORMALIZATION_TECHNIQUE", "LEGACY")
        }
        return emptyMap()
    }

    protected fun getDestinationConfig(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
    ): WorkerDestinationConfig {
        return WorkerDestinationConfig()
            .withConnectionId(UUID.randomUUID())
            .withCatalog(
                DestinationAcceptanceTest.convertProtocolObject(
                    catalog,
                    io.airbyte.protocol.models.ConfiguredAirbyteCatalog::class.java
                )
            )
            .withDestinationConnectionConfiguration(config)
    }

    protected fun runSyncAndVerifyStateOutput(
        config: JsonNode,
        messages: List<AirbyteMessage>,
        catalog: ConfiguredAirbyteCatalog,
        runNormalization: Boolean,
    ) {
        runSyncAndVerifyStateOutput(
            config,
            messages,
            catalog,
            runNormalization,
            imageName,
            verifyIndividualStateAndCounts
        )
    }

    @Throws(Exception::class)
    protected fun runSyncAndVerifyStateOutput(
        config: JsonNode,
        messages: List<AirbyteMessage>,
        catalog: ConfiguredAirbyteCatalog,
        runNormalization: Boolean,
        imageName: String,
        verifyIndividualStateAndCounts: Boolean
    ) {
        val destinationOutput = runSync(config, messages, catalog, runNormalization, imageName)

        var expected = messages.filter { it.type == AirbyteMessage.Type.STATE }
        var actual = destinationOutput.filter { it.type == AirbyteMessage.Type.STATE }

        if (verifyIndividualStateAndCounts) {
            /* Collect the counts and add them to each expected state message */
            val stateToCount = mutableMapOf<JsonNode, Int>()
            messages.fold(0) { acc, message ->
                if (message.type == AirbyteMessage.Type.STATE) {
                    stateToCount[message.state.global.sharedState] = acc
                    0
                } else {
                    acc + 1
                }
            }

            expected.forEach { message ->
                val clone = message.state
                clone.destinationStats =
                    AirbyteStateStats()
                        .withRecordCount(stateToCount[clone.global.sharedState]!!.toDouble())
                message.state = clone
            }
        } else {
            /* Null the stats and collect only the final messages */
            val finalActual =
                actual.lastOrNull()
                    ?: throw IllegalArgumentException(
                        "All message sets used for testing should include a state record"
                    )
            val clone = finalActual.state
            clone.destinationStats = null
            finalActual.state = clone

            expected = listOf(expected.last())
            actual = listOf(finalActual)
        }

        Assertions.assertEquals(expected, actual)
    }

    @Throws(Exception::class)
    open protected fun runSync(
        config: JsonNode,
        messages: List<AirbyteMessage>,
        catalog: ConfiguredAirbyteCatalog,
        runNormalization: Boolean,
        imageName: String,
        additionalEnvs: Map<String, String> = mapOf()
    ): List<AirbyteMessage> {
        val destinationConfig = getDestinationConfig(config, catalog)
        return runSync(messages, runNormalization, imageName, destinationConfig, additionalEnvs)
    }

    @Throws(Exception::class)
    protected fun runSync(
        messages: List<AirbyteMessage>,
        runNormalization: Boolean,
        imageName: String,
        destinationConfig: WorkerDestinationConfig,
        additionalEnvs: Map<String, String> = mapOf()
    ): List<AirbyteMessage> {
        val destination = getDestination(imageName)

        destination.start(
            destinationConfig,
            jobRoot,
            additionalEnvs + inDestinationNormalizationFlags(runNormalization)
        )
        messages.forEach(
            Consumer { message: AirbyteMessage ->
                Exceptions.toRuntime {
                    destination.accept(
                        DestinationAcceptanceTest.convertProtocolObject(
                            message,
                            io.airbyte.protocol.models.AirbyteMessage::class.java
                        )
                    )
                }
            }
        )
        destination.notifyEndOfInput()

        val destinationOutput: MutableList<AirbyteMessage> = ArrayList()
        while (!destination.isFinished()) {
            destination.attemptRead().ifPresent {
                destinationOutput.add(
                    DestinationAcceptanceTest.convertProtocolObject(it, AirbyteMessage::class.java)
                )
            }
        }

        try {
            destination.close()
        } catch (e: TestHarnessException) {
            throw TestHarnessException(e.message, e, destinationOutput)
        }

        return destinationOutput
    }

    protected fun getDestination(imageName: String): AirbyteDestination {
        return DefaultAirbyteDestination(
            integrationLauncher =
                AirbyteIntegrationLauncher(
                    DestinationAcceptanceTest.JOB_ID,
                    DestinationAcceptanceTest.JOB_ATTEMPT,
                    imageName,
                    processFactory,
                    null,
                    null,
                    false,
                    featureFlags
                )
        )
    }

    @BeforeEach
    @Throws(Exception::class)
    open fun setUpInternal() {
        val testDir = Path.of("/tmp/airbyte_tests/")
        // Allow ourselves and our connector access to our test dir
        Files.createDirectories(testDir)
            .grantAllPermissions()
        val workspaceRoot = Files.createTempDirectory(testDir, "test")
            .grantAllPermissions()
        jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"))
            .grantAllPermissions()
        localRoot = Files.createTempDirectory(testDir, "output")
            .grantAllPermissions()
        LOGGER.info { "${"jobRoot: {}"} $jobRoot" }
        LOGGER.info { "${"localRoot: {}"} $localRoot" }
        testEnv = DestinationAcceptanceTest.TestDestinationEnv(localRoot)
        mConnectorConfigUpdater = Mockito.mock(ConnectorConfigUpdater::class.java)
        testSchemas = HashSet()
        setup(testEnv, testSchemas)
        fileTransferMountSource =
            if (supportsFileTransfer)
                Files.createTempDirectory(testDir, "file_transfer")
                    .grantAllPermissions()
            else null

        processFactory =
            DockerProcessFactory(
                workspaceRoot,
                workspaceRoot.toString(),
                localRoot.toString(),
                fileTransferMountSource,
                "host",
                getConnectorEnv()
            )
    }

    /**
     * Function that performs any setup of external resources required for the test. e.g.
     * instantiate a postgres database. This function will be called before EACH test.
     *
     * @param testEnv
     * - information about the test environment.
     * @param TEST_SCHEMAS
     * @throws Exception
     * - can throw any exception, test framework will handle.
     */
    @Throws(Exception::class)
    protected abstract fun setup(
        testEnv: DestinationAcceptanceTest.TestDestinationEnv,
        TEST_SCHEMAS: HashSet<String>
    )

    open fun getConnectorEnv(): Map<String, String> {
        return emptyMap()
    }
}
