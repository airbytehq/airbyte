/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import java.util.List
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.invocation.InvocationOnMock
import org.mockito.kotlin.any

internal class CatalogParserTest {
    private lateinit var sqlGenerator: SqlGenerator
    private var parser: CatalogParser? = null

    @BeforeEach
    fun setup() {
        sqlGenerator = Mockito.mock(SqlGenerator::class.java)
        // noop quoting logic
        Mockito.`when`(sqlGenerator.buildColumnId(any())).thenAnswer { invocation: InvocationOnMock
            ->
            val fieldName = invocation.getArgument<String>(0)
            ColumnId(fieldName, fieldName, fieldName)
        }
        Mockito.`when`(sqlGenerator.buildStreamId(any(), any(), any())).thenAnswer {
            invocation: InvocationOnMock ->
            val namespace = invocation.getArgument<String>(0)
            val name = invocation.getArgument<String>(1)
            val rawNamespace = invocation.getArgument<String>(1)
            StreamId(namespace, name, rawNamespace, namespace + "_abab_" + name, namespace, name)
        }

        parser = CatalogParser(sqlGenerator)
    }

    /**
     * Both these streams will write to the same final table name ("foofoo"). Verify that they don't
     * actually use the same tablename.
     */
    @Test
    fun finalNameCollision() {
        Mockito.`when`(sqlGenerator!!.buildStreamId(any(), any(), any())).thenAnswer {
            invocation: InvocationOnMock ->
            val originalNamespace = invocation.getArgument<String>(0)
            val originalName = (invocation.getArgument<String>(1))
            val originalRawNamespace = (invocation.getArgument<String>(1))

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
                .withStreams(List.of(stream("a", "foobarfoo"), stream("a", "foofoo")))

        val parsedCatalog = parser!!.parseCatalog(catalog)

        Assertions.assertNotEquals(
            parsedCatalog.streams.get(0).id.finalName,
            parsedCatalog.streams.get(1).id.finalName
        )
    }

    /**
     * The schema contains two fields, which will both end up named "foofoo" after quoting. Verify
     * that they don't actually use the same column name.
     */
    @Test
    fun columnNameCollision() {
        Mockito.`when`(sqlGenerator!!.buildColumnId(any(), any())).thenAnswer {
            invocation: InvocationOnMock ->
            val originalName = invocation.getArgument<String>(0)
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
        val catalog = ConfiguredAirbyteCatalog().withStreams(List.of(stream("a", "a", schema)))

        val parsedCatalog = parser!!.parseCatalog(catalog)

        Assertions.assertEquals(2, parsedCatalog.streams.get(0).columns!!.size)
    }

    companion object {
        private fun stream(
            namespace: String,
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
        }
    }
}
