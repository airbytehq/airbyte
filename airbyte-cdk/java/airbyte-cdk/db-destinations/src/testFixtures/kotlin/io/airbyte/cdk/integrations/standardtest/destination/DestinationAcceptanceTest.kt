/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import com.google.common.collect.Sets
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.standardtest.destination.*
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataArgumentsProvider
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataTypeTestArgumentProvider
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.util.ArgumentProviderUtil
import io.airbyte.cdk.integrations.standardtest.destination.comparator.BasicTestDataComparator
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.lang.Exceptions
import io.airbyte.commons.resources.MoreResources
import io.airbyte.commons.util.MoreIterators
import io.airbyte.configoss.JobGetSpecConfig
import io.airbyte.configoss.OperatorDbt
import io.airbyte.configoss.StandardCheckConnectionInput
import io.airbyte.configoss.StandardCheckConnectionOutput
import io.airbyte.configoss.StandardCheckConnectionOutput.Status
import io.airbyte.configoss.WorkerDestinationConfig
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteMessage.Type
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.airbyte.protocol.models.v0.DestinationSyncMode
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
import java.io.IOException
import java.io.UncheckedIOException
import java.net.URISyntaxException
import java.nio.file.Files
import java.nio.file.Path
import java.time.Instant
import java.util.*
import java.util.concurrent.atomic.AtomicInteger
import java.util.function.Consumer
import java.util.stream.Collectors
import java.util.stream.Stream
import kotlin.Comparator
import kotlin.collections.ArrayList
import kotlin.collections.HashSet
import kotlin.test.assertNotNull
import org.junit.jupiter.api.*
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider
import org.junit.jupiter.params.provider.ArgumentsSource
import org.mockito.Mockito
import org.slf4j.Logger
import org.slf4j.LoggerFactory

abstract class DestinationAcceptanceTest {
    protected var TEST_SCHEMAS: HashSet<String> = HashSet()

    private lateinit var testEnv: TestDestinationEnv

    private lateinit var jobRoot: Path
    private lateinit var processFactory: ProcessFactory
    private lateinit var mConnectorConfigUpdater: ConnectorConfigUpdater

    protected var localRoot: Path? = null
    open protected var _testDataComparator: TestDataComparator = getTestDataComparator()

    protected open fun getTestDataComparator(): TestDataComparator {
        return BasicTestDataComparator { this.resolveIdentifier(it) }
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
        TEST_SCHEMAS!!.add(schema)
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

    protected fun normalizationFromDefinition(): Boolean {
        val metadata = readMetadata()["data"] ?: return false
        val normalizationConfig = metadata["normalizationConfig"] ?: return false
        return normalizationConfig.has("normalizationRepository") &&
            normalizationConfig.has("normalizationTag")
    }

    protected fun dbtFromDefinition(): Boolean {
        val metadata = readMetadata()["data"] ?: return false
        val supportsDbt = metadata["supportsDbt"]
        return supportsDbt != null && supportsDbt.asBoolean(false)
    }

    protected val destinationDefinitionKey: String
        get() = imageNameWithoutTag

    protected fun getNormalizationIntegrationType(): String? {
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
    protected fun resolveIdentifier(identifier: String?): List<String?> {
        return java.util.List.of(identifier)
    }

    @BeforeEach
    @Throws(Exception::class)
    fun setUpInternal() {
        val testDir = Path.of("/tmp/airbyte_tests/")
        Files.createDirectories(testDir)
        val workspaceRoot = Files.createTempDirectory(testDir, "test")
        jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"))
        localRoot = Files.createTempDirectory(testDir, "output")
        LOGGER.info("jobRoot: {}", jobRoot)
        LOGGER.info("localRoot: {}", localRoot)
        testEnv = TestDestinationEnv(localRoot)
        mConnectorConfigUpdater = Mockito.mock(ConnectorConfigUpdater::class.java)
        TEST_SCHEMAS = HashSet()
        setup(testEnv, TEST_SCHEMAS)

        processFactory =
            DockerProcessFactory(
                workspaceRoot,
                workspaceRoot.toString(),
                localRoot.toString(),
                "host",
                emptyMap()
            )
    }

    @AfterEach
    @Throws(Exception::class)
    fun tearDownInternal() {
        tearDown(testEnv)
    }

    /** Verify that when the integrations returns a valid spec. */
    @Test
    @Throws(TestHarnessException::class)
    fun testGetSpec() {
        Assertions.assertNotNull(runSpec())
    }

    /**
     * Verify that when given valid credentials, that check connection returns a success response.
     * Assume that the [DestinationAcceptanceTest.getConfig] is valid.
     */
    @Test
    @Throws(Exception::class)
    fun testCheckConnection() {
        Assertions.assertEquals(
            StandardCheckConnectionOutput.Status.SUCCEEDED,
            runCheck(getConfig()).status
        )
    }

    /**
     * Verify that when given invalid credentials, that check connection returns a failed response.
     * Assume that the [DestinationAcceptanceTest.getFailCheckConfig] is invalid.
     */
    @Test
    @Throws(Exception::class)
    fun testCheckConnectionInvalidCredentials() {
        Assertions.assertEquals(
            StandardCheckConnectionOutput.Status.FAILED,
            runCheck(getFailCheckConfig()).status
        )
    }

    /**
     * Verify that the integration successfully writes records. Tests a wide variety of messages and
     * schemas (aspirationally, anyway).
     */
    @ParameterizedTest
    @ArgumentsSource(DataArgumentsProvider::class)
    @Throws(Exception::class)
    fun testSync(messagesFilename: String, catalogFilename: String) {
        val catalog =
            Jsons.deserialize(
                MoreResources.readResource(catalogFilename),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages: List<io.airbyte.protocol.models.v0.AirbyteMessage> =
            MoreResources.readResource(messagesFilename)
                .lines()
                .map {
                    Jsons.deserialize(it, io.airbyte.protocol.models.v0.AirbyteMessage::class.java)
                }
                .toList()

        val config = getConfig()
        val defaultSchema = getDefaultSchema(config)
        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false)
        retrieveRawRecordsAndAssertSameMessages(catalog, messages, defaultSchema)
    }

    /**
     * This serves to test MSSQL 2100 limit parameters in a single query. this means that for
     * Airbyte insert data need to limit to ~ 700 records (3 columns for the raw tables) = 2100
     * params
     */
    @ParameterizedTest
    @ArgumentsSource(DataArgumentsProvider::class)
    @Throws(Exception::class)
    fun testSyncWithLargeRecordBatch(messagesFilename: String, catalogFilename: String) {
        val catalog =
            Jsons.deserialize(
                MoreResources.readResource(catalogFilename),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages: List<io.airbyte.protocol.models.v0.AirbyteMessage> =
            MoreResources.readResource(messagesFilename)
                .lines()
                .map {
                    Jsons.deserialize(it, io.airbyte.protocol.models.v0.AirbyteMessage::class.java)
                }
                .toList()

        val largeNumberRecords =
            Collections.nCopies(400, messages)
                .stream()
                .flatMap { obj: List<io.airbyte.protocol.models.v0.AirbyteMessage> ->
                    obj.stream()
                } // regroup messages per stream
                .sorted(
                    Comparator.comparing { obj: io.airbyte.protocol.models.v0.AirbyteMessage ->
                            obj.type
                        }
                        .thenComparing { message: io.airbyte.protocol.models.v0.AirbyteMessage ->
                            if (
                                message.type ==
                                    io.airbyte.protocol.models.v0.AirbyteMessage.Type.RECORD
                            )
                                message.record.stream
                            else message.toString()
                        }
                )
                .collect(Collectors.toList())

        val config = getConfig()
        runSyncAndVerifyStateOutput(config, largeNumberRecords, configuredCatalog, false)
    }

    /** Verify that the integration overwrites the first sync with the second sync. */
    @Test
    @Throws(Exception::class)
    fun testSecondSync() {
        if (!implementsOverwrite()) {
            LOGGER.info("Destination's spec.json does not support overwrite sync mode.")
            return
        }

        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)

        val firstSyncMessages: List<io.airbyte.protocol.models.v0.AirbyteMessage> =
            MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                        getProtocolVersion()
                    )
                )
                .lines()
                .map {
                    Jsons.deserialize<io.airbyte.protocol.models.v0.AirbyteMessage>(
                        it,
                        io.airbyte.protocol.models.v0.AirbyteMessage::class.java
                    )
                }
                .toList()
        val config = getConfig()
        runSyncAndVerifyStateOutput(config, firstSyncMessages, configuredCatalog, false)

        // We need to make sure that other streams\tables\files in the same location will not be
        // affected\deleted\overridden by our activities during first, second or any future sync.
        // So let's create a dummy data that will be checked after all sync. It should remain the
        // same
        val dummyCatalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        dummyCatalog.streams[0].name = DUMMY_CATALOG_NAME
        val configuredDummyCatalog = CatalogHelpers.toDefaultConfiguredCatalog(dummyCatalog)
        // update messages to set new dummy stream name
        firstSyncMessages
            .stream()
            .filter { message: io.airbyte.protocol.models.v0.AirbyteMessage ->
                message.record != null
            }
            .forEach { message: io.airbyte.protocol.models.v0.AirbyteMessage ->
                message.record.stream = DUMMY_CATALOG_NAME
            }
        // sync dummy data
        runSyncAndVerifyStateOutput(config, firstSyncMessages, configuredDummyCatalog, false)

        // Run second sync
        val secondSyncMessages: List<io.airbyte.protocol.models.v0.AirbyteMessage> =
            Lists.newArrayList(
                io.airbyte.protocol.models.v0
                    .AirbyteMessage()
                    .withType(io.airbyte.protocol.models.v0.AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(catalog.streams[0].name)
                            .withEmittedAt(Instant.now().toEpochMilli())
                            .withData(
                                Jsons.jsonNode(
                                    ImmutableMap.builder<Any, Any>()
                                        .put("id", 1)
                                        .put("currency", "USD")
                                        .put(
                                            "date",
                                            "2020-03-31T00:00:00Z"
                                        ) // TODO(sherifnada) hack: write decimals with sigfigs
                                        // because Snowflake stores 10.1 as "10" which
                                        // fails destination tests
                                        .put("HKD", 10.1)
                                        .put("NZD", 700.1)
                                        .build()
                                )
                            )
                    ),
                io.airbyte.protocol.models.v0
                    .AirbyteMessage()
                    .withType(io.airbyte.protocol.models.v0.AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withData(Jsons.jsonNode(ImmutableMap.of("checkpoint", 2)))
                    )
            )

        runSyncAndVerifyStateOutput(config, secondSyncMessages, configuredCatalog, false)
        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(catalog, secondSyncMessages, defaultSchema)

        // verify that other streams in the same location were not affected. If something fails
        // here,
        // then this need to be fixed in connectors logic to override only required streams
        retrieveRawRecordsAndAssertSameMessages(dummyCatalog, firstSyncMessages, defaultSchema)
    }

    /**
     * Tests that we are able to read over special characters properly when processing line breaks
     * in destinations.
     */
    @Test
    @Throws(Exception::class)
    fun testLineBreakCharacters() {
        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val config = getConfig()

        val secondSyncMessages: List<io.airbyte.protocol.models.v0.AirbyteMessage> =
            Lists.newArrayList(
                io.airbyte.protocol.models.v0
                    .AirbyteMessage()
                    .withType(io.airbyte.protocol.models.v0.AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(catalog.streams[0].name)
                            .withEmittedAt(Instant.now().toEpochMilli())
                            .withData(
                                Jsons.jsonNode(
                                    ImmutableMap.builder<Any, Any>()
                                        .put("id", 1)
                                        .put("currency", "USD\u2028")
                                        .put(
                                            "date",
                                            "2020-03-\n31T00:00:00Z\r"
                                        ) // TODO(sherifnada) hack: write decimals with sigfigs
                                        // because Snowflake stores 10.1 as "10" which
                                        // fails destination tests
                                        .put("HKD", 10.1)
                                        .put("NZD", 700.1)
                                        .build()
                                )
                            )
                    ),
                io.airbyte.protocol.models.v0
                    .AirbyteMessage()
                    .withType(io.airbyte.protocol.models.v0.AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withData(Jsons.jsonNode(ImmutableMap.of("checkpoint", 2)))
                    )
            )

        runSyncAndVerifyStateOutput(config, secondSyncMessages, configuredCatalog, false)
        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(catalog, secondSyncMessages, defaultSchema)
    }

    @Test
    fun normalizationFromDefinitionValueShouldBeCorrect() {
        if (normalizationFromDefinition()) {
            var normalizationRunnerFactorySupportsDestinationImage: Boolean
            try {
                DefaultNormalizationRunner(
                    processFactory,
                    getNormalizationImageName(),
                    getNormalizationIntegrationType()
                )
                normalizationRunnerFactorySupportsDestinationImage = true
            } catch (e: IllegalStateException) {
                normalizationRunnerFactorySupportsDestinationImage = false
            }
            Assertions.assertEquals(
                normalizationFromDefinition(),
                normalizationRunnerFactorySupportsDestinationImage
            )
        }
    }

    /**
     * Verify that the integration successfully writes records incrementally. The second run should
     * append records to the datastore instead of overwriting the previous run.
     */
    @Test
    @Throws(Exception::class)
    fun testIncrementalSync() {
        if (!implementsAppend()) {
            LOGGER.info("Destination's spec.json does not include '\"supportsIncremental\" ; true'")
            return
        }

        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog.streams.forEach { s ->
            s.withSyncMode(SyncMode.INCREMENTAL)
            s.withDestinationSyncMode(DestinationSyncMode.APPEND)
        }

        val firstSyncMessages: List<io.airbyte.protocol.models.v0.AirbyteMessage> =
            MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                        getProtocolVersion()
                    )
                )
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
                .toList()
        val config = getConfig()
        runSyncAndVerifyStateOutput(config, firstSyncMessages, configuredCatalog, false)
        val secondSyncMessages: List<io.airbyte.protocol.models.v0.AirbyteMessage> =
            Lists.newArrayList(
                io.airbyte.protocol.models.v0
                    .AirbyteMessage()
                    .withType(io.airbyte.protocol.models.v0.AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(catalog.streams[0].name)
                            .withEmittedAt(Instant.now().toEpochMilli())
                            .withData(
                                Jsons.jsonNode(
                                    ImmutableMap.builder<Any, Any>()
                                        .put("id", 1)
                                        .put("currency", "USD")
                                        .put(
                                            "date",
                                            "2020-03-31T00:00:00Z"
                                        ) // TODO(sherifnada) hack: write decimals with sigfigs
                                        // because Snowflake stores 10.1 as "10" which
                                        // fails destination tests
                                        .put("HKD", 10.1)
                                        .put("NZD", 700.1)
                                        .build()
                                )
                            )
                    ),
                io.airbyte.protocol.models.v0
                    .AirbyteMessage()
                    .withType(io.airbyte.protocol.models.v0.AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withData(Jsons.jsonNode(ImmutableMap.of("checkpoint", 2)))
                    )
            )
        runSyncAndVerifyStateOutput(config, secondSyncMessages, configuredCatalog, false)

        val expectedMessagesAfterSecondSync:
            MutableList<io.airbyte.protocol.models.v0.AirbyteMessage> =
            ArrayList()
        expectedMessagesAfterSecondSync.addAll(firstSyncMessages)
        expectedMessagesAfterSecondSync.addAll(secondSyncMessages)

        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(
            catalog,
            expectedMessagesAfterSecondSync,
            defaultSchema
        )
    }

    @ArgumentsSource(DataArgumentsProvider::class)
    @Test
    @Throws(Exception::class)
    fun testIncrementalSyncWithNormalizationDropOneColumn() {
        if (!normalizationFromDefinition() || !supportIncrementalSchemaChanges()) {
            return
        }

        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        ProtocolVersion.V0
                    )
                ),
                AirbyteCatalog::class.java
            )

        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog.streams.forEach { s ->
            s.withSyncMode(SyncMode.INCREMENTAL)
            s.withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            s.withCursorField(emptyList())
            // use composite primary key of various types (string, float)
            s.withPrimaryKey(
                java.util.List.of(
                    listOf("id"),
                    listOf("currency"),
                    listOf("date"),
                    listOf("NZD"),
                    listOf("USD")
                )
            )
        }

        var messages =
            MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                        ProtocolVersion.V0
                    )
                )
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
                .toMutableList()

        val config = getConfig()
        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, true)

        val defaultSchema = getDefaultSchema(config)
        var actualMessages = retrieveNormalizedRecords(catalog, defaultSchema)
        assertSameMessages(messages, actualMessages, true)

        // remove one field
        val jsonSchema = configuredCatalog.streams[0].stream.jsonSchema
        (jsonSchema.findValue("properties") as ObjectNode).remove("HKD")
        // insert more messages
        // NOTE: we re-read the messages because `assertSameMessages` above pruned the emittedAt
        // timestamps.
        messages =
            MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                        ProtocolVersion.V0
                    )
                )
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
                .toMutableList()
        messages.addLast(
            Jsons.deserialize(
                "{\"type\": \"RECORD\", \"record\": {\"stream\": \"exchange_rate\", \"emitted_at\": 1602637989500, \"data\": { \"id\": 2, \"currency\": \"EUR\", \"date\": \"2020-09-02T00:00:00Z\", \"NZD\": 1.14, \"USD\": 10.16}}}\n",
                io.airbyte.protocol.models.v0.AirbyteMessage::class.java
            )
        )

        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, true)

        // assert the removed field is missing on the new messages
        actualMessages = retrieveNormalizedRecords(catalog, defaultSchema)

        // We expect all the of messages to be missing the removed column after normalization.
        val expectedMessages =
            messages
                .stream()
                .map { message: io.airbyte.protocol.models.v0.AirbyteMessage ->
                    if (message.record != null) {
                        (message.record.data as ObjectNode).remove("HKD")
                    }
                    message
                }
                .collect(Collectors.toList())
        assertSameMessages(expectedMessages, actualMessages, true)
    }

    /**
     * Verify that the integration successfully writes records successfully both raw and normalized.
     * Tests a wide variety of messages an schemas (aspirationally, anyway).
     */
    @ParameterizedTest
    @ArgumentsSource(DataArgumentsProvider::class)
    @Throws(Exception::class)
    open fun testSyncWithNormalization(messagesFilename: String, catalogFilename: String) {
        if (!normalizationFromDefinition()) {
            return
        }

        val catalog =
            Jsons.deserialize(
                MoreResources.readResource(catalogFilename),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages =
            MoreResources.readResource(messagesFilename).lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }

        val config = getConfig()
        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, true)

        val defaultSchema = getDefaultSchema(config)
        val actualMessages = retrieveNormalizedRecords(catalog, defaultSchema)
        assertSameMessages(messages, actualMessages, true)
    }

    /**
     * Verify that the integration successfully writes records successfully both raw and normalized
     * and run dedupe transformations.
     *
     * Although this test assumes append-dedup requires normalization, and almost all our
     * Destinations do so, this is not necessarily true. This explains [.implementsAppendDedup].
     */
    @Test
    @Throws(Exception::class)
    open fun testIncrementalDedupeSync() {
        if (!implementsAppendDedup()) {
            LOGGER.info(
                "Destination's spec.json does not include 'append_dedupe' in its '\"supportedDestinationSyncModes\"'"
            )
            return
        }

        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog.streams.forEach { s ->
            s.withSyncMode(SyncMode.INCREMENTAL)
            s.withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            s.withCursorField(emptyList())
            // use composite primary key of various types (string, float)
            s.withPrimaryKey(
                java.util.List.of(listOf("id"), listOf("currency"), listOf("date"), listOf("NZD"))
            )
        }

        val firstSyncMessages =
            MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                        getProtocolVersion()
                    )
                )
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
        val config = getConfig()
        runSyncAndVerifyStateOutput(
            config,
            firstSyncMessages,
            configuredCatalog,
            supportsNormalization()
        )

        val secondSyncMessages: List<io.airbyte.protocol.models.v0.AirbyteMessage> =
            Lists.newArrayList(
                io.airbyte.protocol.models.v0
                    .AirbyteMessage()
                    .withType(io.airbyte.protocol.models.v0.AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(catalog.streams[0].name)
                            .withEmittedAt(Instant.now().toEpochMilli())
                            .withData(
                                Jsons.jsonNode(
                                    ImmutableMap.builder<Any, Any>()
                                        .put("id", 2)
                                        .put("currency", "EUR")
                                        .put("date", "2020-09-01T00:00:00Z")
                                        .put("HKD", 10.5)
                                        .put("NZD", 1.14)
                                        .build()
                                )
                            )
                    ),
                io.airbyte.protocol.models.v0
                    .AirbyteMessage()
                    .withType(io.airbyte.protocol.models.v0.AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(catalog.streams[0].name)
                            .withEmittedAt(Instant.now().toEpochMilli() + 100L)
                            .withData(
                                Jsons.jsonNode(
                                    ImmutableMap.builder<Any, Any>()
                                        .put("id", 1)
                                        .put("currency", "USD")
                                        .put("date", "2020-09-01T00:00:00Z")
                                        .put("HKD", 5.4)
                                        .put("NZD", 1.14)
                                        .build()
                                )
                            )
                    ),
                io.airbyte.protocol.models.v0
                    .AirbyteMessage()
                    .withType(io.airbyte.protocol.models.v0.AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withData(Jsons.jsonNode(ImmutableMap.of("checkpoint", 2)))
                    )
            )
        runSyncAndVerifyStateOutput(config, secondSyncMessages, configuredCatalog, false)

        val expectedMessagesAfterSecondSync:
            MutableList<io.airbyte.protocol.models.v0.AirbyteMessage> =
            ArrayList()
        expectedMessagesAfterSecondSync.addAll(firstSyncMessages)
        expectedMessagesAfterSecondSync.addAll(secondSyncMessages)

        val latestMessagesOnly =
            expectedMessagesAfterSecondSync
                .filter { it.type == Type.RECORD && it.record != null }
                .groupBy {
                    it.record.data["id"].asText() +
                        it.record.data["currency"].asText() +
                        it.record.data["date"].asText() +
                        it.record.data["NZD"].asText()
                }
                .mapValues { it.value.maxBy { it.record.emittedAt } }
        // Filter expectedMessagesAfterSecondSync and keep latest messages only (keep same message
        // order)
        val expectedMessages =
            expectedMessagesAfterSecondSync
                .stream()
                .filter { it.type == Type.RECORD && it.record != null }
                .filter {
                    val key =
                        it.record.data["id"].asText() +
                            it.record.data["currency"].asText() +
                            it.record.data["date"].asText() +
                            it.record.data["NZD"].asText()
                    (it.record.emittedAt == latestMessagesOnly[key]!!.record.emittedAt)
                }
                .collect(Collectors.toList())

        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(
            catalog,
            expectedMessagesAfterSecondSync,
            defaultSchema
        )
        if (normalizationFromDefinition()) {
            val actualMessages = retrieveNormalizedRecords(catalog, defaultSchema)
            assertSameMessages(expectedMessages, actualMessages, true)
        }
    }

    protected open val maxRecordValueLimit: Int
        /** @return the max limit length allowed for values in the destination. */
        get() = 1000000000

    @Test
    @Throws(Exception::class)
    open fun testCustomDbtTransformations() {
        if (!dbtFromDefinition()) {
            return
        }

        val config = getConfig()

        // This may throw IllegalStateException "Requesting normalization, but it is not included in
        // the
        // normalization mappings"
        // We indeed require normalization implementation of the 'transform_config' function for
        // this
        // destination,
        // because we make sure to install required dbt dependency in the normalization docker image
        // in
        // order to run
        // this test successfully and that we are able to convert a destination 'config.json' into a
        // dbt
        // 'profiles.yml'
        // (we don't actually rely on normalization running anything else here though)
        val runner =
            DbtTransformationRunner(
                processFactory,
                DefaultNormalizationRunner(
                    processFactory,
                    getNormalizationImageName(),
                    getNormalizationIntegrationType()
                )
            )
        runner.start()
        val transformationRoot = Files.createDirectories(jobRoot!!.resolve("transform"))
        val dbtConfig =
            OperatorDbt() // Forked from https://github.com/dbt-labs/jaffle_shop because they made a
                // change that would have
                // required a dbt version upgrade
                // https://github.com/dbt-labs/jaffle_shop/commit/b1680f3278437c081c735b7ea71c2ff9707bc75f#diff-27386df54b2629c1191d8342d3725ed8678413cfa13b5556f59d69d33fae5425R20
                // We're actually two commits upstream of that, because the previous commit
                // (https://github.com/dbt-labs/jaffle_shop/commit/ec36ae177ab5cb79da39ff8ab068c878fbac13a0) also
                // breaks something
                // TODO once we're on DBT 1.x, switch this back to using the main branch
                .withGitRepoUrl("https://github.com/airbytehq/jaffle_shop.git")
                .withGitRepoBranch("pre_dbt_upgrade")
                .withDockerImage(getNormalizationImageName())
        //
        // jaffle_shop is a fictional ecommerce store maintained by fishtownanalytics/dbt.
        //
        // This dbt project transforms raw data from an app database into a customers and orders
        // model ready
        // for analytics.
        // The repo is a self-contained playground dbt project, useful for testing out scripts, and
        // communicating some of the core dbt concepts:
        //
        // 1. First, it tests if connection to the destination works.
        dbtConfig.withDbtArguments("debug")
        if (!runner.run(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt debug Failed.")
        }
        // 2. Install any dependencies packages, if any
        dbtConfig.withDbtArguments("deps")
        if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt deps Failed.")
        }
        // 3. It contains seeds that includes some (fake) raw data from a fictional app as CSVs data
        // sets.
        // This materializes the CSVs as tables in your target schema.
        // Note that a typical dbt project does not require this step since dbt assumes your raw
        // data is
        // already in your warehouse.
        dbtConfig.withDbtArguments("seed")
        if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt seed Failed.")
        }
        // 4. Run the models:
        // Note: If this steps fails, it might mean that you need to make small changes to the SQL
        // in the
        // models folder to adjust for the flavor of SQL of your target database.
        dbtConfig.withDbtArguments("run")
        if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt run Failed.")
        }
        // 5. Test the output of the models and tables have been properly populated:
        dbtConfig.withDbtArguments("test")
        if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt test Failed.")
        }
        // 6. Generate dbt documentation for the project:
        // This step is commented out because it takes a long time, but is not vital for Airbyte
        // dbtConfig.withDbtArguments("docs generate");
        // if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig))
        // {
        // throw new WorkerException("dbt docs generate Failed.");
        // }
        runner.close()
    }

    @Test
    @Throws(Exception::class)
    fun testCustomDbtTransformationsFailure() {
        if (!normalizationFromDefinition() || !dbtFromDefinition()) {
            // we require normalization implementation for this destination, because we make sure to
            // install
            // required dbt dependency in the normalization docker image in order to run this test
            // successfully
            // (we don't actually rely on normalization running anything here though)
            return
        }

        val config = getConfig()

        val runner =
            DbtTransformationRunner(
                processFactory,
                DefaultNormalizationRunner(
                    processFactory,
                    getNormalizationImageName(),
                    getNormalizationIntegrationType()
                )
            )
        runner.start()
        val transformationRoot = Files.createDirectories(jobRoot!!.resolve("transform"))
        val dbtConfig =
            OperatorDbt()
                .withGitRepoUrl("https://github.com/fishtown-analytics/dbt-learn-demo.git")
                .withGitRepoBranch("main")
                .withDockerImage("fishtownanalytics/dbt:0.19.1")
                .withDbtArguments("debug")
        if (!runner.run(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt debug Failed.")
        }

        dbtConfig.withDbtArguments("test")
        Assertions.assertFalse(
            runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig),
            "dbt test should fail, as we haven't run dbt run on this project yet"
        )
    }

    /** Verify the destination uses the namespace field if it is set. */
    @Test
    @Throws(Exception::class)
    fun testSyncUsesAirbyteStreamNamespaceIfNotNull() {
        if (!implementsNamespaces()) {
            return
        }

        // TODO(davin): make these tests part of the catalog file.
        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        // A unique namespace is required to avoid test isolation problems.
        val namespace = TestingNamespaces.generate("source_namespace")
        TEST_SCHEMAS!!.add(namespace)

        catalog.streams.forEach(Consumer { stream: AirbyteStream -> stream.namespace = namespace })
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)

        val messages =
            MoreResources.readResource(
                    DataArgumentsProvider.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                        getProtocolVersion()
                    )
                )
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
        val messagesWithNewNamespace = getRecordMessagesWithNewNamespace(messages, namespace)

        val config = getConfig()
        val defaultSchema = getDefaultSchema(config)
        runSyncAndVerifyStateOutput(config, messagesWithNewNamespace, configuredCatalog, false)
        retrieveRawRecordsAndAssertSameMessages(catalog, messagesWithNewNamespace, defaultSchema)
    }

    /** Verify a destination is able to write tables with the same name to different namespaces. */
    @Test
    @Throws(Exception::class)
    fun testSyncWriteSameTableNameDifferentNamespace() {
        if (!implementsNamespaces()) {
            return
        }

        // TODO(davin): make these tests part of the catalog file.
        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        val namespace1 = TestingNamespaces.generate("source_namespace")
        TEST_SCHEMAS!!.add(namespace1)
        catalog.streams.forEach(Consumer { stream: AirbyteStream -> stream.namespace = namespace1 })

        val diffNamespaceStreams = ArrayList<AirbyteStream>()
        val namespace2 = TestingNamespaces.generate("diff_source_namespace")
        TEST_SCHEMAS!!.add(namespace2)
        val mapper = MoreMappers.initMapper()
        for (stream in catalog.streams) {
            val clonedStream =
                mapper.readValue(mapper.writeValueAsString(stream), AirbyteStream::class.java)
            clonedStream.namespace = namespace2
            diffNamespaceStreams.add(clonedStream)
        }
        catalog.streams.addAll(diffNamespaceStreams)

        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messageFile: String =
            DataArgumentsProvider.EXCHANGE_RATE_CONFIG.getMessageFileVersion(getProtocolVersion())
        val ns1Messages =
            MoreResources.readResource(messageFile).lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }
        val ns1MessagesAtNamespace1 = getRecordMessagesWithNewNamespace(ns1Messages, namespace1)
        val ns2Messages: List<io.airbyte.protocol.models.v0.AirbyteMessage> =
            MoreResources.readResource(messageFile).lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }
        val ns2MessagesAtNamespace2 = getRecordMessagesWithNewNamespace(ns2Messages, namespace2)

        val allMessages = ArrayList(ns1MessagesAtNamespace1)
        allMessages.addAll(ns2MessagesAtNamespace2)

        val config = getConfig()
        val defaultSchema = getDefaultSchema(config)
        runSyncAndVerifyStateOutput(config, allMessages, configuredCatalog, false)
        retrieveRawRecordsAndAssertSameMessages(catalog, allMessages, defaultSchema)
    }

    /**
     * The goal of this test is to verify the expected conversions of a namespace as it appears in
     * the catalog to how it appears in the destination. Each database has its own rules, so this
     * test runs through several "edge" case sorts of names and checks the behavior.
     *
     * @param testCaseId
     * - the id of each test case in namespace_test_cases.json so that we can handle an individual
     * case specially for a specific database.
     * @param namespaceInCatalog
     * - namespace as it would appear in the catalog
     * @param namespaceInDst
     * - namespace as we would expect it to appear in the destination (this may be overridden for
     * different databases).
     * @throws Exception
     * - broad catch of exception to hydrate log information with additional test case context.
     */
    @ParameterizedTest
    @ArgumentsSource(NamespaceTestCaseProvider::class)
    @Throws(Exception::class)
    fun testNamespaces(testCaseId: String?, namespaceInCatalog: String, namespaceInDst: String?) {
        val nameTransformer = getNameTransformer()
        nameTransformer.ifPresent { namingConventionTransformer: NamingConventionTransformer ->
            assertNamespaceNormalization(
                testCaseId,
                namespaceInDst,
                namingConventionTransformer.getNamespace(namespaceInCatalog!!)
            )
        }

        if (!implementsNamespaces() || !supportNamespaceTest()) {
            return
        }

        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.NAMESPACE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        catalog.streams.forEach(
            Consumer { stream: AirbyteStream -> stream.namespace = namespaceInCatalog }
        )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)

        val messages =
            MoreResources.readResource(
                    DataArgumentsProvider.NAMESPACE_CONFIG.getMessageFileVersion(
                        getProtocolVersion()
                    )
                )
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
        val messagesWithNewNamespace =
            getRecordMessagesWithNewNamespace(messages, namespaceInCatalog)

        val config = getConfig()
        try {
            runSyncAndVerifyStateOutput(config, messagesWithNewNamespace, configuredCatalog, false)
            // Add to the list of schemas to clean up.
            TEST_SCHEMAS!!.add(namespaceInCatalog)
        } catch (e: Exception) {
            throw IOException(
                String.format(
                    "[Test Case %s] Destination failed to sync data to namespace %s, see \"namespace_test_cases.json for details\"",
                    testCaseId,
                    namespaceInCatalog
                ),
                e
            )
        }
    }

    /**
     * In order to launch a source on Kubernetes in a pod, we need to be able to wrap the
     * entrypoint. The source connector must specify its entrypoint in the AIRBYTE_ENTRYPOINT
     * variable. This test ensures that the entrypoint environment variable is set.
     */
    @Test
    @Throws(Exception::class)
    fun testEntrypointEnvVar() {
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

    /**
     * Verify that destination doesn't fail if new fields arrive in the data after initial schema
     * discovery and sync.
     *
     * @throws Exception
     */
    @Test
    @Throws(Exception::class)
    fun testSyncNotFailsWithNewFields() {
        if (!implementsOverwrite()) {
            LOGGER.info("Destination's spec.json does not support overwrite sync mode.")
            return
        }

        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)

        val firstSyncMessages =
            MoreResources.readResource(
                    DataArgumentsProvider.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                        getProtocolVersion()
                    )
                )
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
        val config = getConfig()
        runSyncAndVerifyStateOutput(config, firstSyncMessages, configuredCatalog, false)
        val stream = catalog.streams[0]

        // Run second sync with new fields on the message
        val secondSyncMessagesWithNewFields:
            MutableList<io.airbyte.protocol.models.v0.AirbyteMessage> =
            Lists.newArrayList(
                io.airbyte.protocol.models.v0
                    .AirbyteMessage()
                    .withType(Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(stream.name)
                            .withEmittedAt(Instant.now().toEpochMilli())
                            .withData(
                                Jsons.jsonNode(
                                    ImmutableMap.builder<Any, Any>()
                                        .put("id", 1)
                                        .put("currency", "USD")
                                        .put("date", "2020-03-31T00:00:00Z")
                                        .put("newFieldString", "Value for new field")
                                        .put("newFieldNumber", 3)
                                        .put("HKD", 10.1)
                                        .put("NZD", 700.1)
                                        .build()
                                )
                            )
                    ),
                io.airbyte.protocol.models.v0
                    .AirbyteMessage()
                    .withType(io.airbyte.protocol.models.v0.AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withData(Jsons.jsonNode(ImmutableMap.of("checkpoint", 2)))
                    )
            )

        // Run sync and verify that all message were written without failing
        runSyncAndVerifyStateOutput(
            config,
            secondSyncMessagesWithNewFields,
            configuredCatalog,
            false
        )
        val destinationOutput =
            retrieveRecords(testEnv, stream.name, getDefaultSchema(config)!!, stream.jsonSchema)
        // Remove state message
        secondSyncMessagesWithNewFields.removeIf {
            airbyteMessage: io.airbyte.protocol.models.v0.AirbyteMessage ->
            airbyteMessage.type == io.airbyte.protocol.models.v0.AirbyteMessage.Type.STATE
        }
        Assertions.assertEquals(secondSyncMessagesWithNewFields.size, destinationOutput.size)
    }

    /** Whether the destination should be tested against different namespaces. */
    protected fun supportNamespaceTest(): Boolean {
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
    protected fun assertNamespaceNormalization(
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
    private fun runSpec(): ConnectorSpecification {
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
                        EnvVariableFeatureFlags()
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
                    EnvVariableFeatureFlags()
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
                            EnvVariableFeatureFlags()
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
            LOGGER.error("Failed to check connection:" + e.message)
        }
        return StandardCheckConnectionOutput.Status.FAILED
    }

    protected val destination: AirbyteDestination
        get() =
            DefaultAirbyteDestination(
                AirbyteIntegrationLauncher(
                    JOB_ID,
                    JOB_ATTEMPT,
                    imageName,
                    processFactory,
                    null,
                    null,
                    false,
                    EnvVariableFeatureFlags()
                )
            )

    @Throws(Exception::class)
    protected fun runSyncAndVerifyStateOutput(
        config: JsonNode,
        messages: List<io.airbyte.protocol.models.v0.AirbyteMessage>,
        catalog: io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog,
        runNormalization: Boolean
    ) {
        val destinationOutput = runSync(config, messages, catalog, runNormalization)

        val expectedStateMessage =
            reversed(messages)
                .stream()
                .filter { m: io.airbyte.protocol.models.v0.AirbyteMessage ->
                    m.type == io.airbyte.protocol.models.v0.AirbyteMessage.Type.STATE
                }
                .findFirst()
                .orElseThrow {
                    IllegalArgumentException(
                        "All message sets used for testing should include a state record"
                    )
                }!!

        Collections.reverse(destinationOutput)
        val actualStateMessage =
            destinationOutput
                .stream()
                .filter { it.type == Type.STATE }
                .findFirst()
                .map { msg: AirbyteMessage ->
                    // Modify state message to remove destination stats.
                    val clone = msg.state
                    clone.destinationStats = null
                    msg.state = clone
                    msg
                }
                .orElseGet {
                    Assertions.fail<Any>("Destination failed to output state")
                    null
                }

        Assertions.assertEquals(expectedStateMessage, actualStateMessage)
    }

    @Throws(Exception::class)
    private fun runSync(
        config: JsonNode,
        messages: List<AirbyteMessage>,
        catalog: ConfiguredAirbyteCatalog,
        runNormalization: Boolean
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

        val destination = destination

        destination.start(
            destinationConfig,
            jobRoot,
            inDestinationNormalizationFlags(runNormalization)
        )
        messages.forEach(
            Consumer { message: io.airbyte.protocol.models.v0.AirbyteMessage ->
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
        val normalizationRoot = Files.createDirectories(jobRoot!!.resolve("normalize"))
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
        messages: List<io.airbyte.protocol.models.v0.AirbyteMessage>,
        defaultSchema: String?
    ) {
        val actualMessages: MutableList<AirbyteRecordMessage> = ArrayList()
        for (stream in catalog.streams) {
            val streamName = stream.name
            val schema = if (stream.namespace != null) stream.namespace else defaultSchema!!
            val msgList =
                retrieveRecords(testEnv, streamName, schema, stream.jsonSchema)
                    .stream()
                    .map { data: JsonNode? ->
                        AirbyteRecordMessage()
                            .withStream(streamName)
                            .withNamespace(schema)
                            .withData(data)
                    }
                    .toList()
            actualMessages.addAll(msgList)
        }

        assertSameMessages(messages, actualMessages, false)
    }

    // ignores emitted at.
    protected fun assertSameMessages(
        expected: List<io.airbyte.protocol.models.v0.AirbyteMessage>,
        actual: List<AirbyteRecordMessage>,
        pruneAirbyteInternalFields: Boolean
    ) {
        val expectedProcessed =
            expected
                .stream()
                .filter { message: io.airbyte.protocol.models.v0.AirbyteMessage ->
                    message.type == io.airbyte.protocol.models.v0.AirbyteMessage.Type.RECORD
                }
                .map { obj: io.airbyte.protocol.models.v0.AirbyteMessage -> obj.record }
                .peek { recordMessage: AirbyteRecordMessage -> recordMessage.emittedAt = null }
                .map { recordMessage: AirbyteRecordMessage ->
                    if (pruneAirbyteInternalFields) safePrune(recordMessage) else recordMessage
                }
                .map { obj: AirbyteRecordMessage -> obj.data }
                .collect(Collectors.toList())

        val actualProcessed =
            actual
                .stream()
                .map { recordMessage: AirbyteRecordMessage ->
                    if (pruneAirbyteInternalFields) safePrune(recordMessage) else recordMessage
                }
                .map { obj: AirbyteRecordMessage -> obj.data }
                .collect(Collectors.toList())

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
                retrieveNormalizedRecords(testEnv, streamName, defaultSchema)
                    .stream()
                    .map { data: JsonNode? ->
                        AirbyteRecordMessage().withStream(streamName).withData(data)
                    }
                    .toList()
            actualMessages.addAll(msgList)
        }
        return actualMessages
    }

    class TestDestinationEnv(val localRoot: Path?) {
        override fun toString(): String {
            return "TestDestinationEnv{" + "localRoot=" + localRoot + '}'
        }
    }

    /**
     * This test MUST be disabled by default, but you may uncomment it and use when need to
     * reproduce a performance issue for destination. This test helps you to emulate lot's of stream
     * and messages in each simply changing the "streamsSize" args to set a number of tables\streams
     * and the "messagesNumber" to a messages number that would be written in each stream. !!! Do
     * NOT forget to manually remove all generated objects !!! Hint: To check the destination
     * container output run "docker ps" command in console to find the container's id. Then run
     * "docker container attach your_containers_id" (ex. docker container attach 18cc929f44c8) to
     * see the container's output
     */
    @Test
    @Disabled
    @Throws(Exception::class)
    fun testStressPerformance() {
        val streamsSize = 5 // number of generated streams
        val messagesNumber = 300 // number of msg to be written to each generated stream

        // Each stream will have an id and name fields
        val USERS_STREAM_NAME = "users" // stream's name prefix. Will get "user0", "user1", etc.
        val ID = "id"
        val NAME = "name"

        // generate schema\catalogs
        val configuredAirbyteStreams: MutableList<AirbyteStream> = ArrayList()
        for (i in 0 until streamsSize) {
            configuredAirbyteStreams.add(
                CatalogHelpers.createAirbyteStream(
                    USERS_STREAM_NAME + i,
                    Field.of(NAME, JsonSchemaType.STRING),
                    Field.of(ID, JsonSchemaType.STRING)
                )
            )
        }
        val testCatalog = AirbyteCatalog().withStreams(configuredAirbyteStreams)
        val configuredTestCatalog = CatalogHelpers.toDefaultConfiguredCatalog(testCatalog)

        val config = getConfig()
        val destinationConfig =
            WorkerDestinationConfig()
                .withConnectionId(UUID.randomUUID())
                .withCatalog(
                    convertProtocolObject(
                        configuredTestCatalog,
                        io.airbyte.protocol.models.ConfiguredAirbyteCatalog::class.java
                    )
                )
                .withDestinationConnectionConfiguration(config)
        val destination = destination

        // Start destination
        destination.start(destinationConfig, jobRoot, emptyMap())

        val currentStreamNumber = AtomicInteger(0)
        val currentRecordNumberForStream = AtomicInteger(0)

        // this is just a current state logger. Useful when running long hours tests to see the
        // progress
        val countPrinter = Thread {
            while (true) {
                println(
                    "currentStreamNumber=" +
                        currentStreamNumber +
                        ", currentRecordNumberForStream=" +
                        currentRecordNumberForStream +
                        ", " +
                        Instant.now()
                )
                try {
                    Thread.sleep(10000)
                } catch (e: InterruptedException) {
                    e.printStackTrace()
                }
            }
        }
        countPrinter.start()

        // iterate through streams
        for (streamCounter in 0 until streamsSize) {
            LOGGER.info("Started new stream processing with #$streamCounter")
            // iterate through msm inside a particular stream
            // Generate messages and put it to stream
            for (msgCounter in 0 until messagesNumber) {
                val msg =
                    io.airbyte.protocol.models.v0
                        .AirbyteMessage()
                        .withType(io.airbyte.protocol.models.v0.AirbyteMessage.Type.RECORD)
                        .withRecord(
                            AirbyteRecordMessage()
                                .withStream(USERS_STREAM_NAME + streamCounter)
                                .withData(
                                    Jsons.jsonNode(
                                        ImmutableMap.builder<Any, Any>()
                                            .put(NAME, LOREM_IPSUM)
                                            .put(ID, streamCounter.toString() + "_" + msgCounter)
                                            .build()
                                    )
                                )
                                .withEmittedAt(Instant.now().toEpochMilli())
                        )
                try {
                    destination.accept(
                        convertProtocolObject(
                            msg,
                            io.airbyte.protocol.models.AirbyteMessage::class.java
                        )
                    )
                } catch (e: Exception) {
                    LOGGER.error("Failed to write a RECORD message: $e")
                    throw RuntimeException(e)
                }

                currentRecordNumberForStream.set(msgCounter)
            }

            // send state message here, it's required
            val msgState =
                io.airbyte.protocol.models.v0
                    .AirbyteMessage()
                    .withType(io.airbyte.protocol.models.v0.AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withData(
                                Jsons.jsonNode(
                                    ImmutableMap.builder<Any, Any>()
                                        .put("start_date", "2020-09-02")
                                        .build()
                                )
                            )
                    )
            try {
                destination.accept(
                    convertProtocolObject(
                        msgState,
                        io.airbyte.protocol.models.AirbyteMessage::class.java
                    )
                )
            } catch (e: Exception) {
                LOGGER.error("Failed to write a STATE message: $e")
                throw RuntimeException(e)
            }

            currentStreamNumber.set(streamCounter)
        }

        LOGGER.info(
            String.format(
                "Added %s messages to each of %s streams",
                currentRecordNumberForStream,
                currentStreamNumber
            )
        )
        // Close destination
        destination.notifyEndOfInput()
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

    private fun checkTestCompatibility(
        testCompatibility: DataTypeTestArgumentProvider.TestCompatibility
    ): Boolean {
        return testCompatibility.isTestCompatible(
            supportBasicDataTypeTest(),
            supportArrayDataTypeTest(),
            supportObjectDataTypeTest()
        )
    }

    @ParameterizedTest
    @ArgumentsSource(DataTypeTestArgumentProvider::class)
    @Throws(Exception::class)
    open fun testDataTypeTestWithNormalization(
        messagesFilename: String,
        catalogFilename: String,
        testCompatibility: DataTypeTestArgumentProvider.TestCompatibility
    ) {
        if (!checkTestCompatibility(testCompatibility)) {
            return
        }

        val catalog = readCatalogFromFile(catalogFilename)
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages = readMessagesFromFile(messagesFilename)

        runAndCheck(catalog, configuredCatalog, messages)
    }

    @Test
    @Throws(Exception::class)
    fun testSyncNumberNanDataType() {
        // NaN/Infinity protocol supports started from V1 version or higher
        val numericTypesSupport = specialNumericTypesSupportTest
        if (getProtocolVersion() == ProtocolVersion.V0 || !numericTypesSupport.supportNumberNan) {
            return
        }
        val catalog =
            readCatalogFromFile(
                ArgumentProviderUtil.prefixFileNameByVersion(
                    DataTypeTestArgumentProvider.Companion.NUMBER_TYPE_CATALOG,
                    getProtocolVersion()
                )
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages =
            readMessagesFromFile(
                ArgumentProviderUtil.prefixFileNameByVersion(
                    DataTypeTestArgumentProvider.Companion.NAN_TYPE_MESSAGE,
                    getProtocolVersion()
                )
            )
        val config = getConfig()
        val defaultSchema = getDefaultSchema(config)

        runAndCheck(catalog, configuredCatalog, messages)
    }

    @Test
    @Throws(Exception::class)
    fun testSyncIntegerNanDataType() {
        // NaN/Infinity protocol supports started from V1 version or higher
        val numericTypesSupport = specialNumericTypesSupportTest
        if (getProtocolVersion() == ProtocolVersion.V0 || !numericTypesSupport.supportIntegerNan) {
            return
        }
        val catalog =
            readCatalogFromFile(
                ArgumentProviderUtil.prefixFileNameByVersion(
                    DataTypeTestArgumentProvider.Companion.INTEGER_TYPE_CATALOG,
                    getProtocolVersion()
                )
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages =
            readMessagesFromFile(
                ArgumentProviderUtil.prefixFileNameByVersion(
                    DataTypeTestArgumentProvider.Companion.NAN_TYPE_MESSAGE,
                    getProtocolVersion()
                )
            )
        val config = getConfig()
        val defaultSchema = getDefaultSchema(config)

        runAndCheck(catalog, configuredCatalog, messages)
    }

    @Test
    @Throws(Exception::class)
    fun testSyncNumberInfinityDataType() {
        // NaN/Infinity protocol supports started from V1 version or higher
        val numericTypesSupport = specialNumericTypesSupportTest
        if (
            getProtocolVersion() == ProtocolVersion.V0 || !numericTypesSupport.supportNumberInfinity
        ) {
            return
        }
        val catalog =
            readCatalogFromFile(
                ArgumentProviderUtil.prefixFileNameByVersion(
                    DataTypeTestArgumentProvider.Companion.NUMBER_TYPE_CATALOG,
                    getProtocolVersion()
                )
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages =
            readMessagesFromFile(
                ArgumentProviderUtil.prefixFileNameByVersion(
                    DataTypeTestArgumentProvider.Companion.INFINITY_TYPE_MESSAGE,
                    getProtocolVersion()
                )
            )
        val config = getConfig()
        val defaultSchema = getDefaultSchema(config)

        runAndCheck(catalog, configuredCatalog, messages)
    }

    @Test
    @Throws(Exception::class)
    fun testSyncIntegerInfinityDataType() {
        // NaN/Infinity protocol supports started from V1 version or higher
        val numericTypesSupport = specialNumericTypesSupportTest
        if (
            getProtocolVersion() == ProtocolVersion.V0 ||
                !numericTypesSupport.supportIntegerInfinity
        ) {
            return
        }
        val catalog =
            readCatalogFromFile(
                ArgumentProviderUtil.prefixFileNameByVersion(
                    DataTypeTestArgumentProvider.Companion.INTEGER_TYPE_CATALOG,
                    getProtocolVersion()
                )
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages =
            readMessagesFromFile(
                ArgumentProviderUtil.prefixFileNameByVersion(
                    DataTypeTestArgumentProvider.Companion.INFINITY_TYPE_MESSAGE,
                    getProtocolVersion()
                )
            )
        val config = getConfig()
        val defaultSchema = getDefaultSchema(config)

        runAndCheck(catalog, configuredCatalog, messages)
    }

    @Throws(Exception::class)
    private fun runAndCheck(
        catalog: AirbyteCatalog,
        configuredCatalog: io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog,
        messages: List<io.airbyte.protocol.models.v0.AirbyteMessage>
    ) {
        if (normalizationFromDefinition()) {
            LOGGER.info("Normalization is supported! Run test with normalization.")
            runAndCheckWithNormalization(messages, configuredCatalog, catalog)
        } else {
            LOGGER.info("Normalization is not supported! Run test without normalization.")
            runAndCheckWithoutNormalization(messages, configuredCatalog, catalog)
        }
    }

    @Throws(Exception::class)
    private fun runAndCheckWithNormalization(
        messages: List<io.airbyte.protocol.models.v0.AirbyteMessage>,
        configuredCatalog: io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog,
        catalog: AirbyteCatalog
    ) {
        val config = getConfig()
        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, true)

        val actualMessages = retrieveNormalizedRecords(catalog, getDefaultSchema(config))
        assertSameMessages(messages, actualMessages, true)
    }

    @Throws(Exception::class)
    private fun runAndCheckWithoutNormalization(
        messages: List<io.airbyte.protocol.models.v0.AirbyteMessage>,
        configuredCatalog: io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog,
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
                .stream()
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
        }

        companion object {
            const val NAMESPACE_TEST_CASES_JSON: String = "namespace_test_cases.json"
        }
    }

    private fun supportsNormalization(): Boolean {
        return supportsInDestinationNormalization() || normalizationFromDefinition()
    }

    companion object {
        private val RANDOM = Random()
        private const val NORMALIZATION_VERSION = "dev"

        private const val JOB_ID = "0"
        private const val JOB_ATTEMPT = 0

        private const val DUMMY_CATALOG_NAME = "DummyCatalog"

        private val LOGGER: Logger = LoggerFactory.getLogger(DestinationAcceptanceTest::class.java)

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
                    airbyteInternalFields.stream().anyMatch { internalField: String ->
                        key.lowercase(Locale.getDefault())
                            .contains(internalField.lowercase(Locale.getDefault()))
                    } || json[key].isNull
                ) {
                    (json as ObjectNode).remove(key)
                }
            }
        }

        private const val LOREM_IPSUM =
            ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque malesuada lacinia aliquet. Nam feugiat mauris vel magna dignissim feugiat. Nam non dapibus sapien, ac mattis purus. Donec mollis libero erat, a rutrum ipsum pretium id. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Integer nec aliquam leo. Aliquam eu dictum augue, a ornare elit.\n" +
                "\n" +
                "Nulla viverra blandit neque. Nam blandit varius efficitur. Nunc at sapien blandit, malesuada lectus vel, tincidunt orci. Proin blandit metus eget libero facilisis interdum. Aenean luctus scelerisque orci, at scelerisque sem vestibulum in. Nullam ornare massa sed dui efficitur, eget volutpat lectus elementum. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Integer elementum mi vitae erat eleifend iaculis. Nullam eget tincidunt est, eget tempor est. Sed risus velit, iaculis vitae est in, volutpat consectetur odio. Aenean ut fringilla elit. Suspendisse non aliquet massa. Curabitur suscipit metus nunc, nec porttitor velit venenatis vel. Fusce vestibulum eleifend diam, lobortis auctor magna.\n" +
                "\n" +
                "Etiam maximus, mi feugiat pharetra mattis, nulla neque euismod metus, in congue nunc sem nec ligula. Curabitur aliquam, risus id convallis cursus, nunc orci sollicitudin enim, quis scelerisque nibh dui in ipsum. Suspendisse mollis, metus a dapibus scelerisque, sapien nulla pretium ipsum, non finibus sem orci et lectus. Aliquam dictum magna nisi, a consectetur urna euismod nec. In pulvinar facilisis nulla, id mollis libero pulvinar vel. Nam a commodo leo, eu commodo dolor. In hac habitasse platea dictumst. Curabitur auctor purus quis tortor laoreet efficitur. Quisque tincidunt, risus vel rutrum fermentum, libero urna dignissim augue, eget pulvinar nibh ligula ut tortor. Vivamus convallis non risus sed consectetur. Etiam accumsan enim ac nisl suscipit, vel congue lorem volutpat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce non orci quis lacus rhoncus vestibulum nec ut magna. In varius lectus nec quam posuere finibus. Vivamus quis lectus vitae tortor sollicitudin fermentum.\n" +
                "\n" +
                "Pellentesque elementum vehicula egestas. Sed volutpat velit arcu, at imperdiet sapien consectetur facilisis. Suspendisse porttitor tincidunt interdum. Morbi gravida faucibus tortor, ut rutrum magna tincidunt a. Morbi eu nisi eget dui finibus hendrerit sit amet in augue. Aenean imperdiet lacus enim, a volutpat nulla placerat at. Suspendisse nibh ipsum, venenatis vel maximus ut, fringilla nec felis. Sed risus mi, egestas quis quam ullamcorper, pharetra vestibulum diam.\n" +
                "\n" +
                "Praesent finibus scelerisque elit, accumsan condimentum risus mattis vitae. Donec tristique hendrerit facilisis. Curabitur metus purus, venenatis non elementum id, finibus eu augue. Quisque posuere rhoncus ligula, et vehicula erat pulvinar at. Pellentesque vel quam vel lectus tincidunt congue quis id sapien. Ut efficitur mauris vitae pretium iaculis. Aliquam consectetur iaculis nisi vitae laoreet. Integer vel odio quis diam mattis tempor eget nec est. Donec iaculis facilisis neque, at dictum magna vestibulum ut. Sed malesuada non nunc ac consequat. Maecenas tempus lectus a nisl congue, ac venenatis diam viverra. Nam ac justo id nulla iaculis lobortis in eu ligula. Vivamus et ligula id sapien efficitur aliquet. Curabitur est justo, tempus vitae mollis quis, tincidunt vitae felis. Vestibulum molestie laoreet justo, nec mollis purus vulputate at.")

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

        @Throws(IOException::class)
        private fun readCatalogFromFile(catalogFilename: String): AirbyteCatalog {
            return Jsons.deserialize(
                MoreResources.readResource(catalogFilename),
                AirbyteCatalog::class.java
            )
        }

        @Throws(IOException::class)
        private fun readMessagesFromFile(
            messagesFilename: String
        ): List<io.airbyte.protocol.models.v0.AirbyteMessage> {
            return MoreResources.readResource(messagesFilename).lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }
        }

        /** Mutate the input airbyte record message namespace. */
        private fun getRecordMessagesWithNewNamespace(
            airbyteMessages: List<io.airbyte.protocol.models.v0.AirbyteMessage>,
            namespace: String?
        ): List<io.airbyte.protocol.models.v0.AirbyteMessage> {
            airbyteMessages.forEach(
                Consumer { message: io.airbyte.protocol.models.v0.AirbyteMessage ->
                    if (message.record != null) {
                        message.record.namespace = namespace
                    }
                }
            )
            return airbyteMessages
        }

        private fun <V0, V1> convertProtocolObject(v1: V1, klass: Class<V0>): V0 {
            return Jsons.`object`(Jsons.jsonNode(v1), klass)
        }
    }
}
