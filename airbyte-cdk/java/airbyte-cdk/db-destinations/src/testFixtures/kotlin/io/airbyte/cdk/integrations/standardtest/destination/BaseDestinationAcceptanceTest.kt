/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import com.google.common.collect.Sets
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.standardtest.destination.*
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataArgumentsProvider
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataTypeTestArgumentProvider
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.util.ArgumentProviderUtil
import io.airbyte.cdk.integrations.standardtest.destination.comparator.BasicTestDataComparator
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.features.FeatureFlags
import io.airbyte.commons.features.FeatureFlagsWrapper
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.lang.Exceptions
import io.airbyte.commons.resources.MoreResources
import io.airbyte.commons.util.MoreIterators
import io.airbyte.configoss.JobGetSpecConfig
import io.airbyte.configoss.OperatorDbt
import io.airbyte.configoss.StandardCheckConnectionInput
import io.airbyte.configoss.StandardCheckConnectionOutput
import io.airbyte.configoss.WorkerDestinationConfig
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteMessage.Type
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import io.airbyte.workers.exception.TestHarnessException
import io.airbyte.workers.general.DbtTransformationRunner
import io.airbyte.workers.general.DefaultCheckConnectionTestHarness
import io.airbyte.workers.general.DefaultGetSpecTestHarness
import io.airbyte.workers.helper.ConnectorConfigUpdater
import io.airbyte.workers.helper.EntrypointEnvChecker
import io.airbyte.workers.internal.AirbyteDestination
import io.airbyte.workers.internal.DefaultAirbyteDestination
import io.airbyte.workers.normalization.DefaultNormalizationRunner
import io.airbyte.workers.normalization.NormalizationRunner
import io.airbyte.workers.process.AirbyteIntegrationLauncher
import io.airbyte.workers.process.DockerProcessFactory
import io.airbyte.workers.process.ProcessFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.io.UncheckedIOException
import java.net.URISyntaxException
import java.nio.file.Files
import java.nio.file.Path
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.util.*
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import java.util.function.Consumer
import java.util.stream.Stream
import kotlin.test.assertNotNull
import org.junit.jupiter.api.*
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider
import org.junit.jupiter.params.provider.ArgumentsSource
import org.mockito.Mockito

private val LOGGER = KotlinLogging.logger {}

abstract class BaseDestinationAcceptanceTest(
    // If false, ignore counts and only verify the final state message.
    private val verifyIndividualStateAndCounts: Boolean = false,
    protected val useV2Fields: Boolean = false,
    protected val supportsChangeCapture: Boolean = false,
    protected val expectNumericTimestamps: Boolean = false,
    protected val expectSchemalessObjectsCoercedToStrings: Boolean = false,
    protected val expectUnionsPromotedToDisjointRecords: Boolean = false
) {
    protected var testSchemas: HashSet<String> = HashSet()

    protected lateinit var testEnv: TestDestinationEnv
        private set
    protected var fileTransferMountSource: Path? = null
        private set
    protected open val isCloudTest: Boolean = true
    protected val featureFlags: FeatureFlags =
        if (isCloudTest) {
            FeatureFlagsWrapper.overridingDeploymentMode(EnvVariableFeatureFlags(), "CLOUD")
        } else {
            FeatureFlagsWrapper.overridingDeploymentMode(EnvVariableFeatureFlags(), "OSS")
        }

    protected lateinit var jobRoot: Path
        private set
    protected lateinit var processFactory: ProcessFactory
        private set
    private lateinit var mConnectorConfigUpdater: ConnectorConfigUpdater

    protected var localRoot: Path? = null
    open protected var _testDataComparator: TestDataComparator = getTestDataComparator()

    protected open fun getTestDataComparator(): TestDataComparator {
        return BasicTestDataComparator { @Suppress("deprecation") this.resolveIdentifier(it) }
    }

    protected abstract val imageName: String
        /**
         * Name of the docker image that the tests will run against.
         *
         * @return docker image name
         */
        get

    protected open fun supportsInDestinationNormalization(): Boolean {
        return false
    }

    protected fun inDestinationNormalizationFlags(shouldNormalize: Boolean): Map<String, String> {
        if (shouldNormalize && supportsInDestinationNormalization()) {
            return java.util.Map.of("NORMALIZATION_TECHNIQUE", "LEGACY")
        }
        return emptyMap()
    }

    private val imageNameWithoutTag: String
        get() =
            if (imageName.contains(":"))
                imageName.split(":".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()[0]
            else imageName

    private fun readMetadata(): JsonNode {
        return try {
            Jsons.jsonNodeFromFile(MoreResources.readResourceAsFile("metadata.yaml"))
        } catch (e: IllegalArgumentException) {
            // Resource is not found.
            Jsons.emptyObject()
        } catch (e: URISyntaxException) {
            Jsons.emptyObject()
        } catch (e: IOException) {
            throw UncheckedIOException(e)
        }
    }

    protected fun getNormalizationImageName(): String? {
        val metadata = readMetadata()["data"] ?: return null
        val normalizationConfig = metadata["normalizationConfig"] ?: return null
        val normalizationRepository = normalizationConfig["normalizationRepository"] ?: return null
        return normalizationRepository.asText() + ":" + NORMALIZATION_VERSION
    }

    /**
     * Configuration specific to the integration. Will be passed to integration where appropriate in
     * each test. Should be valid.
     *
     * @return integration-specific configuration
     */
    @Throws(Exception::class) protected abstract fun getConfig(): JsonNode

    /**
     * Configuration specific to the integration. Will be passed to integration where appropriate in
     * tests that test behavior when configuration is invalid. e.g incorrect password. Should be
     * invalid.
     *
     * @return integration-specific configuration
     */
    @Throws(Exception::class) protected abstract fun getFailCheckConfig(): JsonNode?

    /**
     * Function that returns all of the records in destination as json at the time this method is
     * invoked. These will be used to check that the data actually written is what should actually
     * be there. Note: this returns a set and does not test any order guarantees.
     *
     * @param testEnv
     * - information about the test environment.
     * @param streamName
     * - name of the stream for which we are retrieving records.
     * @param namespace
     * - the destination namespace records are located in. Null if not applicable. Usually a JDBC
     * schema.
     * @param streamSchema
     * - schema of the stream to be retrieved. This is only necessary for destinations in which data
     * types cannot be accurately inferred (e.g. in CSV destination, every value is a string).
     * @return All of the records in the destination at the time this method is invoked.
     * @throws Exception
     * - can throw any exception, test framework will handle.
     */
    @Throws(Exception::class)
    protected abstract fun retrieveRecords(
        testEnv: TestDestinationEnv?,
        streamName: String,
        namespace: String,
        streamSchema: JsonNode
    ): List<JsonNode>

    protected fun pruneAndMaybeFlatten(node: JsonNode): JsonNode {
        val metaKeys =
            mutableSetOf(
                // V1
                JavaBaseConstants.COLUMN_NAME_AB_ID,
                JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
                // V2
                JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
                JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
                JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
                JavaBaseConstants.COLUMN_NAME_AB_META,
                JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID,
                // Sometimes added
                "_airbyte_additional_properties"
            )

        val jsons = MoreMappers.initMapper().createObjectNode()
        // Iterate over every key value pair in the json node
        for (entry in node.fields()) {
            if (entry.key in metaKeys) {
                continue
            }

            // If the message is normalized, flatten it
            if (entry.key == JavaBaseConstants.COLUMN_NAME_DATA) {
                for (dataEntry in entry.value.fields()) {
                    jsons.replace(dataEntry.key, dataEntry.value)
                }
            } else {
                jsons.replace(entry.key, entry.value)
            }
        }

        return jsons
    }

    protected fun retrieveRecordsDataOnly(
        testEnv: TestDestinationEnv?,
        streamName: String,
        namespace: String,
        streamSchema: JsonNode
    ): List<JsonNode> {
        return retrieveRecords(testEnv, streamName, namespace, streamSchema)
            .map(this::pruneAndMaybeFlatten)
    }

    /**
     * Returns a destination's default schema. The default implementation assumes this corresponds
     * to the configuration's 'schema' field, as this is how most of our destinations implement
     * this. Destinations are free to appropriately override this. The return value is used to
     * assert correctness.
     *
     * If not applicable, Destinations are free to ignore this.
     *
     * @param config
     * - integration-specific configuration returned by [.getConfig].
     * @return the default schema, if applicatble.
     */
    @Throws(Exception::class)
    protected open fun getDefaultSchema(config: JsonNode): String? {
        if (config["schema"] == null) {
            return null
        }
        val schema = config["schema"].asText()
        testSchemas.add(schema)
        return schema
    }

    /**
     * Override to return true if a destination implements namespaces and should be tested as such.
     */
    protected open fun implementsNamespaces(): Boolean {
        return false
    }

    /**
     * Detects if a destination implements append mode from the spec.json that should include
     * 'supportsIncremental' = true
     *
     * @return
     * - a boolean.
     */
    @Throws(TestHarnessException::class)
    protected fun implementsAppend(): Boolean {
        val spec = runSpec()
        Assertions.assertNotNull(spec)
        return if (spec.supportsIncremental != null) {
            spec.supportsIncremental
        } else {
            false
        }
    }

    protected open fun normalizationFromDefinition(): Boolean {
        val metadata = readMetadata()["data"] ?: return false
        val normalizationConfig = metadata["normalizationConfig"] ?: return false
        return normalizationConfig.has("normalizationRepository") &&
            normalizationConfig.has("normalizationTag")
    }

    protected open fun dbtFromDefinition(): Boolean {
        val metadata = readMetadata()["data"] ?: return false
        val supportsDbt = metadata["supportsDbt"]
        return supportsDbt != null && supportsDbt.asBoolean(false)
    }

    protected open val destinationDefinitionKey: String
        get() = imageNameWithoutTag

    protected open fun getNormalizationIntegrationType(): String? {
        val metadata = readMetadata()["data"] ?: return null
        val normalizationConfig = metadata["normalizationConfig"] ?: return null
        val normalizationIntegrationType =
            normalizationConfig["normalizationIntegrationType"] ?: return null
        return normalizationIntegrationType.asText()
    }

    /**
     * Detects if a destination implements append dedup mode from the spec.json that should include
     * 'supportedDestinationSyncMode'
     *
     * @return
     * - a boolean.
     */
    @Throws(TestHarnessException::class)
    protected fun implementsAppendDedup(): Boolean {
        val spec = runSpec()
        Assertions.assertNotNull(spec)
        return if (spec.supportedDestinationSyncModes != null) {
            spec.supportedDestinationSyncModes.contains(DestinationSyncMode.APPEND_DEDUP)
        } else {
            false
        }
    }

    /**
     * Detects if a destination implements overwrite mode from the spec.json that should include
     * 'supportedDestinationSyncMode'
     *
     * @return
     * - a boolean.
     */
    @Throws(TestHarnessException::class)
    protected fun implementsOverwrite(): Boolean {
        val spec = runSpec()
        Assertions.assertNotNull(spec)
        return if (spec.supportedDestinationSyncModes != null) {
            spec.supportedDestinationSyncModes.contains(DestinationSyncMode.OVERWRITE)
        } else {
            false
        }
    }

    /**
     * Same idea as [.retrieveRecords]. Except this method should pull records from the table that
     * contains the normalized records and convert them back into the data as it would appear in an
     * [AirbyteRecordMessage]. Only need to override this method if [.normalizationFromDefinition]
     * returns true.
     *
     * @param testEnv
     * - information about the test environment.
     * @param streamName
     * - name of the stream for which we are retrieving records.
     * @param namespace
     * - the destination namespace records are located in. Null if not applicable. Usually a JDBC
     * schema.
     * @return All of the records in the destination at the time this method is invoked.
     * @throws Exception
     * - can throw any exception, test framework will handle.
     */
    @Throws(Exception::class)
    protected open fun retrieveNormalizedRecords(
        testEnv: TestDestinationEnv?,
        streamName: String?,
        namespace: String?
    ): List<JsonNode> {
        throw IllegalStateException("Not implemented")
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
    protected abstract fun setup(testEnv: TestDestinationEnv, TEST_SCHEMAS: HashSet<String>)

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
    @Throws(Exception::class) protected abstract fun tearDown(testEnv: TestDestinationEnv)

    @Deprecated(
        """This method is moved to the AdvancedTestDataComparator. Please move your destination
                implementation of the method to your comparator implementation."""
    )
    protected open fun resolveIdentifier(identifier: String?): List<String?> {
        return listOf(identifier)
    }

    @BeforeEach
    @Throws(Exception::class)
    fun setUpInternal() {
        val testDir = Path.of("/tmp/airbyte_tests/")
        Files.createDirectories(testDir)
        val workspaceRoot = Files.createTempDirectory(testDir, "test")
        jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"))
        localRoot = Files.createTempDirectory(testDir, "output")
        LOGGER.info { "${"jobRoot: {}"} $jobRoot" }
        LOGGER.info { "${"localRoot: {}"} $localRoot" }
        testEnv = TestDestinationEnv(localRoot)
        mConnectorConfigUpdater = Mockito.mock(ConnectorConfigUpdater::class.java)
        testSchemas = HashSet()
        setup(testEnv, testSchemas)
        fileTransferMountSource =
            if (supportsFileTransfer) Files.createTempDirectory(testDir, "file_transfer") else null

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

    open fun getConnectorEnv(): Map<String, String> {
        return emptyMap()
    }

    @AfterEach
    @Throws(Exception::class)
    fun tearDownInternal() {
        tearDown(testEnv)
    }





    /** Whether the destination should be tested against different namespaces. */
    open protected fun supportNamespaceTest(): Boolean {
        return false
    }

    /**
     * Set up the name transformer used by a destination to test it against a variety of namespaces.
     */
    protected open fun getNameTransformer(): Optional<NamingConventionTransformer> =
        Optional.empty()

    /**
     * Override this method if the normalized namespace is different from the default one. E.g.
     * BigQuery does allow a name starting with a number. So it should change the expected
     * normalized namespace when testCaseId = "S3A-1". Find the testCaseId in
     * "namespace_test_cases.json".
     */
    protected open fun assertNamespaceNormalization(
        testCaseId: String?,
        expectedNormalizedNamespace: String?,
        actualNormalizedNamespace: String?
    ) {
        Assertions.assertEquals(
            expectedNormalizedNamespace,
            actualNormalizedNamespace,
            String.format(
                "Test case %s failed; if this is expected, please override assertNamespaceNormalization",
                testCaseId
            )
        )
    }

    @Throws(TestHarnessException::class)
    protected fun runSpec(): ConnectorSpecification {
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

    @Throws(TestHarnessException::class)
    protected fun runCheck(config: JsonNode?): StandardCheckConnectionOutput {
        return DefaultCheckConnectionTestHarness(
                AirbyteIntegrationLauncher(
                    JOB_ID,
                    JOB_ATTEMPT,
                    imageName,
                    processFactory,
                    null,
                    null,
                    false,
                    featureFlags
                ),
                mConnectorConfigUpdater
            )
            .run(StandardCheckConnectionInput().withConnectionConfiguration(config), jobRoot)
            .checkConnection
    }

    protected fun runCheckWithCatchedException(
        config: JsonNode?
    ): StandardCheckConnectionOutput.Status {
        try {
            val standardCheckConnectionOutput =
                DefaultCheckConnectionTestHarness(
                        AirbyteIntegrationLauncher(
                            JOB_ID,
                            JOB_ATTEMPT,
                            imageName,
                            processFactory,
                            null,
                            null,
                            false,
                            featureFlags
                        ),
                        mConnectorConfigUpdater
                    )
                    .run(
                        StandardCheckConnectionInput().withConnectionConfiguration(config),
                        jobRoot
                    )
                    .checkConnection
            return standardCheckConnectionOutput.status
        } catch (e: Exception) {
            LOGGER.error { "Failed to check connection:" + e.message }
        }
        return StandardCheckConnectionOutput.Status.FAILED
    }

    protected val destination: AirbyteDestination
        get() {
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

        var expected = messages.filter { it.type == Type.STATE }
        var actual = destinationOutput.filter { it.type == Type.STATE }
        LOGGER.info {"SGX messages=$messages"}
        if (verifyIndividualStateAndCounts) {
            /* Collect the counts and add them to each expected state message */
            val stateToCount = mutableMapOf<JsonNode, Int>()
            messages.fold(0) { acc, message ->
                if (message.type == Type.STATE) {
                    stateToCount[message.state.global.sharedState] = acc
                    0
                } else {
                    acc + 1
                }
            }

            expected.forEach { message ->
                val clone = message.state
                clone.destinationStats =
                    AirbyteStateStats().withRecordCount(stateToCount[clone.global.sharedState]!!.toDouble())
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

    @Throws(Exception::class)
    protected fun retrieveRawRecordsAndAssertSameMessages(
        catalog: AirbyteCatalog,
        messages: List<AirbyteMessage>,
        defaultSchema: String?
    ) {
        val actualMessages: MutableList<AirbyteRecordMessage> = ArrayList()
        for (stream in catalog.streams) {
            val streamName = stream.name
            val schema = if (stream.namespace != null) stream.namespace else defaultSchema!!
            val msgList =
                retrieveRecordsDataOnly(testEnv, streamName, schema, stream.jsonSchema).map {
                    data: JsonNode ->
                    AirbyteRecordMessage()
                        .withStream(streamName)
                        .withNamespace(schema)
                        .withData(data)
                }

            actualMessages.addAll(msgList)
        }

        assertSameMessages(messages, actualMessages, false)
    }

    // ignores emitted at.
    open protected fun assertSameMessages(
        expected: List<AirbyteMessage>,
        actual: List<AirbyteRecordMessage>,
        pruneAirbyteInternalFields: Boolean
    ) {
        val expectedProcessed =
            expected
                .filter { message: AirbyteMessage -> message.type == AirbyteMessage.Type.RECORD }
                .map { obj: AirbyteMessage -> obj.record }
                .onEach { recordMessage: AirbyteRecordMessage -> recordMessage.emittedAt = null }
                .map { recordMessage: AirbyteRecordMessage ->
                    if (pruneAirbyteInternalFields) safePrune(recordMessage) else recordMessage
                }
                .map { obj: AirbyteRecordMessage -> obj.data }

        val actualProcessed =
            actual
                .map { recordMessage: AirbyteRecordMessage ->
                    if (pruneAirbyteInternalFields) safePrune(recordMessage) else recordMessage
                }
                .map { obj: AirbyteRecordMessage -> obj.data }

        _testDataComparator.assertSameData(expectedProcessed, actualProcessed)
    }

    @Throws(Exception::class)
    protected fun retrieveNormalizedRecords(
        catalog: AirbyteCatalog,
        defaultSchema: String?
    ): List<AirbyteRecordMessage> {
        val actualMessages: MutableList<AirbyteRecordMessage> = ArrayList()

        for (stream in catalog.streams) {
            val streamName = stream.name

            val msgList =
                retrieveNormalizedRecords(testEnv, streamName, defaultSchema).map { data: JsonNode
                    ->
                    AirbyteRecordMessage().withStream(streamName).withData(data)
                }

            actualMessages.addAll(msgList)
        }
        return actualMessages
    }

    class TestDestinationEnv(val localRoot: Path?) {
        override fun toString(): String {
            return "TestDestinationEnv{" + "localRoot=" + localRoot + '}'
        }
    }



    protected open fun supportBasicDataTypeTest(): Boolean {
        return false
    }

    protected open fun supportArrayDataTypeTest(): Boolean {
        return false
    }

    protected open fun supportObjectDataTypeTest(): Boolean {
        return false
    }

    protected open fun supportIncrementalSchemaChanges(): Boolean {
        return false
    }

    /**
     * The method should be overridden if destination connector support newer protocol version
     * otherwise [io.airbyte.cdk.integrations.standardtest.destination.ProtocolVersion.V0] is used
     *
     * NOTE: Method should be public in a sake of java reflection
     *
     * @return
     */
    open fun getProtocolVersion(): ProtocolVersion = ProtocolVersion.V0

    protected fun checkTestCompatibility(
        testCompatibility: DataTypeTestArgumentProvider.TestCompatibility
    ): Boolean {
        return testCompatibility.isTestCompatible(
            supportBasicDataTypeTest(),
            supportArrayDataTypeTest(),
            supportObjectDataTypeTest()
        )
    }



    @Throws(Exception::class)
    protected fun runAndCheck(
        catalog: AirbyteCatalog,
        configuredCatalog: ConfiguredAirbyteCatalog,
        messages: List<AirbyteMessage>
    ) {
        if (normalizationFromDefinition()) {
            LOGGER.info { "Normalization is supported! Run test with normalization." }
            runAndCheckWithNormalization(messages, configuredCatalog, catalog)
        } else {
            LOGGER.info { "Normalization is not supported! Run test without normalization." }
            runAndCheckWithoutNormalization(messages, configuredCatalog, catalog)
        }
    }

    @Throws(Exception::class)
    private fun runAndCheckWithNormalization(
        messages: List<AirbyteMessage>,
        configuredCatalog: ConfiguredAirbyteCatalog,
        catalog: AirbyteCatalog
    ) {
        val config = getConfig()
        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, true)

        val actualMessages = retrieveNormalizedRecords(catalog, getDefaultSchema(config))
        assertSameMessages(messages, actualMessages, true)
    }

    @Throws(Exception::class)
    private fun runAndCheckWithoutNormalization(
        messages: List<AirbyteMessage>,
        configuredCatalog: ConfiguredAirbyteCatalog,
        catalog: AirbyteCatalog
    ) {
        val config = getConfig()
        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false)
        retrieveRawRecordsAndAssertSameMessages(catalog, messages, getDefaultSchema(config))
    }

    /**
     * Can be used in overridden [
     * getSpecialNumericTypesSupportTest()][.getSpecialNumericTypesSupportTest] method to specify if
     * connector supports Integer/Number NaN or Integer/Number Infinity types
     */
    class SpecialNumericTypes(
        val supportIntegerNan: Boolean = false,
        val supportNumberNan: Boolean = false,
        val supportIntegerInfinity: Boolean = false,
        val supportNumberInfinity: Boolean = false
    )

    class NamespaceTestCaseProvider : ArgumentsProvider {
        @Throws(Exception::class)
        override fun provideArguments(context: ExtensionContext): Stream<out Arguments> {
            val testCases = Jsons.deserialize(MoreResources.readResource(NAMESPACE_TEST_CASES_JSON))
            return MoreIterators.toList(testCases.elements())
                .filter { testCase: JsonNode -> testCase["enabled"].asBoolean() }
                .map { testCase: JsonNode ->
                    val namespaceInCatalog =
                        TestingNamespaces.generate(testCase["namespace"].asText())
                    val namespaceInDst =
                        TestingNamespaces.generateFromOriginal(
                            namespaceInCatalog,
                            testCase["namespace"].asText(),
                            testCase["normalized"].asText()
                        )
                    Arguments.of(
                        testCase["id"]
                            .asText(), // Add uniqueness to namespace to avoid collisions between
                        // tests.
                        namespaceInCatalog,
                        namespaceInDst
                    )
                }
                .stream()
        }

        companion object {
            const val NAMESPACE_TEST_CASES_JSON: String = "namespace_test_cases.json"
        }
    }

    protected fun supportsNormalization(): Boolean {
        return supportsInDestinationNormalization() || normalizationFromDefinition()
    }

    protected open val supportsFileTransfer: Boolean = false

    companion object {
        private val RANDOM = Random()
        private const val NORMALIZATION_VERSION = "dev"

        @JvmStatic
        protected val JOB_ID = "0"
        @JvmStatic
        protected val JOB_ATTEMPT = 0

        /**
         * Reverses a list by creating a new list with the same elements of the input list and then
         * reversing it. The input list will not be altered.
         *
         * @param list to reverse
         * @param <T> type
         * @return new list with elements of original reversed. </T>
         */
        fun <T> reversed(list: List<T>): List<T> {
            val reversed = ArrayList(list)
            Collections.reverse(reversed)
            return reversed
        }

        /**
         * Same as [.pruneMutate], except does a defensive copy and returns a new json node object
         * instead of mutating in place.
         *
         * @param record
         * - record that will be pruned.
         * @return pruned json node.
         */
        private fun safePrune(record: AirbyteRecordMessage): AirbyteRecordMessage {
            val clone = Jsons.clone(record)
            pruneMutate(clone.data)
            return clone
        }

        /**
         * Prune fields that are added internally by airbyte and are not part of the original data.
         * Used so that we can compare data that is persisted by an Airbyte worker to the original
         * data. This method mutates the provided json in place.
         *
         * @param json
         * - json that will be pruned. will be mutated in place!
         */
        private fun pruneMutate(json: JsonNode) {
            for (key in Jsons.keys(json)) {
                val node = json[key]
                // recursively prune all airbyte internal fields.
                if (node.isObject || node.isArray) {
                    pruneMutate(node)
                }

                // prune the following
                // - airbyte internal fields
                // - fields that match what airbyte generates as hash ids
                // - null values -- normalization will often return `<key>: null` but in the
                // original data that key
                // likely did not exist in the original message. the most consistent thing to do is
                // always remove
                // the null fields (this choice does decrease our ability to check that
                // normalization creates
                // columns even if all the values in that column are null)
                val airbyteInternalFields =
                    Sets.newHashSet(
                        "emitted_at",
                        "ab_id",
                        "normalized_at",
                        "EMITTED_AT",
                        "AB_ID",
                        "NORMALIZED_AT",
                        "HASHID",
                        "unique_key",
                        "UNIQUE_KEY"
                    )
                if (
                    airbyteInternalFields.any { internalField: String ->
                        key.lowercase(Locale.getDefault())
                            .contains(internalField.lowercase(Locale.getDefault()))
                    } || json[key].isNull
                ) {
                    (json as ObjectNode).remove(key)
                }
            }
        }



        @JvmStatic
        protected val specialNumericTypesSupportTest: SpecialNumericTypes
            /**
             * NaN and Infinity test are not supported by default. Please override this method to
             * specify NaN/Infinity types support example:
             *
             * <pre>
             *
             * protected SpecialNumericTypes getSpecialNumericTypesSupportTest() { return
             * SpecialNumericTypes.builder() .supportNumberNan(true) .supportIntegerNan(true)
             * .build(); } </pre> *
             *
             * @return SpecialNumericTypes with support flags
             */
            get() = SpecialNumericTypes()

        @JvmStatic
        @Throws(IOException::class)
        protected fun readCatalogFromFile(catalogFilename: String): AirbyteCatalog {
            return Jsons.deserialize(
                MoreResources.readResource(catalogFilename),
                AirbyteCatalog::class.java
            )
        }

        @JvmStatic
        @Throws(IOException::class)
        protected fun readMessagesFromFile(messagesFilename: String): List<AirbyteMessage> {
            return MoreResources.readResource(messagesFilename).trim().lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }
        }

        /** Mutate the input airbyte record message namespace. */
        @JvmStatic
        protected fun getRecordMessagesWithNewNamespace(
            airbyteMessages: List<AirbyteMessage>,
            namespace: String?
        ): List<AirbyteMessage> {
            airbyteMessages.forEach(
                Consumer { message: AirbyteMessage ->
                    if (message.record != null) {
                        message.record.namespace = namespace
                    }
                }
            )
            return airbyteMessages
        }

        @JvmStatic
        protected fun <V0, V1> convertProtocolObject(v1: V1, klass: Class<V0>): V0 {
            return Jsons.`object`(Jsons.jsonNode(v1), klass)!!
        }
    }
}
