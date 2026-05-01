/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.discover

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.h2.H2TestFixture
import io.airbyte.cdk.h2source.H2SourceConfiguration
import io.airbyte.cdk.h2source.H2SourceConfigurationFactory
import io.airbyte.cdk.h2source.H2SourceConfigurationSpecification
import io.airbyte.cdk.h2source.H2SourceOperations
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.sql.JDBCType
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JdbcMetadataQuerierTest {
    val h2 = H2TestFixture()

    init {
        h2.execute("CREATE TABLE kv (k INT PRIMARY KEY, v VARCHAR(60))")
    }

    val factory =
        JdbcMetadataQuerier.Factory(
            selectQueryGenerator = H2SourceOperations(),
            fieldTypeMapper = H2SourceOperations(),
            checkQueries = JdbcCheckQueries(),
            constants = DefaultJdbcConstants(),
        )

    @Test
    fun testEmptyNamespacesDiscoversAllSchemas() {
        h2.execute("CREATE SCHEMA OTHER_SCHEMA")
        h2.execute("CREATE TABLE OTHER_SCHEMA.extra (k INT PRIMARY KEY)")
        val configPojo =
            H2SourceConfigurationSpecification().apply {
                port = h2.port
                database = h2.database
            }
        val baseConfig: H2SourceConfiguration = H2SourceConfigurationFactory().make(configPojo)
        // Bypass the factory default of {"PUBLIC"} to exercise the empty-namespaces path.
        val config: H2SourceConfiguration = baseConfig.copy(namespaces = emptySet())
        factory.session(config).use { mdq: MetadataQuerier ->
            val namespaces: Set<String> = mdq.streamNamespaces().toSet()
            Assertions.assertTrue(
                namespaces.contains("PUBLIC"),
                "expected PUBLIC in discovered namespaces $namespaces",
            )
            Assertions.assertTrue(
                namespaces.contains("OTHER_SCHEMA"),
                "expected OTHER_SCHEMA in discovered namespaces $namespaces",
            )
            val publicStreams: List<String> = mdq.streamNames("PUBLIC").map { it.toString() }
            val otherStreams: List<String> = mdq.streamNames("OTHER_SCHEMA").map { it.toString() }
            Assertions.assertTrue(
                publicStreams.contains("PUBLIC.KV"),
                "expected PUBLIC.KV among $publicStreams",
            )
            Assertions.assertTrue(
                otherStreams.contains("OTHER_SCHEMA.EXTRA"),
                "expected OTHER_SCHEMA.EXTRA among $otherStreams",
            )
            // Columns should have been discovered for tables in both schemas.
            val otherDesc = StreamDescriptor().withNamespace("OTHER_SCHEMA").withName("EXTRA")
            val otherStreamID: StreamIdentifier = StreamIdentifier.from(otherDesc)
            val otherTable = (mdq as JdbcMetadataQuerier).findTableName(otherStreamID)
            Assertions.assertNotNull(otherTable)
            val otherColumns = mdq.columnMetadata(otherTable!!).map { it.name }
            Assertions.assertTrue(
                otherColumns.contains("K"),
                "expected column K on OTHER_SCHEMA.EXTRA, got $otherColumns",
            )
        }
    }

    @Test
    fun testEmptyNamespacesRespectsIgnoredNamespaces() {
        h2.execute("CREATE SCHEMA OTHER_SCHEMA")
        h2.execute("CREATE TABLE OTHER_SCHEMA.extra (k INT PRIMARY KEY)")
        val filteringFactory =
            JdbcMetadataQuerier.Factory(
                selectQueryGenerator = H2SourceOperations(),
                fieldTypeMapper = H2SourceOperations(),
                checkQueries = JdbcCheckQueries(),
                constants = DefaultJdbcConstants(ignoredNamespaces = setOf("OTHER_SCHEMA")),
            )
        val configPojo =
            H2SourceConfigurationSpecification().apply {
                port = h2.port
                database = h2.database
            }
        val baseConfig: H2SourceConfiguration = H2SourceConfigurationFactory().make(configPojo)

        // Auto-discovery path: OTHER_SCHEMA must be filtered out.
        val autoConfig: H2SourceConfiguration = baseConfig.copy(namespaces = emptySet())
        filteringFactory.session(autoConfig).use { mdq: MetadataQuerier ->
            val namespaces: Set<String> = mdq.streamNamespaces().toSet()
            Assertions.assertFalse(
                namespaces.contains("OTHER_SCHEMA"),
                "OTHER_SCHEMA should have been filtered out, got $namespaces",
            )
            Assertions.assertTrue(
                namespaces.contains("PUBLIC"),
                "expected PUBLIC in $namespaces",
            )
        }

        // Explicit-namespace path: naming OTHER_SCHEMA bypasses the filter.
        val explicitConfig: H2SourceConfiguration =
            baseConfig.copy(namespaces = setOf("OTHER_SCHEMA"))
        filteringFactory.session(explicitConfig).use { mdq: MetadataQuerier ->
            val namespaces: Set<String> = mdq.streamNamespaces().toSet()
            Assertions.assertTrue(
                namespaces.contains("OTHER_SCHEMA"),
                "expected OTHER_SCHEMA (explicitly requested) in $namespaces",
            )
        }
    }

    @Test
    fun testIgnoredStreamsFiltersTablesAndViews() {
        h2.execute("CREATE TABLE hidden (id INT PRIMARY KEY)")
        h2.execute("CREATE VIEW kv_view AS SELECT * FROM kv")
        val filteringFactory =
            JdbcMetadataQuerier.Factory(
                selectQueryGenerator = H2SourceOperations(),
                fieldTypeMapper = H2SourceOperations(),
                checkQueries = JdbcCheckQueries(),
                constants = DefaultJdbcConstants(ignoredStreams = setOf("HIDDEN", "KV_VIEW")),
            )
        val configPojo =
            H2SourceConfigurationSpecification().apply {
                port = h2.port
                database = h2.database
            }
        val config: H2SourceConfiguration = H2SourceConfigurationFactory().make(configPojo)
        filteringFactory.session(config).use { mdq: MetadataQuerier ->
            val streams: List<String> = mdq.streamNames("PUBLIC").map { it.name }
            Assertions.assertFalse(
                streams.contains("HIDDEN"),
                "HIDDEN table should have been filtered, got $streams",
            )
            Assertions.assertFalse(
                streams.contains("KV_VIEW"),
                "KV_VIEW view should have been filtered, got $streams",
            )
            Assertions.assertTrue(
                streams.contains("KV"),
                "expected KV in $streams",
            )
        }
    }

    @Test
    fun test() {
        val configPojo =
            H2SourceConfigurationSpecification().apply {
                port = h2.port
                database = h2.database
            }
        val config: H2SourceConfiguration = H2SourceConfigurationFactory().make(configPojo)
        factory.session(config).use { mdq: MetadataQuerier ->
            Assertions.assertEquals(listOf("PUBLIC"), mdq.streamNamespaces())
            Assertions.assertEquals(
                listOf("PUBLIC.KV"),
                mdq.streamNames("PUBLIC").map { it.toString() },
            )
            val expectedColumnMetadata: List<JdbcMetadataQuerier.ColumnMetadata> =
                listOf(
                    JdbcMetadataQuerier.ColumnMetadata(
                        name = "_ROWID_",
                        label = "_ROWID_",
                        type =
                            SystemType(
                                typeName = "BIGINT",
                                typeCode = JDBCType.BIGINT.vendorTypeNumber,
                                precision = 64,
                                scale = 0,
                            ),
                        nullable = false,
                    ),
                    JdbcMetadataQuerier.ColumnMetadata(
                        name = "K",
                        label = "K",
                        type =
                            SystemType(
                                typeName = "INTEGER",
                                typeCode = JDBCType.INTEGER.vendorTypeNumber,
                                precision = 32,
                                scale = 0,
                            ),
                        nullable = false,
                    ),
                    JdbcMetadataQuerier.ColumnMetadata(
                        name = "V",
                        label = "V",
                        type =
                            SystemType(
                                typeName = "CHARACTER VARYING",
                                typeCode = JDBCType.VARCHAR.vendorTypeNumber,
                                precision = 60,
                                scale = 0,
                            ),
                        nullable = true,
                    ),
                )
            val desc = StreamDescriptor().withNamespace("PUBLIC").withName("KV")
            val streamID: StreamIdentifier = StreamIdentifier.from(desc)
            val tableName = (mdq as JdbcMetadataQuerier).findTableName(streamID)
            Assertions.assertNotNull(tableName)
            Assertions.assertEquals(expectedColumnMetadata, mdq.columnMetadata(tableName!!))
            Assertions.assertEquals(listOf(listOf("K")), mdq.primaryKey(streamID))
        }
    }
}
