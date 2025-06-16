/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping

import com.google.cloud.bigquery.*
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.integrations.base.destination.typing_deduping.BaseDestinationV1V2Migrator
import io.airbyte.integrations.base.destination.typing_deduping.CollectionUtils.containsAllIgnoreCase
import io.airbyte.integrations.base.destination.typing_deduping.NamespacedTableName
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer
import java.util.*
import java.util.stream.Collectors

class BigQueryV1V2Migrator(
    private val bq: BigQuery,
    private val nameTransformer: BigQuerySQLNameTransformer
) : BaseDestinationV1V2Migrator<TableDefinition>() {
    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    override fun doesAirbyteInternalNamespaceExist(streamConfig: StreamConfig?): Boolean {
        val dataset = bq.getDataset(streamConfig!!.id.rawNamespace)
        return dataset != null && dataset.exists()
    }

    override fun getTableIfExists(
        namespace: String?,
        tableName: String?
    ): Optional<TableDefinition> {
        val table = bq.getTable(TableId.of(namespace, tableName))
        return if (table != null && table.exists()) Optional.of(table.getDefinition())
        else Optional.empty()
    }

    override fun schemaMatchesExpectation(
        existingTable: TableDefinition,
        columns: Collection<String>
    ): Boolean {
        val existingSchemaColumns =
            Optional.ofNullable(existingTable.schema)
                .map { schema: Schema ->
                    schema.fields
                        .stream()
                        .map { obj: Field -> obj.name }
                        .collect(Collectors.toSet())
                }
                .orElse(emptySet())

        return !existingSchemaColumns.isEmpty() &&
            containsAllIgnoreCase(columns, existingSchemaColumns)
    }

    @Suppress("deprecation")
    override fun convertToV1RawName(streamConfig: StreamConfig): NamespacedTableName {
        return NamespacedTableName(
            nameTransformer.getNamespace(streamConfig.id.originalNamespace),
            nameTransformer.getRawTableName(streamConfig.id.originalName)
        )
    }
}
