/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.schema

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.integrations.destination.s3_data_lake.spec.S3DataLakeConfiguration
import jakarta.inject.Singleton

/**
 * Maps input schema names to the names actually written to Iceberg.
 *
 * Table identifiers are owned by the catalog-specific [TableIdGenerator] (the Iceberg toolkit
 * resolves tables through it), so this mapper delegates to it rather than duplicating the Glue /
 * Nessie / REST / Polaris naming rules. That keeps the CDK's view of the final table name in sync
 * with the identifier the toolkit uses.
 *
 * Column names are passed through unchanged unless [S3DataLakeConfiguration.lowercaseColumnNames]
 * is enabled, in which case they are lowercased (and nothing else: `URLs` becomes `urls`, `Foo.Bar`
 * becomes `foo.bar`). Case-insensitive collisions (e.g. `ID` and `id`) are resolved by the CDK's
 * [io.airbyte.cdk.load.schema.ColumnNameResolver] using the default [colsConflict] rule.
 */
@Singleton
class S3DataLakeTableSchemaMapper(
    private val config: S3DataLakeConfiguration,
    private val tableIdGenerator: TableIdGenerator,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : TableSchemaMapper {
    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName {
        val tableId = tableIdGenerator.toTableIdentifier(desc)
        return TableName(namespace = tableId.namespace().toString(), name = tableId.name())
    }

    override fun toTempTableName(tableName: TableName): TableName =
        tempTableNameGenerator.generate(tableName)

    override fun toColumnName(name: String): String =
        if (config.lowercaseColumnNames) name.lowercase() else name

    override fun toColumnType(fieldType: FieldType): ColumnType =
        ColumnType(fieldType.type.toString(), fieldType.nullable)
}
