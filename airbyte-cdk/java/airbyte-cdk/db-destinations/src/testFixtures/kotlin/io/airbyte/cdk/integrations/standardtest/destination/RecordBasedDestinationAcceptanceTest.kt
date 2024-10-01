package io.airbyte.cdk.integrations.standardtest.destination

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import com.google.common.collect.Sets
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataArgumentsProvider
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.protocol.models.v0.*
import io.github.oshai.kotlinlogging.KotlinLogging
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Assumptions
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ArgumentsSource
import java.time.*
import java.util.*

private val LOGGER = KotlinLogging.logger {}

abstract class RecordBasedDestinationAcceptanceTest(
    private val useV2Fields: Boolean = false,
    private val supportsChangeCapture: Boolean = false,
    private val expectNumericTimestamps: Boolean = false,
    private val expectSchemalessObjectsCoercedToStrings: Boolean = false,
    private val expectUnionsPromotedToDisjointRecords: Boolean = false
): DestinationAcceptanceTest(){

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
        configuredCatalog.streams.forEach {
            it.withSyncId(42).withGenerationId(12).withMinimumGenerationId(12)
        }
        val messages: List<AirbyteMessage> =
            MoreResources.readResource(messagesFilename).trim().lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }

        /* Replicate the runs of messages and state hundreds of times, but keep trace messages at the end. */
        val lotsOfRecordAndStateBlocks =
            Collections.nCopies(
                400,
                messages.filter { it.type == AirbyteMessage.Type.RECORD || it.type == AirbyteMessage.Type.STATE }
            )
        val traceMessages = messages.filter { it.type == AirbyteMessage.Type.TRACE }
        val concatenated = lotsOfRecordAndStateBlocks.flatten() + traceMessages

        val config = getConfig()
        runSyncAndVerifyStateOutput(config, concatenated, configuredCatalog, false)
    }


    /** Verify that the integration overwrites the first sync with the second sync. */
    @Test
    @Throws(Exception::class)
    fun testSecondSync() {
        if (!implementsOverwrite()) {
            LOGGER.info { "Destination's spec.json does not support overwrite sync mode." }
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
        configuredCatalog.streams.forEach {
            it.withSyncId(42).withGenerationId(12).withMinimumGenerationId(12)
        }
        val firstSyncMessages: List<AirbyteMessage> =
            MoreResources.readResource(
                DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                    getProtocolVersion()
                )
            )
                .trim()
                .lines()
                .map { Jsons.deserialize<AirbyteMessage>(it, AirbyteMessage::class.java) }

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
        configuredDummyCatalog.streams.forEach {
            it.withSyncId(42).withGenerationId(20).withMinimumGenerationId(20)
        }
        // update messages to set new dummy stream name
        firstSyncMessages
            .filter { message: AirbyteMessage -> message.record != null }
            .forEach { message: AirbyteMessage -> message.record.stream = DUMMY_CATALOG_NAME }
        firstSyncMessages
            .filter { message: AirbyteMessage -> message.type == AirbyteMessage.Type.TRACE }
            .forEach { message: AirbyteMessage ->
                message.trace.streamStatus.streamDescriptor.name = DUMMY_CATALOG_NAME
            }
        // sync dummy data
        runSyncAndVerifyStateOutput(config, firstSyncMessages, configuredDummyCatalog, false)

        // Run second sync
        val configuredCatalog2 = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog2.streams.forEach {
            it.withSyncId(43).withGenerationId(13).withMinimumGenerationId(13)
        }
        val descriptor = StreamDescriptor().withName(catalog.streams[0].name)
        val secondSyncMessages: List<AirbyteMessage> =
            Lists.newArrayList(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
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
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withData(Jsons.jsonNode(ImmutableMap.of("checkpoint", 2)))
                    ),
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.TRACE)
                    .withTrace(
                        AirbyteTraceMessage()
                            .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                            .withStreamStatus(
                                AirbyteStreamStatusTraceMessage()
                                    .withStreamDescriptor(descriptor)
                                    .withStatus(
                                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE
                                    )
                            )
                    )
            )

        runSyncAndVerifyStateOutput(config, secondSyncMessages, configuredCatalog2, false)
        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(catalog, secondSyncMessages, defaultSchema)

        // verify that other streams in the same location were not affected. If something fails
        // here,
        // then this need to be fixed in connectors logic to override only required streams
        retrieveRawRecordsAndAssertSameMessages(dummyCatalog, firstSyncMessages, defaultSchema)
    }

    @Test
    @Throws(Exception::class)
    open fun testAirbyteFields() {
        val configuredCatalog =
            Jsons.deserialize(
                MoreResources.readResource("v0/users_with_generation_id_configured_catalog.json"),
                ConfiguredAirbyteCatalog::class.java
            )
        val config = getConfig()
        val messages =
            MoreResources.readResource("v0/users_with_generation_id_messages.txt")
                .trim()
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
        val preRunTime = Instant.now()
        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false)
        val generationId = configuredCatalog.streams[0].generationId
        val stream = configuredCatalog.streams[0].stream
        val destinationOutput =
            retrieveRecords(
                testEnv,
                "users",
                getDefaultSchema(config)!! /* ignored */,
                stream.jsonSchema
            )

        // Resolve common field keys.
        val abIdKey: String =
            if (useV2Fields) JavaBaseConstants.COLUMN_NAME_AB_RAW_ID
            else JavaBaseConstants.COLUMN_NAME_AB_ID
        val abTsKey =
            if (useV2Fields) JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT
            else JavaBaseConstants.COLUMN_NAME_EMITTED_AT

        // Validate airbyte fields as much as possible
        val uuidRegex = "[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
        val zippedMessages = messages.take(destinationOutput.size).zip(destinationOutput)
        zippedMessages.forEach { (message, record) ->
            // Ensure the id is UUID4 format (best we can do without mocks)
            Assertions.assertTrue(record.get(abIdKey).asText().matches(Regex(uuidRegex)))
            Assertions.assertEquals(message.record.emittedAt, record.get(abTsKey).asLong())

            if (useV2Fields) {
                // Generation id should match the one from the catalog
                Assertions.assertEquals(
                    generationId,
                    record.get(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID).asLong()
                )
            }
        }

        // Regardless of whether change failures are capatured, all v2
        // destinations should pass upstream changes through and set sync id.
        if (useV2Fields) {
            val metas = destinationOutput.map { getMeta(it) }
            val syncIdsAllValid = metas.map { it["sync_id"].asLong() }.all { it == 100L }
            Assertions.assertTrue(syncIdsAllValid)

            val changes = metas[2]["changes"].elements().asSequence().toList()
            Assertions.assertEquals(changes.size, 1)
            Assertions.assertEquals(changes[0]["field"].asText(), "name")
            Assertions.assertEquals(
                changes[0]["change"].asText(),
                AirbyteRecordMessageMetaChange.Change.TRUNCATED.value()
            )
            Assertions.assertEquals(
                changes[0]["reason"].asText(),
                AirbyteRecordMessageMetaChange.Reason.SOURCE_FIELD_SIZE_LIMITATION.value()
            )
        }

        // Specifically verify that bad fields were captures for supporting formats
        // (ie, Avro and Parquet)
        if (supportsChangeCapture) {
            // Expect the second message id field to have been nulled due to type conversion error.
            val badRow = destinationOutput[1]
            val data = getData(badRow)

            Assertions.assertTrue(data["id"] == null || data["id"].isNull)
            val changes = getMeta(badRow)["changes"].elements().asSequence().toList()

            Assertions.assertEquals(1, changes.size)
            Assertions.assertEquals("id", changes[0]["field"].asText())
            Assertions.assertEquals(
                AirbyteRecordMessageMetaChange.Change.NULLED.value(),
                changes[0]["change"].asText()
            )
            Assertions.assertEquals(
                AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR.value(),
                changes[0]["reason"].asText()
            )

            // Expect the third message to have added a new change to an old one
            val badRowWithPreviousChange = destinationOutput[3]
            val dataWithPreviousChange = getData(badRowWithPreviousChange)
            Assertions.assertTrue(
                dataWithPreviousChange["id"] == null || dataWithPreviousChange["id"].isNull
            )
            val twoChanges =
                getMeta(badRowWithPreviousChange)["changes"].elements().asSequence().toList()
            Assertions.assertEquals(2, twoChanges.size)
        }
    }

    private fun toTimeTypeMap(
        schemaMap: Map<String, JsonNode>,
        format: String
    ): Map<String, Map<String, Boolean>> {
        return schemaMap.mapValues { schema ->
            schema.value["properties"]
                .fields()
                .asSequence()
                .filter { (_, value) -> value["format"]?.asText() == format }
                .map { (key, value) ->
                    val hasTimeZone =
                        !(value.has("airbyte_type") &&
                                value["airbyte_type"]!!.asText().endsWith("without_timezone"))
                    key to hasTimeZone
                }
                .toMap()
        }
    }

    @Test
    open fun testAirbyteTimeTypes() {
        val configuredCatalog =
            Jsons.deserialize(
                MoreResources.readResource("v0/every_time_type_configured_catalog.json"),
                ConfiguredAirbyteCatalog::class.java
            )
        val config = getConfig()
        val messages =
            MoreResources.readResource("v0/every_time_type_messages.txt").trim().lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }

        val expectedByStream =
            messages.filter { it.type == AirbyteMessage.Type.RECORD }.groupBy { it.record.stream }
        val schemasByStreamName =
            configuredCatalog.streams
                .associateBy { it.stream.name }
                .mapValues { it.value.stream.jsonSchema }
        val dateFieldMeta = toTimeTypeMap(schemasByStreamName, "date")
        val datetimeFieldMeta = toTimeTypeMap(schemasByStreamName, "date-time")
        val timeFieldMeta = toTimeTypeMap(schemasByStreamName, "time")

        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false)
        for (stream in configuredCatalog.streams) {
            val name = stream.stream.name
            val schema = stream.stream.jsonSchema
            val records =
                retrieveRecordsDataOnly(
                    testEnv,
                    stream.stream.name,
                    getDefaultSchema(config)!!, /* ignored */
                    schema
                )
            val actual = records.map { node -> pruneAndMaybeFlatten(node) }
            val expected =
                expectedByStream[stream.stream.name]!!.map {
                    if (expectNumericTimestamps) {
                        val node = MoreMappers.initMapper().createObjectNode()
                        it.record.data.fields().forEach { (k, v) ->
                            if (dateFieldMeta[name]!!.containsKey(k)) {
                                val daysSinceEpoch = LocalDate.parse(v.asText()).toEpochDay()
                                node.put(k, daysSinceEpoch.toInt())
                            } else if (datetimeFieldMeta[name]!!.containsKey(k)) {
                                val hasTimeZone = datetimeFieldMeta[name]!![k]!!
                                val millisSinceEpoch =
                                    if (hasTimeZone) {
                                        Instant.parse(v.asText()).toEpochMilli() * 1000L
                                    } else {
                                        LocalDateTime.parse(v.asText())
                                            .toInstant(ZoneOffset.UTC)
                                            .toEpochMilli() * 1000L
                                    }
                                node.put(k, millisSinceEpoch)
                            } else if (timeFieldMeta[name]!!.containsKey(k)) {
                                val hasTimeZone = timeFieldMeta[name]!![k]!!
                                val timeOfDayMicros =
                                    if (hasTimeZone) {
                                        val offsetTime = OffsetTime.parse(v.asText())
                                        val microsLocal =
                                            offsetTime.toLocalTime().toNanoOfDay() / 1000L
                                        val microsUTC =
                                            microsLocal -
                                                    offsetTime.offset.totalSeconds * 1_000_000L
                                        if (microsUTC < 0) {
                                            microsUTC + 24L * 60L * 60L * 1_000_000L
                                        } else {
                                            microsUTC
                                        }
                                    } else {
                                        LocalTime.parse(v.asText()).toNanoOfDay() / 1000L
                                    }
                                node.put(k, timeOfDayMicros)
                            } else {
                                node.set(k, v)
                            }
                        }
                        node
                    } else {
                        it.record.data
                    }
                }

            Assertions.assertEquals(expected, actual)
        }
    }

    @Test
    fun testProblematicTypes() {
        // Kind of a hack, since we'd prefer to test this not happen on some destinations,
        // but verifiying that for CSV is painful.
        Assumptions.assumeTrue(
            expectSchemalessObjectsCoercedToStrings || expectUnionsPromotedToDisjointRecords
        )

        // Run the sync
        val configuredCatalog =
            Jsons.deserialize(
                MoreResources.readResource("v0/problematic_types_configured_catalog.json"),
                ConfiguredAirbyteCatalog::class.java
            )
        val config = getConfig()
        val messagesIn =
            MoreResources.readResource("v0/problematic_types_messages_in.txt").trim().lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }

        runSyncAndVerifyStateOutput(config, messagesIn, configuredCatalog, false)

        // Collect destination data, using the correct transformed schema
        val destinationSchemaStr =
            if (!expectUnionsPromotedToDisjointRecords) {
                MoreResources.readResource("v0/problematic_types_coerced_schemaless_schema.json")
            } else {
                MoreResources.readResource("v0/problematic_types_disjoint_union_schema.json")
            }
        val destinationSchema = Jsons.deserialize(destinationSchemaStr, JsonNode::class.java)
        val actual =
            retrieveRecordsDataOnly(
                testEnv,
                "problematic_types",
                getDefaultSchema(config)!!,
                destinationSchema
            )

        // Validate data
        val expectedMessages =
            if (!expectUnionsPromotedToDisjointRecords) {
                MoreResources.readResource(
                    "v0/problematic_types_coerced_schemaless_messages_out.txt"
                )
            } else { // expectSchemalessObjectsCoercedToStrings
                MoreResources.readResource(
                    "v0/problematic_types_disjoint_union_messages_out.txt"
                )
            }
                .trim()
                .lines()
                .map { Jsons.deserialize(it, JsonNode::class.java) }
        actual.forEachIndexed { i, record: JsonNode ->
            Assertions.assertEquals(expectedMessages[i], record, "Record $i")
        }
    }


    /**
     * Tests that we are able to read over special characters properly when processing line breaks
     * in destinations.
     */
    @Test
    @Throws(Exception::class)
    open fun testLineBreakCharacters() {
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
        configuredCatalog.streams.forEach {
            it.withSyncId(42).withGenerationId(12).withMinimumGenerationId(12)
        }
        val config = getConfig()

        val secondSyncMessages: List<AirbyteMessage> =
            Lists.newArrayList(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
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
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withData(Jsons.jsonNode(ImmutableMap.of("checkpoint", 2)))
                    ),
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.TRACE)
                    .withTrace(
                        AirbyteTraceMessage()
                            .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                            .withStreamStatus(
                                AirbyteStreamStatusTraceMessage()
                                    .withStreamDescriptor(
                                        StreamDescriptor().withName(catalog.streams[0].name)
                                    )
                                    .withStatus(
                                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE
                                    )
                            )
                    )
            )

        runSyncAndVerifyStateOutput(config, secondSyncMessages, configuredCatalog, false)
        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(catalog, secondSyncMessages, defaultSchema)
    }

    private fun pruneAndMaybeFlatten(node: JsonNode): JsonNode {
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

    private fun retrieveRecordsDataOnly(
        testEnv: TestDestinationEnv?,
        streamName: String,
        namespace: String,
        streamSchema: JsonNode
    ): List<JsonNode> {
        return retrieveRecords(testEnv, streamName, namespace, streamSchema)
            .map(this::pruneAndMaybeFlatten)
    }

    @Throws(Exception::class)
    override protected fun retrieveRawRecordsAndAssertSameMessages(
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

    /**
     * Same as [.pruneMutate], except does a defensive copy and returns a new json node object
     * instead of mutating in place.
     *
     * @param record
     * - record that will be pruned.
     * @return pruned json node.
     */
    override fun safePrune(record: AirbyteRecordMessage): AirbyteRecordMessage {
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

    private fun getData(record: JsonNode): JsonNode {
        if (record.has(JavaBaseConstants.COLUMN_NAME_DATA))
            return record.get(JavaBaseConstants.COLUMN_NAME_DATA)
        return record
    }

    private fun getMeta(record: JsonNode): ObjectNode {
        val meta = record.get(JavaBaseConstants.COLUMN_NAME_AB_META)

        val asString = if (meta.isTextual) meta.asText() else Jsons.serialize(meta)
        val asMeta = Jsons.deserialize(asString)

        return asMeta as ObjectNode
    }
}
