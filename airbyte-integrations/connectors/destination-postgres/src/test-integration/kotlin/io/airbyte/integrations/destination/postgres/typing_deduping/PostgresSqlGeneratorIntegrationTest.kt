/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcSqlGeneratorIntegrationTest
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.executeTypeAndDedupe
import io.airbyte.integrations.destination.postgres.*
import java.util.List
import java.util.Optional
import org.jooq.DataType
import org.jooq.Field
import org.jooq.SQLDialect
import org.jooq.conf.ParamType
import org.jooq.impl.DSL
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock

class PostgresSqlGeneratorIntegrationTest : JdbcSqlGeneratorIntegrationTest<PostgresState>() {
    override val supportsSafeCast: Boolean
        get() = true

    override val database: JdbcDatabase
        get() = Companion.database!!

    override val structType: DataType<*>
        get() = PostgresSqlGenerator.JSONB_TYPE

    override val sqlGenerator: JdbcSqlGenerator
        get() =
            PostgresSqlGenerator(
                PostgresSQLNameTransformer(),
                cascadeDrop = false,
                unconstrainedNumber = false
            )

    override val destinationHandler: DestinationHandler<PostgresState>
        get() = PostgresDestinationHandler(databaseName, Companion.database!!, namespace, mock())

    override val sqlDialect: SQLDialect
        get() = SQLDialect.POSTGRES

    override fun toJsonValue(valueAsString: String?): Field<*> {
        return DSL.cast(DSL.`val`(valueAsString), PostgresSqlGenerator.JSONB_TYPE)
    }

    @Test
    @Throws(Exception::class)
    override fun testCreateTableIncremental() {
        val sql = generator.createTable(incrementalDedupStream, "", false)
        destinationHandler.execute(sql)

        val initialStatuses = destinationHandler.gatherInitialState(List.of(incrementalDedupStream))
        Assertions.assertEquals(1, initialStatuses.size)
        val initialStatus = initialStatuses.first()
        Assertions.assertTrue(initialStatus.isFinalTablePresent)
        Assertions.assertFalse(initialStatus.isSchemaMismatch)
    }

    /** Verify that we correctly DROP...CASCADE the final table when cascadeDrop is enabled. */
    @Test
    @Throws(Exception::class)
    fun testCascadeDrop() {
        // Explicitly create a sqlgenerator with cascadeDrop=true
        val generator =
            PostgresSqlGenerator(
                PostgresSQLNameTransformer(),
                cascadeDrop = true,
                unconstrainedNumber = false
            )
        // Create a table, then create a view referencing it
        destinationHandler.execute(generator.createTable(incrementalAppendStream, "", false))
        Companion.database!!.execute(
            DSL.createView(
                    DSL.quotedName(incrementalAppendStream.id.finalNamespace, "example_view")
                )
                .`as`(
                    DSL.select()
                        .from(
                            DSL.quotedName(
                                incrementalAppendStream.id.finalNamespace,
                                incrementalAppendStream.id.finalName
                            )
                        )
                )
                .getSQL(ParamType.INLINED)
        )
        // Create a "soft reset" table
        destinationHandler.execute(
            generator.createTable(incrementalDedupStream, "_soft_reset", false)
        )

        // Overwriting the first table with the second table should succeed.
        Assertions.assertDoesNotThrow {
            destinationHandler.execute(
                generator.overwriteFinalTable(incrementalDedupStream.id, "_soft_reset")
            )
        }
    }

    /**
     * Verify that when cascadeDrop is disabled, an error caused by dropping a table with
     * dependencies results in a configuration error with the correct message.
     */
    @Test
    @Throws(Exception::class)
    fun testCascadeDropDisabled() {
        // Create a sql generator with cascadeDrop=false (this simulates what the framework passes
        // from the
        // config).
        val generator =
            PostgresSqlGenerator(
                PostgresSQLNameTransformer(),
                cascadeDrop = false,
                unconstrainedNumber = false
            )

        // Create a table in the test namespace with a default name.
        destinationHandler.execute(generator.createTable(incrementalAppendStream, "", false))

        // Create a view in the test namespace that selects from the test table.
        // (Ie, emulate a client action that creates some dependency on the table.)
        Companion.database!!.execute(
            DSL.createView(
                    DSL.quotedName(incrementalAppendStream.id.finalNamespace, "example_view")
                )
                .`as`(
                    DSL.select()
                        .from(
                            DSL.quotedName(
                                incrementalAppendStream.id.finalNamespace,
                                incrementalAppendStream.id.finalName
                            )
                        )
                )
                .getSQL(ParamType.INLINED)
        )

        // Simulate a staging table with an arbitrary suffix.
        destinationHandler.execute(
            generator.createTable(incrementalDedupStream, "_soft_reset", false)
        )

        // `overwriteFinalTable` drops the "original" table (without the suffix) and swaps in the
        // suffixed table. The first step should fail because of the view dependency.
        // (The generator does not support dropping tables directly.)
        val t: Throwable =
            Assertions.assertThrowsExactly(ConfigErrorException::class.java) {
                destinationHandler.execute(
                    generator.overwriteFinalTable(incrementalDedupStream.id, "_soft_reset")
                )
            }
        Assertions.assertTrue(
            t.message ==
                "Failed to drop table without the CASCADE option. Consider changing the drop_cascade configuration parameter"
        )
    }

    @Test
    fun testUnconstrainedNumber() {
        val generator =
            PostgresSqlGenerator(
                PostgresSQLNameTransformer(),
                cascadeDrop = false,
                unconstrainedNumber = true,
            )

        createRawTable(streamId)
        destinationHandler.execute(generator.createTable(incrementalDedupStream, "", false))
        insertRawTableRecords(
            streamId,
            listOf(
                Jsons.deserialize(
                    """
                        {
                          "_airbyte_raw_id": "7e1fac0c-017e-4ad6-bc78-334a34d64fce",
                          "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                          "_airbyte_data": {
                            "id1": 6,
                            "id2": 100,
                            "updated_at": "2023-01-01T01:00:00Z",
                            "number": 10325.876543219876543
                          }
                        }
                    """.trimIndent()
                )
            )
        )

        executeTypeAndDedupe(
            generator,
            destinationHandler,
            incrementalDedupStream,
            Optional.empty(),
            ""
        )

        DIFFER.diffFinalTableRecords(
            listOf(
                Jsons.deserialize(
                    """
                        {
                          "_airbyte_raw_id": "7e1fac0c-017e-4ad6-bc78-334a34d64fce",
                          "_airbyte_extracted_at": "2023-01-01T00:00:00.000000Z",
                          "_airbyte_meta": {"changes":[],"sync_id":null},
                          "id1": 6,
                          "id2": 100,
                          "updated_at": "2023-01-01T01:00:00.000000Z",
                          "number": 10325.876543219876543
                        }
                    """.trimIndent()
                )
            ),
            dumpFinalTableRecords(streamId, ""),
        )
    }

    companion object {
        private var testContainer: PostgresTestDatabase? = null
        private var databaseName: String? = null
        private var database: JdbcDatabase? = null

        @JvmStatic
        @BeforeAll
        fun setupPostgres(): Unit {
            testContainer = PostgresTestDatabase.`in`(PostgresTestDatabase.BaseImage.POSTGRES_13)
            val config: JsonNode =
                testContainer!!
                    .configBuilder()
                    .with("schema", "public")
                    .withDatabase()
                    .withHostAndPort()
                    .withCredentials()
                    .withoutSsl()
                    .build()

            databaseName = config.get(JdbcUtils.DATABASE_KEY).asText()
            val postgresDestination = PostgresDestination()
            val dataSource = postgresDestination.getDataSource(config)
            database = DefaultJdbcDatabase(dataSource, PostgresSourceOperations())
        }

        @JvmStatic
        @AfterAll
        fun teardownPostgres(): Unit {
            testContainer!!.close()
        }
    }
}
