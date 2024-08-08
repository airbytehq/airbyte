/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.jdbc

import io.airbyte.cdk.source.MetadataQuerier
import io.airbyte.cdk.test.source.FakeSourceConfiguration
import io.airbyte.cdk.test.source.FakeSourceConfigurationFactory
import io.airbyte.cdk.test.source.FakeSourceConfigurationJsonObject
import io.airbyte.cdk.test.source.FakeSourceOperations
import java.sql.JDBCType
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JdbcMetadataQuerierTest {
    val h2 = H2TestFixture()

    init {
        h2.execute("CREATE TABLE kv (k INT PRIMARY KEY, v VARCHAR(60))")
    }

    val factory = JdbcMetadataQuerier.Factory(FakeSourceOperations(), FakeSourceOperations())

    @Test
    fun test() {
        val configPojo =
            FakeSourceConfigurationJsonObject().apply {
                port = h2.port
                database = h2.database
            }
        val config: FakeSourceConfiguration = FakeSourceConfigurationFactory().make(configPojo)
        factory.session(config).use { mdq: MetadataQuerier ->
            Assertions.assertEquals(listOf("PUBLIC"), mdq.streamNamespaces())
            Assertions.assertEquals(listOf("KV"), mdq.streamNames("PUBLIC"))
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
            val tableName = (mdq as JdbcMetadataQuerier).findTableName("KV", "PUBLIC")
            Assertions.assertNotNull(tableName)
            Assertions.assertEquals(expectedColumnMetadata, mdq.columnMetadata(tableName!!))
            Assertions.assertEquals(listOf(listOf("K")), mdq.primaryKeys("KV", "PUBLIC"))
        }
    }
}
