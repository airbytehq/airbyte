/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.do_stuff_with_tables

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
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.DestinationColumnNameMapping
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.LegacyTypingDedupingUtil
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.Sql
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.TableName

class BigquerySqlGenerator(private val projectId: String?) {
    fun createRawTableIfNotExists(
        stream: DestinationStream,
        rawTableName: TableName,
        suffix: String,
    ): Sql {
        return Sql.of(
            """
            CREATE IF NOT EXISTS TABLE $projectId.${quote(rawTableName.namespace)}.${quote(rawTableName.name)}$suffix (
              _airbyte_raw_id STRING,
              _airbyte_extracted_at TIMESTAMP,
              _airbyte_loaded_at TIMESTAMP,
              _airbyte_data STRING,
              _airbyte_meta STRING,
              _airbyte_generation_id INT64
            )
            PARTITION BY
              RANGE_BUCKET(_airbyte_generation_id, GENERATE_ARRAY(0, 10000, 5))
            CLUSTER BY
              _airbyte_extracted_at
            """.trimIndent()
        )
    }

    fun createFinalTable(
        stream: DestinationStream,
        finalTableName: TableName,
        destinationColumnNames: DestinationColumnNameMapping,
        suffix: String,
        force: Boolean,
    ): Sql {
        val columnDeclarations = columnsAndTypes(stream, destinationColumnNames)
        val clusterConfig =
            clusteringColumns(stream, destinationColumnNames).joinToString(", ") { quote(it) }
        val forceCreateTable = if (force) "OR REPLACE" else ""

        return Sql.of(
            """
            CREATE $forceCreateTable TABLE $projectId.${quote(finalTableName.namespace)}.${quote(finalTableName.name)}$suffix (
              _airbyte_raw_id STRING NOT NULL,
              _airbyte_extracted_at TIMESTAMP NOT NULL,
              _airbyte_meta JSON NOT NULL,
              _airbyte_generation_id INTEGER,
              $columnDeclarations
            )
            PARTITION BY (DATE_TRUNC(_airbyte_extracted_at, DAY))
            CLUSTER BY $clusterConfig;
            """.trimIndent(),
        )
    }

    private fun columnsAndTypes(
        stream: DestinationStream,
        destinationColumnNames: DestinationColumnNameMapping,
    ): String {
        return destinationColumnNames.entries
            .map { (origColumName, destinationColumnName) ->
                val type = (stream.schema as ObjectType).properties[origColumName]!!
                quote(destinationColumnName) + " " + toDialectType(type.type).name
            }
            .joinToString { ",\n" }
    }

    private fun clusteringColumns(
        stream: DestinationStream,
        destinationColumnNames: DestinationColumnNameMapping,
    ): List<String> {
        val clusterColumns: MutableList<String> = ArrayList()
        if (stream.importType is Dedupe) {
            // We're doing de-duping, therefore we have a primary key.
            // Cluster on the first 3 PK columns since BigQuery only allows up to 4 clustering
            // columns,
            // and we're always clustering on _airbyte_extracted_at
            (stream.importType as Dedupe).primaryKey.take(3).forEach { origColumnName ->
                // needing the [0] to get the first PK element is gross
                clusterColumns.add(destinationColumnNames[origColumnName[0]]!!)
            }
        }
        clusterColumns.add("_airbyte_extracted_at")
        return clusterColumns
    }

    private fun toDialectType(type: AirbyteType): StandardSQLTypeName =
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
            is UnionType -> {
                val typeWithPrecedence: AirbyteType = LegacyTypingDedupingUtil.chooseType(type)
                when (typeWithPrecedence) {
                    ArrayTypeWithoutSchema,
                    is ArrayType,
                    is ObjectType,
                    ObjectTypeWithEmptySchema,
                    ObjectTypeWithoutSchema -> StandardSQLTypeName.JSON
                    else -> toDialectType(typeWithPrecedence)
                }
            }
            ArrayTypeWithoutSchema,
            is ArrayType,
            is ObjectType,
            ObjectTypeWithEmptySchema,
            ObjectTypeWithoutSchema,
            is UnknownType -> StandardSQLTypeName.JSON
        }

    companion object {
        private const val QUOTE: Char = '`'
        private fun quote(identifier: String) = "$QUOTE$identifier$QUOTE"
    }
}
