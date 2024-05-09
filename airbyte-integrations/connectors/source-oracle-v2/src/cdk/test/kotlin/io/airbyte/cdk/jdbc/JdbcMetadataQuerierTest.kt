/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.jdbc

import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.test.source.TestSourceConfiguration
import io.airbyte.cdk.test.source.TestSourceConfigurationFactory
import io.airbyte.cdk.test.source.TestSourceConfigurationJsonObject
import io.airbyte.cdk.test.source.TestSourceOperations
import java.lang.Long
import java.lang.String
import java.sql.JDBCType
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JdbcMetadataQuerierTest {

    val h2 = H2TestFixture()

    init {
        h2.execute("CREATE TABLE kv (k INT PRIMARY KEY, v VARCHAR(60))")
    }

    val factory = JdbcMetadataQuerier.Factory(TestSourceOperations(), TestSourceOperations())

    @Test
    fun test() {
        val configPojo =
            TestSourceConfigurationJsonObject().apply {
                port = h2.port
                database = h2.database
            }
        val config: TestSourceConfiguration = TestSourceConfigurationFactory().make(configPojo)
        factory.session(config).use { mdq: MetadataQuerier ->
            val actualTableNames: List<TableName> = mdq.tableNames()
            val expectedTableName = TableName(schema = "PUBLIC", name = "KV", type = "BASE TABLE")
            Assertions.assertEquals(
                listOf(expectedTableName),
                actualTableNames.map { it.copy(catalog = null) }
            )
            val tableName: TableName = actualTableNames.first()
            val expectedColumnMetadata: List<ColumnMetadata> =
                listOf(
                    ColumnMetadata(
                        name = "_ROWID_",
                        label = "_ROWID_",
                        type =
                            SystemType(
                                typeName = "BIGINT",
                                klazz = Long::class.java,
                                typeCode = JDBCType.BIGINT.vendorTypeNumber,
                                signed = true,
                                displaySize = 20,
                                precision = 64,
                                scale = 0
                            ),
                        autoIncrement = false,
                        caseSensitive = true,
                        searchable = true,
                        currency = false,
                        nullable = false,
                    ),
                    ColumnMetadata(
                        name = "K",
                        label = "K",
                        type =
                            SystemType(
                                typeName = "INTEGER",
                                klazz = Integer::class.java,
                                typeCode = JDBCType.INTEGER.vendorTypeNumber,
                                signed = true,
                                displaySize = 11,
                                precision = 32,
                                scale = 0
                            ),
                        autoIncrement = false,
                        caseSensitive = true,
                        searchable = true,
                        currency = false,
                        nullable = false,
                    ),
                    ColumnMetadata(
                        name = "V",
                        label = "V",
                        type =
                            SystemType(
                                typeName = "CHARACTER VARYING",
                                klazz = String::class.java,
                                typeCode = JDBCType.VARCHAR.vendorTypeNumber,
                                signed = false,
                                displaySize = 60,
                                precision = 60,
                                scale = 0
                            ),
                        autoIncrement = false,
                        caseSensitive = true,
                        searchable = true,
                        currency = false,
                        nullable = true,
                    )
                )

            Assertions.assertEquals(expectedColumnMetadata, (mdq as JdbcMetadataQuerier).columnMetadata(tableName))
            Assertions.assertEquals(listOf(listOf("K")), mdq.primaryKeys(tableName))
        }
    }
}
