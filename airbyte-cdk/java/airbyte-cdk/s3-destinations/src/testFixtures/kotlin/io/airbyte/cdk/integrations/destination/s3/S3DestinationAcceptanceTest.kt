/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.DeleteObjectsRequest
import com.amazonaws.services.s3.model.S3ObjectSummary
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.s3.util.S3NameTransformer
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataArgumentsProvider
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import io.airbyte.commons.io.IOs
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import io.airbyte.workers.exception.TestHarnessException
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path
import java.time.Instant
import java.util.*
import org.apache.commons.lang3.RandomStringUtils
import org.joda.time.DateTime
import org.joda.time.DateTimeZone
import org.junit.jupiter.api.Assumptions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.mockito.Mockito.mock

private val LOGGER = KotlinLogging.logger {}
/**
 * When adding a new S3 destination acceptance test, extend this class and do the following:
 * * Implement [.getFormatConfig] that returns a [UploadFormatConfig]
 * * Implement [.retrieveRecords] that returns the Json records for the test
 *
 * Under the hood, a [S3DestinationConfig] is constructed as follows:
 * * Retrieve the secrets from "secrets/config.json"
 * * Get the S3 bucket path from the constructor
 * * Get the format config from [.getFormatConfig]
 */
abstract class S3DestinationAcceptanceTest
protected constructor(
    protected val outputFormat: FileUploadFormat,
    supportsChangeCapture: Boolean = false,
    expectNumericTimestamps: Boolean = false,
    expectSchemalessObjectsCoercedToStrings: Boolean = false,
    expectUnionsPromotedToDisjointRecords: Boolean = false
) :
    DestinationAcceptanceTest(
        verifyIndividualStateAndCounts = true,
        useV2Fields = true,
        supportsChangeCapture = supportsChangeCapture,
        expectNumericTimestamps = expectNumericTimestamps,
        expectSchemalessObjectsCoercedToStrings = expectSchemalessObjectsCoercedToStrings,
        expectUnionsPromotedToDisjointRecords = expectUnionsPromotedToDisjointRecords
    ) {
    protected val secretFilePath: String = "secrets/config.json"
    protected var configJson: JsonNode? = null
    protected var s3DestinationConfig: S3DestinationConfig = mock()
    protected var s3Client: AmazonS3? = null
    protected var s3nameTransformer: NamingConventionTransformer = mock()
    protected var s3StorageOperations: S3StorageOperations? = null

    protected open val baseConfigJson: JsonNode
        get() = Jsons.deserialize(IOs.readFile(Path.of(secretFilePath)))

    override val imageName: String
        get() = "airbyte/destination-s3:dev"

    override fun getDefaultSchema(config: JsonNode): String? {
        if (config.has("s3_bucket_path")) {
            return config["s3_bucket_path"].asText()
        }
        return null
    }

    override fun getConfig(): JsonNode = configJson!!

    override fun getFailCheckConfig(): JsonNode {
        val baseJson = baseConfigJson
        val failCheckJson = Jsons.clone(baseJson)
        // invalid credential
        (failCheckJson as ObjectNode).put("access_key_id", "fake-key")
        failCheckJson.put("secret_access_key", "fake-secret")
        return failCheckJson
    }

    /** Helper method to retrieve all synced objects inside the configured bucket path. */
    protected fun getAllSyncedObjects(
        streamName: String,
        namespace: String
    ): List<S3ObjectSummary> {
        val namespaceStr = s3nameTransformer.getNamespace(namespace)
        val streamNameStr = s3nameTransformer.getIdentifier(streamName)
        val outputPrefix =
            s3StorageOperations!!.getBucketObjectPath(
                namespaceStr,
                streamNameStr,
                DateTime.now(DateTimeZone.UTC),
                s3DestinationConfig.pathFormat!!,
            )
        // the child folder contains a non-deterministic epoch timestamp, so use the parent folder
        val parentFolder = outputPrefix.substring(0, outputPrefix.lastIndexOf("/") + 1)
        val objectSummaries =
            s3Client!!
                .listObjects(s3DestinationConfig.bucketName, parentFolder)
                .objectSummaries
                .filter { o: S3ObjectSummary -> o.key.contains("$streamNameStr/") }
                .sortedWith(Comparator.comparingLong { o: S3ObjectSummary -> o.lastModified.time })

        LOGGER.info {
            "${"All objects: {}"} ${
                objectSummaries.map { o: S3ObjectSummary ->
                    String.format("%s/%s", o.bucketName, o.key)
                }
            }"
        }
        return objectSummaries
    }

    protected abstract val formatConfig: JsonNode?
        get

    /**
     * This method does the following:
     * * Construct the S3 destination config.
     * * Construct the S3 client.
     */
    override fun setup(testEnv: TestDestinationEnv, TEST_SCHEMAS: HashSet<String>) {
        val baseConfigJson = baseConfigJson
        // Set a random s3 bucket path for each integration test
        val configJson = Jsons.clone(baseConfigJson)
        val testBucketPath =
            String.format(
                "%s_test_%s",
                outputFormat.name.lowercase(),
                RandomStringUtils.randomAlphanumeric(5),
            )
        (configJson as ObjectNode)
            .put("s3_bucket_path", testBucketPath)
            .set<JsonNode>("format", formatConfig)
        this.configJson = configJson
        this.s3DestinationConfig =
            S3DestinationConfig.getS3DestinationConfig(
                configJson,
                storageProvider(),
                getConnectorEnv()
            )
        LOGGER.info {
            "${"Test full path: {}/{}"} ${s3DestinationConfig.bucketName} ${s3DestinationConfig.bucketPath}"
        }

        this.s3Client = s3DestinationConfig.getS3Client()
        this.s3nameTransformer = S3NameTransformer()
        this.s3StorageOperations =
            S3StorageOperations(s3nameTransformer, s3Client!!, s3DestinationConfig)
    }

    /** Remove all the S3 output from the tests. */
    override fun tearDown(testEnv: TestDestinationEnv) {
        val keysToDelete: MutableList<DeleteObjectsRequest.KeyVersion> = LinkedList()
        val objects =
            s3Client!!
                .listObjects(s3DestinationConfig.bucketName, s3DestinationConfig.bucketPath)
                .objectSummaries
        for (`object` in objects) {
            keysToDelete.add(DeleteObjectsRequest.KeyVersion(`object`.key))
        }

        if (keysToDelete.size > 0) {
            LOGGER.info {
                "${"Tearing down test bucket path: {}/{}"} ${s3DestinationConfig.bucketName} ${s3DestinationConfig.bucketPath}"
            }
            val result =
                s3Client!!.deleteObjects(
                    DeleteObjectsRequest(s3DestinationConfig.bucketName).withKeys(keysToDelete),
                )
            LOGGER.info { "${"Deleted {} file(s)."} ${result.deletedObjects.size}" }
        }
    }

    override fun getTestDataComparator(): TestDataComparator = AdvancedTestDataComparator()

    override fun supportBasicDataTypeTest(): Boolean {
        return true
    }

    override fun supportArrayDataTypeTest(): Boolean {
        return true
    }

    override fun supportObjectDataTypeTest(): Boolean {
        return true
    }

    fun storageProvider(): StorageProvider {
        return StorageProvider.AWS_S3
    }

    private fun getTestCatalog(
        syncMode: SyncMode,
        destinationSyncMode: DestinationSyncMode,
        syncId: Long?,
        minimumGenerationId: Long?,
        generationId: Long?
    ): Pair<ConfiguredAirbyteCatalog, AirbyteCatalog> {
        val catalog =
            Jsons.deserialize(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog.streams.forEach {
            it.withSyncMode(syncMode)
                .withDestinationSyncMode(destinationSyncMode)
                .withSyncId(syncId)
                .withGenerationId(generationId)
                .withMinimumGenerationId(minimumGenerationId)
        }
        return Pair(configuredCatalog, catalog)
    }

    private fun getFirstSyncMessagesFixture1(
        configuredCatalog: ConfiguredAirbyteCatalog,
        streamStatus: AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
    ): List<AirbyteMessage> {
        val descriptor = StreamDescriptor().withName(configuredCatalog.streams[0].stream.name)
        return listOf(
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(configuredCatalog.streams[0].stream.name)
                        .withEmittedAt(Instant.now().toEpochMilli())
                        .withData(
                            Jsons.jsonNode(
                                ImmutableMap.builder<Any, Any>()
                                    .put("id", 1)
                                    .put("currency", "USD")
                                    .put("date", "2020-03-31T00:00:00Z")
                                    .put("HKD", 10.1)
                                    .put("NZD", 700.1)
                                    .build(),
                            ),
                        ),
                ),
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withData(Jsons.jsonNode(ImmutableMap.of("checkpoint", 2))),
                ),
            AirbyteMessage()
                .withType(AirbyteMessage.Type.TRACE)
                .withTrace(
                    AirbyteTraceMessage()
                        .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                        .withStreamStatus(
                            AirbyteStreamStatusTraceMessage()
                                .withStreamDescriptor(descriptor)
                                .withStatus(streamStatus)
                        ),
                ),
        )
    }

    private fun getSyncMessagesFixture2(): List<AirbyteMessage> {
        return MoreResources.readResource(
                DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                    getProtocolVersion(),
                ),
            )
            .trim()
            .lines()
            .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
    }

    /**
     * Test 2 runs before refreshes support and after refreshes support in OVERWRITE mode. Verifies
     * we clean up after ourselves correctly.
     */
    @Test
    fun testOverwriteSyncPreRefreshAndPostSupport() {
        assumeTrue(
            implementsOverwrite(),
            "Destination's spec.json does not support overwrite sync mode."
        )

        // Run sync with OLD version connector
        val catalogPair =
            getTestCatalog(SyncMode.FULL_REFRESH, DestinationSyncMode.OVERWRITE, 42, null, null)
        val config = getConfig()
        val firstSyncMessages =
            getFirstSyncMessagesFixture1(
                catalogPair.first,
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE,
            )
        // Old connector doesn't have destinationStats so skip checking that.
        runSyncAndVerifyStateOutput(
            config,
            firstSyncMessages,
            catalogPair.first,
            runNormalization = false,
            "airbyte/destination-s3:0.6.4",
            verifyIndividualStateAndCounts = false,
        )

        // This simulates first sync after enabling generationId in connector. null -> 1.
        // legend has it that platform always increments to 1 and sends min and gen id as 1.
        val catalogPair2 =
            getTestCatalog(SyncMode.FULL_REFRESH, DestinationSyncMode.OVERWRITE, 43, 1, 1)

        // Run and verify only second sync messages are present.
        val secondSyncMessages = getSyncMessagesFixture2()
        runSyncAndVerifyStateOutput(config, secondSyncMessages, catalogPair2.first, false)

        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(
            catalogPair2.second,
            secondSyncMessages,
            defaultSchema
        )
    }

    /**
     * This test is an impractical case. Running twice in APPEND mode with incrementing
     * generationIds, switching to OVERWRITE mode without incrementing generationId This verifies
     * that the previous data (including old generations data) is preserved. We don't know if the
     * old data is synced in which mode this uses generationId as source of truth to NOT touch
     * existing data.
     */
    @Test
    fun testSwitchingModesSyncWithPreviousData() {
        assumeTrue(
            implementsOverwrite(),
            "Destination's spec.json does not support overwrite sync mode."
        )

        // Run sync with some messages and send incomplete status.
        // This is to simulate crash
        val catalogPair =
            getTestCatalog(SyncMode.FULL_REFRESH, DestinationSyncMode.APPEND, 42, 0, 1)
        val config = getConfig()
        val firstSyncMessages = getSyncMessagesFixture2()
        runSyncAndVerifyStateOutput(config, firstSyncMessages, catalogPair.first, false)

        // Run second sync, even though the previous one was incomplete, intentionally incrementing
        // genId and minGenId
        // to test erratic behavior and we don't accidentally clean up stuff.
        val catalogPair2 =
            getTestCatalog(SyncMode.FULL_REFRESH, DestinationSyncMode.APPEND, 43, 0, 2)

        // Run and verify only second sync messages are present.
        val secondSyncMessages = getSyncMessagesFixture2()
        runSyncAndVerifyStateOutput(config, secondSyncMessages, catalogPair2.first, false)

        // Run third sync.
        val catalogPair3 =
            getTestCatalog(SyncMode.FULL_REFRESH, DestinationSyncMode.OVERWRITE, 44, 2, 2)

        // Run and verify only second sync messages are present.
        val thirdSyncMessages = getSyncMessagesFixture2()
        runSyncAndVerifyStateOutput(config, thirdSyncMessages, catalogPair3.first, false)

        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(
            catalogPair3.second,
            firstSyncMessages + secondSyncMessages,
            defaultSchema
        )
    }

    /** Test runs 2 successfull overwrite syncs and verifies last sync is preserved */
    @Test
    fun testOverwriteSyncSubsequentGenerations() {
        assumeTrue(
            implementsOverwrite(),
            "Destination's spec.json does not support overwrite sync mode."
        )

        // Run sync with some messages
        val catalogPair =
            getTestCatalog(SyncMode.FULL_REFRESH, DestinationSyncMode.OVERWRITE, 42, 12, 12)
        val config = getConfig()
        val firstSyncMessages =
            getFirstSyncMessagesFixture1(
                catalogPair.first,
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE,
            )
        runSyncAndVerifyStateOutput(config, firstSyncMessages, catalogPair.first, false)

        // Change the generationId, we always assume platform sends a monotonically increasing
        // number
        val catalogPair2 =
            getTestCatalog(SyncMode.FULL_REFRESH, DestinationSyncMode.OVERWRITE, 43, 13, 13)

        // Run and verify only second sync messages are present.
        val secondSyncMessages = getSyncMessagesFixture2()
        runSyncAndVerifyStateOutput(config, secondSyncMessages, catalogPair2.first, false)

        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(
            catalogPair2.second,
            secondSyncMessages,
            defaultSchema
        )
    }

    /**
     * Test runs 1 failed and 1 successful OVERWRITE sync of same generation. Verified data from
     * both syncs are preserved.
     */
    @Test
    fun testOverwriteSyncFailedResumedGeneration() {
        assumeTrue(
            implementsOverwrite(),
            "Destination's spec.json does not support overwrite sync mode."
        )
        val config = getConfig()

        // Run sync with some messages and incomplete stream status
        val catalogPair =
            getTestCatalog(SyncMode.FULL_REFRESH, DestinationSyncMode.OVERWRITE, 42, 12, 12)
        val firstSyncMessages: List<AirbyteMessage> =
            getFirstSyncMessagesFixture1(
                catalogPair.first,
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.INCOMPLETE
            )
        assertThrows<TestHarnessException>(
            "Should not succeed the sync when Trace message is INCOMPLETE"
        ) { runSyncAndVerifyStateOutput(config, firstSyncMessages, catalogPair.first, false) }

        // Run second sync with the same messages from the previous failed sync.
        val secondSyncMessages = getSyncMessagesFixture2()
        runSyncAndVerifyStateOutput(config, secondSyncMessages, catalogPair.first, false)

        // verify records are preserved from first failed sync + second sync.
        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(
            catalogPair.second,
            firstSyncMessages + secondSyncMessages,
            defaultSchema
        )
    }

    /** Test runs 2 failed syncs and verifies the previous sync objects are not cleaned up. */
    @Test
    fun testOverwriteSyncMultipleFailedGenerationsFilesPreserved() {
        assumeTrue(
            implementsOverwrite(),
            "Destination's spec.json does not support overwrite sync mode."
        )
        val config = getConfig()

        // Run first failed attempt of same generation
        val catalogPair =
            getTestCatalog(SyncMode.FULL_REFRESH, DestinationSyncMode.OVERWRITE, 42, 12, 12)
        val firstSyncMessages: List<AirbyteMessage> =
            getFirstSyncMessagesFixture1(
                catalogPair.first,
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.INCOMPLETE
            )
        assertThrows<TestHarnessException>(
            "Should not succeed the sync when Trace message is INCOMPLETE"
        ) { runSyncAndVerifyStateOutput(config, firstSyncMessages, catalogPair.first, false) }

        // Run second failed attempt of same generation
        val catalogPair2 =
            getTestCatalog(SyncMode.FULL_REFRESH, DestinationSyncMode.OVERWRITE, 43, 12, 12)
        val secondSyncMessages =
            getFirstSyncMessagesFixture1(
                catalogPair2.first,
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.INCOMPLETE
            )

        assertThrows<TestHarnessException>(
            "Should not succeed the sync when Trace message is INCOMPLETE"
        ) { runSyncAndVerifyStateOutput(config, secondSyncMessages, catalogPair2.first, false) }

        // Verify our delayed delete logic creates no data downtime.
        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(
            catalogPair.second,
            firstSyncMessages + secondSyncMessages,
            defaultSchema
        )

        // Run a successful sync with incremented generationId, This should nuke all old generation
        // files which were preserved.
        val catalogPair3 =
            getTestCatalog(SyncMode.FULL_REFRESH, DestinationSyncMode.OVERWRITE, 43, 13, 13)
        val thirdSyncMessages = getSyncMessagesFixture2()
        runSyncAndVerifyStateOutput(config, thirdSyncMessages, catalogPair3.first, false)

        retrieveRawRecordsAndAssertSameMessages(
            catalogPair.second,
            thirdSyncMessages,
            defaultSchema
        )
    }

    /**
     * Test runs 2 successful OVERWRITE syncs but with same generation and a sync to another catalog
     * with no generationId, this shouldn't happen from platform but acts as a simulation for
     * failure of first sync. This verifies that data from both syncs are preserved and the
     * unrelated catalog sync data is untouched too.
     */
    @Test
    fun testOverwriteSyncWithGenerationId() {
        assumeTrue(
            implementsOverwrite(),
            "Destination's spec.json does not support overwrite sync mode."
        )

        val config = getConfig()

        // First Sync
        val catalogPair =
            getTestCatalog(SyncMode.FULL_REFRESH, DestinationSyncMode.OVERWRITE, 42, 12, 12)
        val firstSyncMessages: List<AirbyteMessage> =
            getFirstSyncMessagesFixture1(
                catalogPair.first,
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE
            )
        runSyncAndVerifyStateOutput(config, firstSyncMessages, catalogPair.first, false)

        // We need to make sure that other streams\tables\files in the same location will not be
        // affected\deleted\overridden by our activities during first, second or any future sync.
        // So let's create a dummy data that will be checked after all sync. It should remain the
        // same
        val dummyCatalogStream = "DummyStream"
        val dummyCatalog =
            Jsons.deserialize(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        dummyCatalog.streams[0].name = dummyCatalogStream
        val configuredDummyCatalog = CatalogHelpers.toDefaultConfiguredCatalog(dummyCatalog)
        configuredDummyCatalog.streams.forEach {
            it.withSyncId(42).withGenerationId(20).withMinimumGenerationId(20)
        }
        // update messages to set new dummy stream name
        firstSyncMessages
            .filter { message: AirbyteMessage -> message.record != null }
            .forEach { message: AirbyteMessage -> message.record.stream = dummyCatalogStream }
        firstSyncMessages
            .filter { message: AirbyteMessage -> message.type == AirbyteMessage.Type.TRACE }
            .forEach { message: AirbyteMessage ->
                message.trace.streamStatus.streamDescriptor.name = dummyCatalogStream
            }
        // sync dummy data
        runSyncAndVerifyStateOutput(config, firstSyncMessages, configuredDummyCatalog, false)

        // Run second sync
        val secondSyncMessages: List<AirbyteMessage> = getSyncMessagesFixture2()
        runSyncAndVerifyStateOutput(config, secondSyncMessages, catalogPair.first, false)

        // Verify records of both syncs are preserved.
        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(
            catalogPair.second,
            firstSyncMessages + secondSyncMessages,
            defaultSchema
        )
        // verify that other streams in the same location were not affected. If something fails
        // here,
        // then this need to be fixed in connectors logic to override only required streams
        retrieveRawRecordsAndAssertSameMessages(dummyCatalog, firstSyncMessages, defaultSchema)
    }

    /**
     * This test is similar to testIncrementalSync with adding generationId to the ConfiguredCatalog
     * This verifies that the core behavior of APPEND mode sync is unaltered when the
     * minimumGenerationId is set to 0
     */
    @Test
    @Throws(Exception::class)
    fun testIncrementalSyncWithGenerationId() {
        assumeTrue(
            implementsAppend(),
            "Destination's spec.json does not include '\"supportsIncremental\" ; true'"
        )

        val catalogPair =
            getTestCatalog(SyncMode.INCREMENTAL, DestinationSyncMode.APPEND, 42, 0, 12)
        val config = getConfig()

        // First sync
        val firstSyncMessages: List<AirbyteMessage> =
            getFirstSyncMessagesFixture1(
                catalogPair.first,
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE,
            )
        runSyncAndVerifyStateOutput(config, firstSyncMessages, catalogPair.first, false)

        // Second sync
        val secondSyncMessages: List<AirbyteMessage> = getSyncMessagesFixture2()
        runSyncAndVerifyStateOutput(config, secondSyncMessages, catalogPair.first, false)

        // Verify records
        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(
            catalogPair.second,
            firstSyncMessages + secondSyncMessages,
            defaultSchema
        )
    }

    /**
     * Test 2 runs before refreshes support and after refreshes support in APPEND mode. Verifies we
     * don't accidentally delete any data when generationId is encountered.
     */
    @Test
    fun testAppendSyncPreRefreshAndPostSupport() {
        assumeTrue(
            implementsOverwrite(),
            "Destination's spec.json does not support overwrite sync mode."
        )

        // Run sync with some messages
        val catalogPair =
            getTestCatalog(SyncMode.FULL_REFRESH, DestinationSyncMode.APPEND, 42, null, null)
        val config = getConfig()
        val firstSyncMessages =
            getFirstSyncMessagesFixture1(
                catalogPair.first,
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE,
            )
        // Old connector doesn't have destinationStats so skip checking that.
        runSyncAndVerifyStateOutput(
            config,
            firstSyncMessages,
            catalogPair.first,
            runNormalization = false,
            "airbyte/destination-s3:0.6.4",
            verifyIndividualStateAndCounts = false,
        )

        // This simulates first sync after enabling generationId in connector. null -> 0.
        // Apparently we encountered a behavior where for APPEND mode min and genID are not
        // incremented and sent as 0
        val catalogPair2 =
            getTestCatalog(SyncMode.FULL_REFRESH, DestinationSyncMode.APPEND, 43, 0, 0)

        // Run and verify only second sync messages are present.
        val secondSyncMessages = getSyncMessagesFixture2()
        runSyncAndVerifyStateOutput(config, secondSyncMessages, catalogPair2.first, false)

        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(
            catalogPair2.second,
            firstSyncMessages + secondSyncMessages,
            defaultSchema
        )
    }

    companion object {

        @JvmStatic protected val MAPPER: ObjectMapper = MoreMappers.initMapper()
    }
}
