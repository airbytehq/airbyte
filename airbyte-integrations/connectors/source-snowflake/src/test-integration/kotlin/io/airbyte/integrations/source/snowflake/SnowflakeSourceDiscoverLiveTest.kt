/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.discover
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.execute
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

class SnowflakeSourceDiscoverLiveTest : AbstractSnowflakeLiveTest() {

    private lateinit var catalog: AirbyteCatalog

    @BeforeAll
    fun discoverOnce() {
        catalog = discover(spec())
    }

    private val seededStreams =
        setOf(
            "TYPE_MATRIX",
            "EMPTY_TABLE",
            "NO_PK",
            "COMPOSITE_PK",
            "PK_TABLE",
            "V_TYPES",
            "INC_NUMBER",
            "INC_TS_NTZ",
            "INC_TS_TZ",
            "INC_TS_LTZ",
            "INC_DATE",
            "INC_VARCHAR",
            "INC_NOPK_NUMBER",
            "SPLIT_100K",
        )

    private val expectedTypeMatrixTypes: Map<String, LeafAirbyteSchemaType> =
        mapOf(
            "ID" to LeafAirbyteSchemaType.NUMBER,
            "C_NUMBER" to LeafAirbyteSchemaType.NUMBER,
            "C_INT" to LeafAirbyteSchemaType.NUMBER,
            "C_BIGINT" to LeafAirbyteSchemaType.NUMBER,
            "C_SMALLINT" to LeafAirbyteSchemaType.NUMBER,
            "C_BYTEINT" to LeafAirbyteSchemaType.NUMBER,
            "C_NUMBER_10_2" to LeafAirbyteSchemaType.NUMBER,
            "C_NUMERIC" to LeafAirbyteSchemaType.NUMBER,
            "C_FLOAT" to LeafAirbyteSchemaType.NUMBER,
            "C_DOUBLE" to LeafAirbyteSchemaType.NUMBER,
            "C_VARCHAR" to LeafAirbyteSchemaType.STRING,
            "C_CHAR" to LeafAirbyteSchemaType.STRING,
            "C_STRING" to LeafAirbyteSchemaType.STRING,
            "C_BINARY" to LeafAirbyteSchemaType.BINARY,
            "C_BOOLEAN" to LeafAirbyteSchemaType.BOOLEAN,
            "C_DATE" to LeafAirbyteSchemaType.DATE,
            "C_TIME" to LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
            "C_TIME3" to LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
            "C_TIMESTAMP_NTZ" to LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
            "C_TIMESTAMP_LTZ" to LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
            "C_TIMESTAMP_TZ" to LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
            "C_VARIANT" to LeafAirbyteSchemaType.STRING,
            "C_OBJECT" to LeafAirbyteSchemaType.STRING,
            "C_ARRAY" to LeafAirbyteSchemaType.STRING,
            "C_GEOGRAPHY" to LeafAirbyteSchemaType.STRING,
            "C_VECTOR" to LeafAirbyteSchemaType.STRING,
        )

    @Test
    fun schemaFilterIsAnExactName() {
        // airbytehq/airbyte#87000, #86998: `_` in the Schema option used to be a LIKE wildcard, so
        // SCHEMA_A also matched SCHEMAXA, took minutes on a large account, and the matched schemas'
        // columns and primary keys came back as duplicates.
        val target = "${schema}_A"
        val decoy = "${schema}XA"
        for (s in listOf(target, decoy)) {
            execute(admin, "CREATE SCHEMA \"$database\".\"$s\"")
            execute(
                admin,
                "CREATE TABLE \"$database\".\"$s\".T (ID INTEGER PRIMARY KEY, V VARCHAR)"
            )
        }
        try {
            val filtered = discover(SnowflakeLiveTestSupport.spec(schema = target))
            assertEquals(listOf("T"), filtered.streams.map { it.name })
            val stream = filtered.streams.single()
            assertEquals(target, stream.namespace)
            assertEquals(listOf(listOf("ID")), stream.sourceDefinedPrimaryKey)
            assertEquals(
                listOf("ID", "V"),
                stream.jsonSchema["properties"].fieldNames().asSequence().sorted().toList(),
            )
        } finally {
            for (s in listOf(target, decoy)) {
                execute(admin, "DROP SCHEMA IF EXISTS \"$database\".\"$s\" CASCADE")
            }
        }
    }

    @Test
    fun catalogShape() {
        val byName = catalog.streams.associateBy { it.name }
        // V_BROKEN (a view over a dropped table) is skipped instead of failing discovery.
        assertEquals(seededStreams, byName.keys)
        catalog.streams.forEach { assertEquals(schema, it.namespace, it.name) }
        assertEquals(listOf(listOf("ID")), byName["PK_TABLE"]!!.sourceDefinedPrimaryKey)
        assertEquals(
            listOf(listOf("A"), listOf("B")),
            byName["COMPOSITE_PK"]!!.sourceDefinedPrimaryKey
        )
        assertTrue(byName["NO_PK"]!!.sourceDefinedPrimaryKey.isEmpty())
        assertTrue(byName["V_TYPES"]!!.sourceDefinedPrimaryKey.isEmpty())
        assertEquals(true, byName["PK_TABLE"]!!.isResumable)
        assertEquals(false, byName["NO_PK"]!!.isResumable)
        assertEquals(false, byName["V_TYPES"]!!.isResumable)
        assertEquals(
            listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
            byName["TYPE_MATRIX"]!!.supportedSyncModes,
        )
        assertEquals(
            setOf("ID", "V"),
            byName["EMPTY_TABLE"]!!.jsonSchema["properties"].fieldNames().asSequence().toSet()
        )
    }

    @Test
    fun typeMatrixJsonSchema() {
        val props = catalog.streams.first { it.name == "TYPE_MATRIX" }.jsonSchema["properties"]
        assertEquals(expectedTypeMatrixTypes.keys, props.fieldNames().asSequence().toSet())
        for ((column, type) in expectedTypeMatrixTypes) {
            assertEquals(type.asJsonSchema(), props[column], column)
        }
    }

    @Test
    fun checkPrivilegesOffOnlyKeepsTheBrokenView() {
        // check_privileges=true takes type names from a LIMIT 0 probe (ResultSetMetaData),
        // check_privileges=false from DatabaseMetaData.getColumns; the types must agree.
        val withoutProbes = discover(spec(checkPrivileges = false))
        val probed = catalog.streams.associateBy { it.name }
        val unprobed = withoutProbes.streams.associateBy { it.name }
        assertEquals(seededStreams + "V_BROKEN", unprobed.keys)
        for (name in seededStreams) {
            assertEquals(probed[name]!!.jsonSchema, unprobed[name]!!.jsonSchema, name)
            assertEquals(
                probed[name]!!.sourceDefinedPrimaryKey,
                unprobed[name]!!.sourceDefinedPrimaryKey,
                name
            )
        }
    }
}
