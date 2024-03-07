/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.components.debezium

import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import java.util.regex.Pattern
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class ConfigBuilderTest {

    @Test
    fun testTopicName() {
        checkTopicName("regularName123", "regularName123")
        checkTopicName("dirty!Name", "dirty_Name")
    }

    private fun checkTopicName(name: String, expected: String) {
        val actual =
            ConfigBuilder()
                .withDebeziumName(name)
                .withTestTargets()
                .build()
                .debeziumProperties["topic.prefix"]
        Assertions.assertEquals(expected, actual)
    }

    @Test
    fun testIncludeList() {
        checkIncludeLists(
            listOf(
                CatalogHelpers.createAirbyteStream(
                    "onecol",
                    "public",
                    Field.of("k", JsonSchemaType.INTEGER)
                )
            ),
            "\\Qpublic.onecol\\E",
            "\\Qpublic.onecol\\E\\.(\\Qk\\E)"
        )
        checkIncludeLists(
            listOf(
                CatalogHelpers.createAirbyteStream(
                    "kv",
                    "public",
                    Field.of("k", JsonSchemaType.INTEGER),
                    Field.of("v", JsonSchemaType.STRING)
                ),
                CatalogHelpers.createAirbyteStream(
                    "eventlog",
                    "public",
                    Field.of("ts", JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE),
                    Field.of("entry", JsonSchemaType.STRING)
                )
            ),
            "\\Qpublic.kv\\E,\\Qpublic.eventlog\\E",
            "\\Qpublic.kv\\E\\.(\\Qv\\E|\\Qk\\E),\\Qpublic.eventlog\\E\\.(\\Qentry\\E|\\Qts\\E)"
        )
        checkIncludeLists(
            listOf(
                CatalogHelpers.createAirbyteStream(
                    "dirty.,$|(",
                    "public",
                    Field.of("dirty.,$", JsonSchemaType.INTEGER)
                )
            ),
            "\\Qpublic.dirty.\\,\$|(\\E",
            "\\Qpublic.dirty.\\,\$|(\\E\\.(\\Qdirty.\\,\$\\E)"
        )
    }

    private fun checkIncludeLists(
        streams: List<AirbyteStream>,
        expectedTableIncludeList: String,
        expectedColumnIncludeList: String
    ) {
        checkInputValidity(expectedTableIncludeList)
        checkInputValidity(expectedColumnIncludeList)
        val configuredCatalog =
            CatalogHelpers.toDefaultConfiguredCatalog(AirbyteCatalog().withStreams(streams))
        configuredCatalog.streams.forEach { s: ConfiguredAirbyteStream ->
            s.syncMode = SyncMode.INCREMENTAL
        }
        val actualConfig =
            RelationalConfigBuilder().withCatalog(configuredCatalog).withTestTargets().build()
        Assertions.assertEquals(
            expectedTableIncludeList,
            actualConfig.debeziumProperties["table.include.list"]
        )
        Assertions.assertEquals(
            expectedColumnIncludeList,
            actualConfig.debeziumProperties["column.include.list"]
        )
    }

    private fun checkInputValidity(expectedIncludeList: String) {
        expectedIncludeList.split(Pattern.compile("(?<!\\\\),")).forEach { Pattern.compile(it) }
    }
}
