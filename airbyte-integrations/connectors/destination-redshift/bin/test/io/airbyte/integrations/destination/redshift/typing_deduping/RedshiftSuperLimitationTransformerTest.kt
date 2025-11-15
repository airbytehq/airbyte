/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons.deserializeExact
import io.airbyte.commons.json.Jsons.jsonNode
import io.airbyte.commons.json.Jsons.serialize
import io.airbyte.commons.resources.MoreResources.readResource
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.ImportType
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.redshift.RedshiftSQLNameTransformer
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.io.IOException
import java.nio.charset.StandardCharsets
import java.util.Optional
import java.util.UUID
import java.util.stream.IntStream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class RedshiftSuperLimitationTransformerTest {
    private var transformer: RedshiftSuperLimitationTransformer? = null
    @BeforeEach
    fun setup() {
        val column1 = redshiftSqlGenerator.buildColumnId("column1")
        val column2 = redshiftSqlGenerator.buildColumnId("column2")
        val primaryKey = listOf(column1, column2)
        val columns = LinkedHashMap<ColumnId, AirbyteType>()
        // Generate columnIds from 3 to 1024 and add to columns map
        IntStream.range(3, 1025).forEach { i: Int ->
            columns[redshiftSqlGenerator.buildColumnId("column$i")] = AirbyteProtocolType.STRING
        }

        val streamId =
            StreamId(
                "test_schema",
                "users_final",
                "test_schema",
                "users_raw",
                "test_schema",
                "users_final"
            )
        val streamConfig =
            StreamConfig(
                streamId,
                ImportType.DEDUPE,
                primaryKey,
                Optional.empty(),
                columns,
                0,
                0,
                0
            )
        val parsedCatalog = ParsedCatalog(listOf(streamConfig))
        transformer = RedshiftSuperLimitationTransformer(parsedCatalog, "test_schema")
    }

    @Test
    @Throws(IOException::class)
    fun testVarcharNulling() {
        val jsonString = readResource("test.json")
        val jsonNode = deserializeExact(jsonString)
        // Calculate the size of the json before transformation, note that the original JsonNode is
        // altered
        // so
        // serializing after transformation will return modified size.
        val jacksonDeserializationSize =
            serialize(jsonNode).toByteArray(StandardCharsets.UTF_8).size
        // Add a short length as predicate.
        val transformationInfo =
            transformer!!.transformNodes(jsonNode) { text: String -> text.length > 10 }
        // Calculate the size of the json after transformation
        val jacksonDeserializeSizeAfterTransform =
            serialize(jsonNode).toByteArray(StandardCharsets.UTF_8).size
        Assertions.assertEquals(jacksonDeserializationSize, transformationInfo.originalBytes)
        Assertions.assertEquals(
            jacksonDeserializeSizeAfterTransform,
            transformationInfo.originalBytes - transformationInfo.removedBytes
        )
        println(transformationInfo.meta)
        println(serialize(jsonNode))
    }

    @Test
    @Throws(IOException::class)
    fun testRedshiftSuperLimit_ShouldRemovePartialRecord() {
        // We generate 1020 16Kb strings and 1 64Kb string + 2 uuids.
        // Removing the 64kb will make it fall below the 16MB limit & offending varchar removed too.
        val testData: MutableMap<String, String> = HashMap()
        testData["column1"] = UUID.randomUUID().toString()
        testData["column2"] = UUID.randomUUID().toString()
        testData["column3"] = getLargeString(64)
        // Add 16Kb strings from column 3 to 1024 in testData
        IntStream.range(4, 1025).forEach { i: Int -> testData["column$i"] = getLargeString(16) }

        val upstreamMeta =
            AirbyteRecordMessageMeta()
                .withChanges(
                    listOf(
                        AirbyteRecordMessageMetaChange()
                            .withField("upstream_field")
                            .withChange(AirbyteRecordMessageMetaChange.Change.NULLED)
                            .withReason(
                                AirbyteRecordMessageMetaChange.Reason.PLATFORM_SERIALIZATION_ERROR
                            )
                    )
                )
        val transformed: Pair<JsonNode?, AirbyteRecordMessageMeta?> =
            transformer!!.transform(
                StreamDescriptor().withNamespace("test_schema").withName("users_final"),
                jsonNode<Map<String, String>>(testData),
                upstreamMeta
            )
        Assertions.assertTrue(
            serialize(transformed.first!!).toByteArray(StandardCharsets.UTF_8).size <
                RedshiftSuperLimitationTransformer.REDSHIFT_SUPER_MAX_BYTE_SIZE
        )
        Assertions.assertEquals(2, transformed.second!!.changes.size)
        // Assert that transformation added the change
        Assertions.assertEquals("$.column3", transformed.second!!.changes.first().field)
        Assertions.assertEquals(
            AirbyteRecordMessageMetaChange.Change.NULLED,
            transformed.second!!.changes.first().change
        )
        Assertions.assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            transformed.second!!.changes.first().reason
        )
        // Assert that upstream changes are preserved (appended last)
        Assertions.assertEquals("upstream_field", transformed.second!!.changes.last().field)
    }

    @Test
    fun testRedshiftSuperLimit_ShouldRemoveWholeRecord() {
        val testData: MutableMap<String, String> = HashMap()
        // Add 16Kb strings from column 1 to 1024 in testData where total > 16MB
        IntStream.range(1, 1025).forEach { i: Int -> testData["column$i"] = getLargeString(16) }

        val upstreamMeta =
            AirbyteRecordMessageMeta()
                .withChanges(
                    listOf(
                        AirbyteRecordMessageMetaChange()
                            .withField("upstream_field")
                            .withChange(AirbyteRecordMessageMetaChange.Change.NULLED)
                            .withReason(
                                AirbyteRecordMessageMetaChange.Reason.PLATFORM_SERIALIZATION_ERROR
                            )
                    )
                )
        val transformed =
            transformer!!.transform(
                StreamDescriptor().withNamespace("test_schema").withName("users_final"),
                jsonNode<Map<String, String>>(testData),
                upstreamMeta
            )
        // Verify PKs are preserved.
        Assertions.assertNotNull(transformed.first!!["column1"])
        Assertions.assertNotNull(transformed.first!!["column1"])
        Assertions.assertTrue(
            serialize<AirbyteRecordMessageMeta>(transformed.second!!)
                .toByteArray(StandardCharsets.UTF_8)
                .size < RedshiftSuperLimitationTransformer.REDSHIFT_SUPER_MAX_BYTE_SIZE
        )
        Assertions.assertEquals(2, transformed.second!!.changes.size)
        // Assert that transformation added the change
        Assertions.assertEquals("all", transformed.second!!.changes.first().field)
        Assertions.assertEquals(
            AirbyteRecordMessageMetaChange.Change.NULLED,
            transformed.second!!.changes.first().change
        )
        Assertions.assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_RECORD_SIZE_LIMITATION,
            transformed.second!!.changes.first().reason
        )
        // Assert that upstream changes are preserved (appended last)
        Assertions.assertEquals("upstream_field", transformed.second!!.changes.last().field)
    }

    @Test
    fun testRedshiftSuperLimit_ShouldFailOnPKMissing() {
        val testData: MutableMap<String, String> = HashMap()
        // Add 16Kb strings from column 3 to 1027 in testData, 1 & 2 are pks missing
        IntStream.range(3, 1028).forEach { i: Int -> testData["column$i"] = getLargeString(16) }

        val upstreamMeta =
            AirbyteRecordMessageMeta()
                .withChanges(
                    listOf(
                        AirbyteRecordMessageMetaChange()
                            .withField("upstream_field")
                            .withChange(AirbyteRecordMessageMetaChange.Change.NULLED)
                            .withReason(
                                AirbyteRecordMessageMetaChange.Reason.PLATFORM_SERIALIZATION_ERROR
                            )
                    )
                )
        val ex: Exception =
            Assertions.assertThrows(RuntimeException::class.java) {
                transformer!!.transform(
                    StreamDescriptor().withNamespace("test_schema").withName("users_final"),
                    jsonNode<Map<String, String>>(testData),
                    upstreamMeta
                )
            }

        Assertions.assertEquals(
            "Record exceeds size limit, cannot transform without PrimaryKeys in DEDUPE sync",
            ex.message
        )
    }

    private fun getLargeString(kbSize: Int): String {
        val longString = StringBuilder()
        while (longString.length < 1024 * kbSize) { // Repeat until the given KB size
            longString.append("Lorem ipsum dolor sit amet, consectetur adipiscing elit. ")
        }
        return longString.toString()
    }

    companion object {
        private val redshiftSqlGenerator = RedshiftSqlGenerator(RedshiftSQLNameTransformer(), false)
    }
}
