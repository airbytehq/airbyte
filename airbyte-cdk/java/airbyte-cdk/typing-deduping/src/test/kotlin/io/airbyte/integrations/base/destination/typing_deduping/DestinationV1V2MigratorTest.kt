/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.protocol.models.v0.DestinationSyncMode
import java.util.*
import java.util.stream.Stream
import lombok.SneakyThrows
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider
import org.junit.jupiter.params.provider.ArgumentsSource
import org.mockito.Mockito
import org.mockito.Mockito.mock
import org.mockito.kotlin.any
import org.mockito.kotlin.spy

class DestinationV1V2MigratorTest {
    class ShouldMigrateTestArgumentProvider : ArgumentsProvider {
        @Throws(Exception::class)
        override fun provideArguments(context: ExtensionContext): Stream<out Arguments> {
            // Don't throw an exception

            val v2SchemaMatches = true

            return Stream.of( // Doesn't Migrate because of sync mode
                Arguments.of(
                    DestinationSyncMode.OVERWRITE,
                    makeMockMigrator(true, false, v2SchemaMatches, true, true),
                    false
                ), // Doesn't migrate because v2 table already exists
                Arguments.of(
                    DestinationSyncMode.APPEND,
                    makeMockMigrator(true, true, v2SchemaMatches, true, true),
                    false
                ),
                Arguments.of(
                    DestinationSyncMode.APPEND_DEDUP,
                    makeMockMigrator(true, true, v2SchemaMatches, true, true),
                    false
                ), // Doesn't migrate because no valid v1 raw table exists
                Arguments.of(
                    DestinationSyncMode.APPEND,
                    makeMockMigrator(true, false, v2SchemaMatches, false, true),
                    false
                ),
                Arguments.of(
                    DestinationSyncMode.APPEND_DEDUP,
                    makeMockMigrator(true, false, v2SchemaMatches, false, true),
                    false
                ),
                Arguments.of(
                    DestinationSyncMode.APPEND,
                    makeMockMigrator(true, false, v2SchemaMatches, true, false),
                    false
                ),
                Arguments.of(
                    DestinationSyncMode.APPEND_DEDUP,
                    makeMockMigrator(true, false, v2SchemaMatches, true, false),
                    false
                ), // Migrates
                Arguments.of(DestinationSyncMode.APPEND, noIssuesMigrator(), true),
                Arguments.of(DestinationSyncMode.APPEND_DEDUP, noIssuesMigrator(), true)
            )
        }
    }

    @ParameterizedTest
    @ArgumentsSource(ShouldMigrateTestArgumentProvider::class)
    @Throws(Exception::class)
    fun testShouldMigrate(
        destinationSyncMode: DestinationSyncMode,
        migrator: BaseDestinationV1V2Migrator<*>,
        expected: Boolean
    ) {
        val config = StreamConfig(STREAM_ID, null, destinationSyncMode, null, null, null)
        val actual = migrator.shouldMigrate(config)
        Assertions.assertEquals(expected, actual)
    }

    @Test
    @Throws(Exception::class)
    fun testMismatchedSchemaThrowsException() {
        val config =
            StreamConfig(STREAM_ID, null, DestinationSyncMode.APPEND_DEDUP, null, null, null)
        val migrator = makeMockMigrator(true, true, false, false, false)
        val exception =
            Assertions.assertThrows(UnexpectedSchemaException::class.java) {
                migrator.shouldMigrate(config)
            }
        Assertions.assertEquals(
            "Destination V2 Raw Table does not match expected Schema",
            exception.message
        )
    }

    @SneakyThrows
    @Test
    @Throws(Exception::class)
    fun testMigrate() {
        val sqlGenerator = MockSqlGenerator()
        val stream =
            StreamConfig(STREAM_ID, null, DestinationSyncMode.APPEND_DEDUP, null, null, null)
        val handler = Mockito.mock(DestinationHandler::class.java)
        val sql = sqlGenerator.migrateFromV1toV2(STREAM_ID, "v1_raw_namespace", "v1_raw_table")
        // All is well
        val migrator = noIssuesMigrator()
        migrator.migrate(sqlGenerator, handler, stream)
        Mockito.verify(handler).execute(sql)
        // Exception thrown when executing sql, TableNotMigratedException thrown
        Mockito.doThrow(Exception::class.java).`when`(handler).execute(any())
        val exception =
            Assertions.assertThrows(TableNotMigratedException::class.java) {
                migrator.migrate(sqlGenerator, handler, stream)
            }
        Assertions.assertEquals(
            "Attempted and failed to migrate stream final_table",
            exception.message
        )
    }

    companion object {
        private val STREAM_ID = StreamId("final", "final_table", "raw", "raw_table", null, null)

        @Throws(Exception::class)
        fun makeMockMigrator(
            v2NamespaceExists: Boolean,
            v2TableExists: Boolean,
            v2RawSchemaMatches: Boolean,
            v1RawTableExists: Boolean,
            v1RawTableSchemaMatches: Boolean
        ): BaseDestinationV1V2Migrator<*> {
            val migrator: BaseDestinationV1V2Migrator<String> = spy()
            Mockito.`when`(migrator.doesAirbyteInternalNamespaceExist(any()))
                .thenReturn(v2NamespaceExists)
            val existingTable =
                if (v2TableExists) Optional.of("v2_raw") else Optional.empty<String>()
            Mockito.`when`(migrator.getTableIfExists("raw", "raw_table")).thenReturn(existingTable)
            Mockito.`when`<Boolean>(
                    migrator.schemaMatchesExpectation(
                        "v2_raw",
                        JavaBaseConstants.V2_RAW_TABLE_COLUMN_NAMES
                    )
                )
                .thenReturn(false)
            Mockito.`when`<Boolean>(
                    migrator.schemaMatchesExpectation(
                        "v2_raw",
                        JavaBaseConstants.V2_RAW_TABLE_COLUMN_NAMES_WITHOUT_META
                    )
                )
                .thenReturn(v2RawSchemaMatches)

            Mockito.`when`(migrator.convertToV1RawName(any()))
                .thenReturn(NamespacedTableName("v1_raw_namespace", "v1_raw_table"))
            val existingV1RawTable =
                if (v1RawTableExists) Optional.of("v1_raw") else Optional.empty<String>()
            Mockito.`when`(migrator.getTableIfExists("v1_raw_namespace", "v1_raw_table"))
                .thenReturn(existingV1RawTable)
            Mockito.`when`<Boolean>(
                    migrator.schemaMatchesExpectation(
                        "v1_raw",
                        JavaBaseConstants.LEGACY_RAW_TABLE_COLUMNS
                    )
                )
                .thenReturn(v1RawTableSchemaMatches)
            return migrator
        }

        @Throws(Exception::class)
        fun noIssuesMigrator(): BaseDestinationV1V2Migrator<*> {
            return makeMockMigrator(
                v2NamespaceExists = true,
                v2TableExists = false,
                v2RawSchemaMatches = true,
                v1RawTableExists = true,
                v1RawTableSchemaMatches = true
            )
        }
    }
}
