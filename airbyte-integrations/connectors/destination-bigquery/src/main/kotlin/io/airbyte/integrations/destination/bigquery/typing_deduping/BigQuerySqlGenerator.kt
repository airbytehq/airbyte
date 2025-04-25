/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping

import com.google.cloud.bigquery.StandardSQLTypeName
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingSqlGenerator
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer
import java.time.Instant
import java.util.*

/**
 * @param projectId
 * @param datasetLocation This is technically redundant with [BigQueryDatabaseHandler] setting the
 * query execution location, but let's be explicit since this is typically a compliance requirement.
 */
class BigQuerySqlGenerator(private val projectId: String?, private val datasetLocation: String?) :
    TypingDedupingSqlGenerator {

    override fun createFinalTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        finalTableSuffix: String,
        replace: Boolean
    ) = Sql.empty()

    override fun prepareTablesForSoftReset(
        stream: DestinationStream,
        tableNames: TableNames,
        columnNameMapping: ColumnNameMapping,
    ) = Sql.empty()

    override fun clearLoadedAt(stream: DestinationStream, rawTableName: TableName) = Sql.empty()

    override fun updateFinalTable(
        stream: DestinationStream,
        tableNames: TableNames,
        columnNameMapping: ColumnNameMapping,
        finalTableSuffix: String,
        maxProcessedTimestamp: Instant?,
        useExpensiveSaferCasting: Boolean,
    ) = Sql.empty()

    override fun overwriteFinalTable(
        stream: DestinationStream,
        finalTableName: TableName,
        finalTableSuffix: String,
    ) = Sql.empty()

    companion object {
        val nameTransformer = BigQuerySQLNameTransformer()

        fun toDialectType(type: AirbyteType): StandardSQLTypeName =
            when (type) {
                BooleanType -> StandardSQLTypeName.BOOL
                DateType -> StandardSQLTypeName.DATE
                IntegerType -> StandardSQLTypeName.INT64
                NumberType -> StandardSQLTypeName.NUMERIC
                StringType -> StandardSQLTypeName.STRING
                TimeTypeWithTimezone -> StandardSQLTypeName.STRING
                TimeTypeWithoutTimezone -> StandardSQLTypeName.TIME
                TimestampTypeWithTimezone -> StandardSQLTypeName.TIMESTAMP
                TimestampTypeWithoutTimezone -> StandardSQLTypeName.DATETIME
                is ArrayType,
                ArrayTypeWithoutSchema,
                is ObjectType,
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema -> StandardSQLTypeName.JSON
                is UnionType ->
                    if (type.isLegacyUnion) {
                        toDialectType(type.chooseType())
                    } else {
                        StandardSQLTypeName.JSON
                    }
                is UnknownType -> StandardSQLTypeName.JSON
            }

        fun clusteringColumns(
            stream: DestinationStream,
            columnNameMapping: ColumnNameMapping
        ): List<String> {
            val clusterColumns: MutableList<String> = ArrayList()
            if (stream.importType is Dedupe) {
                // We're doing de-duping, therefore we have a primary key.
                // Cluster on the first 3 PK columns since BigQuery only allows up to 4 clustering
                // columns,
                // and we're always clustering on _airbyte_extracted_at
                (stream.importType as Dedupe).primaryKey.stream().limit(3).forEach {
                    pk: List<String> ->
                    clusterColumns.add(columnNameMapping[pk.first()]!!)
                }
            }
            clusterColumns.add("_airbyte_extracted_at")
            return clusterColumns
        }
    }
}
