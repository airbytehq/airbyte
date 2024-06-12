/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Assertions.assertAll
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.invocation.InvocationOnMock
import org.mockito.kotlin.any
import org.mockito.kotlin.whenever

internal class CatalogParserTest {
    private lateinit var sqlGenerator: SqlGenerator
    private lateinit var parser: CatalogParser

    @BeforeEach
    fun setup() {
        sqlGenerator = Mockito.mock(SqlGenerator::class.java)
        // noop quoting logic
        Mockito.`when`(sqlGenerator.buildColumnId(any(), any())).thenAnswer {
            invocation: InvocationOnMock ->
            val fieldName = invocation.getArgument<String>(0)
            val suffix = invocation.getArgument<String>(1)
            ColumnId(fieldName + suffix, fieldName + suffix, fieldName + suffix)
        }
        Mockito.`when`(sqlGenerator.buildColumnId(any())).thenAnswer { invocation: InvocationOnMock
            ->
            sqlGenerator.buildColumnId(invocation.getArgument<String>(0), "")
        }
        Mockito.`when`(sqlGenerator.buildStreamId(any(), any(), any())).thenAnswer {
            invocation: InvocationOnMock ->
            val namespace = invocation.getArgument<String>(0)
            val name = invocation.getArgument<String>(1)
            val rawNamespace = invocation.getArgument<String>(1)
            StreamId(namespace, name, rawNamespace, namespace + "_abab_" + name, namespace, name)
        }

        parser = CatalogParser(sqlGenerator, "default_namespace")
    }

    /**
     * Both these streams will write to the same final table name ("foofoo"). Verify that they don't
     * actually use the same tablename.
     */
    @Test
    fun finalNameCollision() {
        Mockito.`when`(sqlGenerator.buildStreamId(any(), any(), any())).thenAnswer {
            invocation: InvocationOnMock ->
            val originalNamespace = invocation.getArgument<String>(0)
            val originalName = (invocation.getArgument<String>(1))
            val originalRawNamespace = (invocation.getArgument<String>(2))

            // emulate quoting logic that causes a name collision
            val quotedName = originalName.replace("bar".toRegex(), "")
            StreamId(
                originalNamespace,
                quotedName,
                originalRawNamespace,
                originalNamespace + "_abab_" + quotedName,
                originalNamespace,
                originalName
            )
        }
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(listOf(stream("a", "foobarfoo"), stream("a", "foofoo")))

        val parsedCatalog = parser.parseCatalog(catalog)

        assertAll(
            {
                Assertions.assertEquals(
                    StreamId("a", "foofoo", "airbyte_internal", "a_abab_foofoo", "a", "foobarfoo"),
                    parsedCatalog.streams[0].id,
                )
            },
            {
                Assertions.assertEquals(
                    StreamId(
                        "a",
                        "foofoo_3fd",
                        "airbyte_internal",
                        "a_abab_foofoo_3fd",
                        "a",
                        "foofoo"
                    ),
                    parsedCatalog.streams[1].id,
                )
            },
        )
    }

    /**
     * The schema contains two fields, which will both end up named "foofoo" after quoting. Verify
     * that they don't actually use the same column name.
     */
    @Test
    fun columnNameCollision() {
        Mockito.`when`(sqlGenerator.buildColumnId(any(), any())).thenAnswer {
            invocation: InvocationOnMock ->
            val originalName = invocation.getArgument<String>(0) + invocation.getArgument<String>(1)
            // emulate quoting logic that causes a name collision
            val quotedName = originalName.replace("bar".toRegex(), "")
            ColumnId(quotedName, originalName, quotedName)
        }
        val schema =
            Jsons.deserialize(
                """
                                              {
                                                "type": "object",
                                                "properties": {
                                                  "foobarfoo": {"type": "string"},
                                                  "foofoo": {"type": "string"}
                                                }
                                              }
                                              
                                              """.trimIndent()
            )
        val catalog = ConfiguredAirbyteCatalog().withStreams(listOf(stream("a", "a", schema)))

        val parsedCatalog = parser.parseCatalog(catalog)
        val columnsList = parsedCatalog.streams[0].columns.keys.toList()

        assertAll(
            { Assertions.assertEquals(2, parsedCatalog.streams[0].columns.size) },
            { Assertions.assertEquals("foofoo", columnsList[0].name) },
            { Assertions.assertEquals("foofoo_1", columnsList[1].name) }
        )
    }

    /**
     * Test behavior when the sqlgenerator truncates column names. We should end generate new names
     * that still avoid collision.
     */
    @Test
    fun truncatingColumnNameCollision() {
        whenever(sqlGenerator.buildColumnId(any(), any())).thenAnswer { invocation: InvocationOnMock
            ->
            val originalName = invocation.getArgument<String>(0) + invocation.getArgument<String>(1)
            // truncate to 10 characters
            val truncatedName = originalName.substring(0, 10.coerceAtMost(originalName.length))
            ColumnId(truncatedName, originalName, truncatedName)
        }
        val schema =
            Jsons.deserialize(
                """
                                              {
                                                "type": "object",
                                                "properties": {
                                                  "aVeryLongColumnName": {"type": "string"},
                                                  "aVeryLongColumnNameWithMoreTextAfterward": {"type": "string"}
                                                }
                                              }
                                              
                                              """.trimIndent()
            )
        val catalog = ConfiguredAirbyteCatalog().withStreams(listOf(stream("a", "a", schema)))

        val parsedCatalog = parser.parseCatalog(catalog)
        val columnsList = parsedCatalog.streams[0].columns.keys.toList()

        assertAll(
            { Assertions.assertEquals(2, parsedCatalog.streams[0].columns.size) },
            { Assertions.assertEquals("aVeryLongC", columnsList[0].name) },
            { Assertions.assertEquals("aV36rd", columnsList[1].name) }
        )
    }

    @Test
    fun testDefaultNamespace() {
        val catalog =
            parser.parseCatalog(
                ConfiguredAirbyteCatalog()
                    .withStreams(
                        listOf(stream(null, "a", Jsons.deserialize("""{"type": "object"}""")))
                    )
            )

        Assertions.assertEquals("default_namespace", catalog.streams[0].id.originalNamespace)
    }

    companion object {
        private fun stream(
            namespace: String?,
            name: String,
            schema: JsonNode =
                Jsons.deserialize(
                    """
                          {
                            "type": "object",
                            "properties": {
                              "name": {"type": "string"}
                            }
                          }
                          
                          """.trimIndent()
                )
        ): ConfiguredAirbyteStream {
            return ConfiguredAirbyteStream()
                .withStream(
                    AirbyteStream().withNamespace(namespace).withName(name).withJsonSchema(schema)
                )
                .withSyncMode(SyncMode.INCREMENTAL)
                .withDestinationSyncMode(DestinationSyncMode.APPEND)
                .withGenerationId(0)
                .withMinimumGenerationId(0)
                .withSyncId(0)
        }
    }
}
