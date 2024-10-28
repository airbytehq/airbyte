/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
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
