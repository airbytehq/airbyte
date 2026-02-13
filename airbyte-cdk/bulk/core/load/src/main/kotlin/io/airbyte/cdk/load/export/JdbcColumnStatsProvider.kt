/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.export

import io.airbyte.cdk.load.schema.model.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import javax.sql.DataSource

@Singleton
@Requires(beans = [DataSource::class])
class JdbcColumnStatsProvider(
    private val dataSource: DataSource,
) : ColumnStatsProvider {
    private val log = KotlinLogging.logger {}

    override fun computeColumnStats(
        tableName: TableName,
        columnNames: Collection<String>,
    ): Map<String, ColumnStats> {
        val columnList = columnNames.toList()
        if (columnList.isEmpty()) {
            return emptyMap()
        }

        dataSource.connection.use { conn ->
            val quote = conn.metaData.identifierQuoteString ?: "\""
            val countExprs =
                columnList.joinToString(", ") { col -> "COUNT($quote$col$quote)" }
            val qualifiedTable =
                "$quote${tableName.namespace}$quote.$quote${tableName.name}$quote"
            val sql = "SELECT COUNT(*) AS _total, $countExprs FROM $qualifiedTable"
            log.info { "Running stats query: $sql" }

            conn.createStatement().use { stmt ->
                stmt.executeQuery(sql).use { rs ->
                    if (!rs.next()) return emptyMap()
                    val total = rs.getLong(1)
                    return columnList.mapIndexed { index, col ->
                        val nonNullCount = rs.getLong(index + 2)
                        col to
                            ColumnStats(
                                nullCount = total - nonNullCount,
                                nonNullCount = nonNullCount,
                            )
                    }.toMap()
                }
            }
        }
    }
}
