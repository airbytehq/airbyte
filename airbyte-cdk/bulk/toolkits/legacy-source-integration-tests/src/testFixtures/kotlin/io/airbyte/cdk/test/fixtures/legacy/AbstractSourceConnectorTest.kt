/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.api.client.AirbyteApiClient
import io.airbyte.api.client.generated.SourceApi
import io.airbyte.api.client.model.generated.DiscoverCatalogResult
import io.airbyte.api.client.model.generated.SourceDiscoverSchemaWriteRequestBody
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConnectorSpecification
import java.nio.file.Files
import java.nio.file.Path
import java.util.*
import kotlin.test.assertNotNull
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.mockito.ArgumentCaptor
import org.mockito.ArgumentMatchers
import org.mockito.Mockito

/**
 * This abstract class contains helpful functionality and boilerplate for testing a source
 * connector.
 */
abstract class AbstractSourceConnectorTest {
    private var environment: TestDestinationEnv? = null
    private lateinit var jobRoot: Path
    protected var localRoot: Path? = null
    private lateinit var processFactory: ProcessFactory

    /** Name of the docker image that the tests will run against. */
    protected abstract val imageName: String

    @get:Throws(Exception::class) protected abstract val config: JsonNode?

    /**
     * Function that performs any setup of external resources required for the test. e.g.
     * instantiate a postgres database. This function will be called before EACH test.
     *
     * @param environment
     * - information about the test environment.
     * @throws Exception
     * - can throw any exception, test framework will handle.
     */
    @Throws(Exception::class)
    protected abstract fun setupEnvironment(environment: TestDestinationEnv?)

    /**
     * Function that performs any clean up of external resources required for the test. e.g. delete
     * a postgres database. This function will be called after EACH test. It MUST remove all data in
     * the destination so that there is no contamination across tests.
     *
     * @param testEnv
     * - information about the test environment.
     * @throws Exception
     * - can throw any exception, test framework will handle.
     */
    @Throws(Exception::class) protected abstract fun tearDown(testEnv: TestDestinationEnv?)

    private lateinit var mAirbyteApiClient: AirbyteApiClient

    private lateinit var mSourceApi: SourceApi

    private lateinit var mConnectorConfigUpdater: ConnectorConfigUpdater

    protected val lastPersistedCatalog: AirbyteCatalog
        get() =
            convertProtocolObject(
                CatalogClientConverters.toAirbyteProtocol(discoverWriteRequest.value.catalog),
                AirbyteCatalog::class.java
            )

    private val discoverWriteRequest: ArgumentCaptor<SourceDiscoverSchemaWriteRequestBody> =
        ArgumentCaptor.forClass(SourceDiscoverSchemaWriteRequestBody::class.java)

    @BeforeEach
    @Throws(Exception::class)
    fun setUpInternal() {
        val testDir = Path.of("/tmp/airbyte_tests/")
        Files.createDirectories(testDir)
        val workspaceRoot = Files.createTempDirectory(testDir, "test")
        jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"))
        localRoot = Files.createTempDirectory(testDir, "output")
        environment = TestDestinationEnv(localRoot)
        setupEnvironment(environment)
        mAirbyteApiClient = Mockito.mock(AirbyteApiClient::class.java)
        mSourceApi = Mockito.mock(SourceApi::class.java)
        Mockito.`when`(mAirbyteApiClient.sourceApi).thenReturn(mSourceApi)
        Mockito.`when`(mSourceApi.writeDiscoverCatalogResult(ArgumentMatchers.any()))
            .thenReturn(DiscoverCatalogResult().catalogId(CATALOG_ID))
        mConnectorConfigUpdater = Mockito.mock(ConnectorConfigUpdater::class.java)
        val envMap = HashMap(TestEnvConfigs().jobDefaultEnvMap)
        envMap[EnvVariableFeatureFlags.DEPLOYMENT_MODE] = featureFlags().deploymentMode()
        processFactory =
            DockerProcessFactory(
                workspaceRoot,
                workspaceRoot.toString(),
                localRoot.toString(),
                fileTransferMountSource = null,
                "host",
                envMap
            )

        postSetup()
    }

    /**
     * Override this method if you want to do any per-test setup that depends on being able to e.g.
     * [.runRead].
     */
    @Throws(Exception::class) protected open fun postSetup() {}

    @AfterEach
    @Throws(Exception::class)
    fun tearDownInternal() {
        tearDown(environment)
    }

    protected open fun featureFlags(): FeatureFlags {
        return EnvVariableFeatureFlags()
    }

    protected fun runSpec(): ConnectorSpecification {
        val spec =
            DefaultGetSpecTestHarness(
                    AirbyteIntegrationLauncher(
                        JOB_ID,
                        JOB_ATTEMPT,
                        imageName,
                        processFactory,
                        null,
                        null,
                        false,
                        featureFlags()
                    )
                )
                .run(JobGetSpecConfig().withDockerImage(imageName), jobRoot)
                .spec
        return convertProtocolObject(spec, ConnectorSpecification::class.java)
    }

    @Throws(Exception::class)
    protected fun runCheck(): StandardCheckConnectionOutput {
        return DefaultCheckConnectionTestHarness(
                AirbyteIntegrationLauncher(
                    JOB_ID,
                    JOB_ATTEMPT,
                    imageName,
                    processFactory,
                    null,
                    null,
                    false,
                    featureFlags()
                ),
                mConnectorConfigUpdater
            )
            .run(StandardCheckConnectionInput().withConnectionConfiguration(config), jobRoot)
            .checkConnection!!
    }

    @Throws(Exception::class)
    protected fun runCheckAndGetStatusAsString(config: JsonNode?): String {
        return DefaultCheckConnectionTestHarness(
                AirbyteIntegrationLauncher(
                    JOB_ID,
                    JOB_ATTEMPT,
                    imageName,
                    processFactory,
                    null,
                    null,
                    false,
                    featureFlags()
                ),
                mConnectorConfigUpdater
            )
            .run(StandardCheckConnectionInput().withConnectionConfiguration(config), jobRoot)
            .checkConnection!!
            .status
            .toString()
    }

    @Throws(Exception::class)
    protected fun runDiscover(): UUID {
        val toReturn =
            DefaultDiscoverCatalogTestHarness(
                    mAirbyteApiClient,
                    AirbyteIntegrationLauncher(
                        JOB_ID,
                        JOB_ATTEMPT,
                        imageName,
                        processFactory,
                        null,
                        null,
                        false,
                        featureFlags()
                    ),
                    mConnectorConfigUpdater
                )
                .run(
                    StandardDiscoverCatalogInput()
                        .withSourceId(SOURCE_ID.toString())
                        .withConnectionConfiguration(config),
                    jobRoot
                )
                .discoverCatalogId!!
        Mockito.verify(mSourceApi).writeDiscoverCatalogResult(discoverWriteRequest.capture())
        return toReturn
    }

    @Throws(Exception::class)
    protected fun checkEntrypointEnvVariable() {
        val entrypoint =
            EntrypointEnvChecker.getEntrypointEnvVariable(
                processFactory,
                JOB_ID,
                JOB_ATTEMPT,
                jobRoot,
                imageName
            )
        assertNotNull(entrypoint)
        Assertions.assertFalse(entrypoint.isBlank())
    }

    @Throws(Exception::class)
    protected open fun runRead(configuredCatalog: ConfiguredAirbyteCatalog?): List<AirbyteMessage> {
        return runRead(configuredCatalog, null)
    }

    // todo (cgardens) - assume no state since we are all full refresh right now.
    @Throws(Exception::class)
    protected fun runRead(
        catalog: ConfiguredAirbyteCatalog?,
        state: JsonNode?
    ): List<AirbyteMessage> {
        val sourceConfig =
            WorkerSourceConfig()
                .withSourceConnectionConfiguration(config)
                .withState(if (state == null) null else State().withState(state))
                .withCatalog(
                    convertProtocolObject(
                        catalog,
                        io.airbyte.protocol.models.ConfiguredAirbyteCatalog::class.java
                    )
                )

        val source: AirbyteSource =
            DefaultAirbyteSource(
                AirbyteIntegrationLauncher(
                    JOB_ID,
                    JOB_ATTEMPT,
                    imageName,
                    processFactory,
                    null,
                    null,
                    false,
                    featureFlags()
                ),
                featureFlags()
            )
        val messages: MutableList<AirbyteMessage> = ArrayList()
        source.start(sourceConfig, jobRoot)
        while (!source.isFinished) {
            source.attemptRead().ifPresent { m: io.airbyte.protocol.models.AirbyteMessage ->
                messages.add(convertProtocolObject(m, AirbyteMessage::class.java))
            }
        }
        source.close()

        return messages
    }

    @Throws(Exception::class)
    protected fun runReadVerifyNumberOfReceivedMsgs(
        catalog: ConfiguredAirbyteCatalog,
        state: JsonNode?,
        mapOfExpectedRecordsCount: MutableMap<String, Int>
    ): Map<String, Int> {
        val sourceConfig =
            WorkerSourceConfig()
                .withSourceConnectionConfiguration(config)
                .withState(if (state == null) null else State().withState(state))
                .withCatalog(
                    convertProtocolObject(
                        catalog,
                        io.airbyte.protocol.models.ConfiguredAirbyteCatalog::class.java
                    )
                )

        val source = prepareAirbyteSource()
        source.start(sourceConfig, jobRoot)

        while (!source.isFinished) {
            val airbyteMessageOptional =
                source.attemptRead().map { m: io.airbyte.protocol.models.AirbyteMessage ->
                    convertProtocolObject(m, AirbyteMessage::class.java)
                }
            if (
                airbyteMessageOptional.isPresent &&
                    airbyteMessageOptional.get().type == AirbyteMessage.Type.RECORD
            ) {
                val airbyteMessage = airbyteMessageOptional.get()
                val record = airbyteMessage.record

                val streamName = record.stream
                mapOfExpectedRecordsCount[streamName] = mapOfExpectedRecordsCount[streamName]!! - 1
            }
        }
        source.close()
        return mapOfExpectedRecordsCount
    }

    private fun prepareAirbyteSource(): AirbyteSource {
        val integrationLauncher =
            AirbyteIntegrationLauncher(
                JOB_ID,
                JOB_ATTEMPT,
                imageName,
                processFactory,
                null,
                null,
                false,
                featureFlags()
            )
        return DefaultAirbyteSource(integrationLauncher, featureFlags())
    }

    companion object {
        private const val JOB_ID = 0L.toString()
        private const val JOB_ATTEMPT = 0

        private val CATALOG_ID: UUID = UUID.randomUUID()

        private val SOURCE_ID: UUID = UUID.randomUUID()

        private const val CPU_REQUEST_FIELD_NAME = "cpuRequest"
        private const val CPU_LIMIT_FIELD_NAME = "cpuLimit"
        private const val MEMORY_REQUEST_FIELD_NAME = "memoryRequest"
        private const val MEMORY_LIMIT_FIELD_NAME = "memoryLimit"

        private fun <V0, V1> convertProtocolObject(v1: V1, klass: Class<V0>): V0 {
            return Jsons.`object`(Jsons.jsonNode(v1), klass)!!
        }
    }
}
