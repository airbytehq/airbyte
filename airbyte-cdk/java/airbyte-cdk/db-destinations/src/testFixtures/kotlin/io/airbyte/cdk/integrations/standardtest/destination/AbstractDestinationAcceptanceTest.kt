package io.airbyte.cdk.integrations.standardtest.destination;

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.features.FeatureFlags
import io.airbyte.commons.features.FeatureFlagsWrapper
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.lang.Exceptions
import io.airbyte.configoss.JobGetSpecConfig
import io.airbyte.configoss.WorkerDestinationConfig
import io.airbyte.protocol.models.v0.*
import io.airbyte.workers.exception.TestHarnessException
import io.airbyte.workers.general.DefaultGetSpecTestHarness
import io.airbyte.workers.internal.AirbyteDestination
import io.airbyte.workers.internal.DefaultAirbyteDestination
import io.airbyte.workers.normalization.DefaultNormalizationRunner
import io.airbyte.workers.normalization.NormalizationRunner
import io.airbyte.workers.process.AirbyteIntegrationLauncher
import io.airbyte.workers.process.DockerProcessFactory
import io.airbyte.workers.process.ProcessFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import java.nio.file.Files
import java.nio.file.Path
import java.util.*
import java.util.function.Consumer

private val LOGGER = KotlinLogging.logger {}

abstract class AbstractDestinationAcceptanceTest(
    override val verifyIndividualStateAndCounts: Boolean = false,
): BaseDestinationAcceptanceTest {
    protected var localRoot: Path? = null
        private set
    override lateinit var jobRoot: Path
    override lateinit var processFactory: ProcessFactory
    override lateinit var testEnv: TestDestinationEnv
    protected var fileTransferMountSource: Path? = null
        private set

    override val isCloudTest: Boolean = true




    class TestDestinationEnv(val localRoot: Path?) {
        override fun toString(): String {
            return "TestDestinationEnv{" + "localRoot=" + localRoot + '}'
        }
    }

    open fun getConnectorEnv(): Map<String, String> {
        return emptyMap()
    }

    @Throws(Exception::class)
    override fun runSyncAndVerifyStateOutput(
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
                    stateToCount[message.state.data] = acc
                    0
                } else {
                    acc + 1
                }
            }

            expected.forEach { message ->
                val clone = message.state
                clone.destinationStats =
                    AirbyteStateStats().withRecordCount(stateToCount[clone.data]!!.toDouble())
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
    private fun runSync(
        config: JsonNode,
        messages: List<AirbyteMessage>,
        catalog: ConfiguredAirbyteCatalog,
        runNormalization: Boolean,
        imageName: String,
    ): List<AirbyteMessage> {
        val destinationConfig =
            WorkerDestinationConfig()
                .withConnectionId(UUID.randomUUID())
                .withCatalog(
                    convertProtocolObject(
                        catalog,
                        io.airbyte.protocol.models.ConfiguredAirbyteCatalog::class.java
                    )
                )
                .withDestinationConnectionConfiguration(config)

        val destination = getDestination(imageName)

        destination.start(
            destinationConfig,
            jobRoot,
            inDestinationNormalizationFlags(runNormalization)
        )
        messages.forEach(
            Consumer { message: AirbyteMessage ->
                Exceptions.toRuntime {
                    destination.accept(
                        convertProtocolObject(
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
                destinationOutput.add(convertProtocolObject(it, AirbyteMessage::class.java))
            }
        }

        destination.close()

        if (!runNormalization || (supportsInDestinationNormalization())) {
            return destinationOutput
        }

        val runner: NormalizationRunner =
            DefaultNormalizationRunner(
                processFactory,
                getNormalizationImageName(),
                getNormalizationIntegrationType()
            )
        runner.start()
        val normalizationRoot = Files.createDirectories(jobRoot.resolve("normalize"))
        if (
            !runner.normalize(
                JOB_ID,
                JOB_ATTEMPT,
                normalizationRoot,
                destinationConfig.destinationConnectionConfiguration,
                destinationConfig.catalog,
                null
            )
        ) {
            throw TestHarnessException("Normalization Failed.")
        }
        runner.close()
        return destinationOutput
    }

    private fun getDestination(imageName: String): AirbyteDestination {
        return DefaultAirbyteDestination(
            integrationLauncher =
            AirbyteIntegrationLauncher(
                JOB_ID,
                JOB_ATTEMPT,
                imageName,
                processFactory,
                null,
                null,
                false,
                featureFlags
            )
        )
    }

    abstract fun inDestinationNormalizationFlags(shouldNormalize: Boolean): Map<String, String>

    abstract fun getNormalizationImageName(): String?

    abstract fun getNormalizationIntegrationType(): String?

    @Throws(TestHarnessException::class)
    override fun runSpec(): ConnectorSpecification {
        return convertProtocolObject(
            DefaultGetSpecTestHarness(
                AirbyteIntegrationLauncher(
                    JOB_ID,
                    JOB_ATTEMPT,
                    imageName,
                    processFactory,
                    null,
                    null,
                    false,
                    featureFlags
                )
            )
                .run(JobGetSpecConfig().withDockerImage(imageName), jobRoot)
                .spec,
            ConnectorSpecification::class.java
        )
    }

    @BeforeEach
    fun setupBase() {
        val testDir = Path.of("/tmp/airbyte_tests/")
        Files.createDirectories(testDir)
        val workspaceRoot = Files.createTempDirectory(testDir, "test")
        jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"))
        localRoot = Files.createTempDirectory(testDir, "output")
        LOGGER.info { "${"jobRoot: {}"} $jobRoot" }
        LOGGER.info { "${"localRoot: {}"} $localRoot" }
        testEnv = TestDestinationEnv(localRoot)
        fileTransferMountSource = Files.createTempDirectory(testDir, "file_transfer")

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

    companion object {
        @JvmStatic
        val JOB_ID = "0"
        @JvmStatic
         val JOB_ATTEMPT = 0

        fun <V0, V1> convertProtocolObject(v1: V1, klass: Class<V0>): V0 {
            return Jsons.`object`(Jsons.jsonNode(v1), klass)!!
        }
    }
}
