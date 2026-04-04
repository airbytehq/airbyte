/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.schema

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.iceberg.parquet.GlueCatalogConfiguration
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.s3_data_lake.spec.S3DataLakeConfiguration
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

/**
 * AWS Glue requires lowercase database+table names. Table/namespace lowercasing is always applied.
 * Column lowercasing is controlled by the [lowercaseColumnNames] toggle.
 */
class GlueTableSchemaMapper(
    private val databaseName: String?,
    private val tempTableNameGenerator: TempTableNameGenerator,
    private val lowercaseColumnNames: Boolean = false,
) : TableSchemaMapper {
    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName {
        val namespace =
            Transformations.toAlphanumericAndUnderscore(
                (desc.namespace ?: databaseName)!!.lowercase()
            )
        val name = Transformations.toAlphanumericAndUnderscore(desc.name.lowercase())
        return TableName(namespace, name)
    }

    override fun toTempTableName(tableName: TableName): TableName {
        return tempTableNameGenerator.generate(tableName)
    }

    override fun toColumnName(name: String): String {
        return if (lowercaseColumnNames) {
            toSnakeCaseColumnName(name)
        } else {
            name
        }
    }

    override fun toColumnType(fieldType: FieldType): ColumnType =
        ColumnType(fieldType.type.toString(), fieldType.nullable)
}

/**
 * Default mapper for non-Glue catalogs (Nessie, REST, Polaris). Passes table/namespace identifiers
 * through unchanged. Column lowercasing is controlled by the [lowercaseColumnNames] toggle.
 */
class S3DataLakeDefaultTableSchemaMapper(
    private val tempTableNameGenerator: TempTableNameGenerator,
    private val lowercaseColumnNames: Boolean = false,
) : TableSchemaMapper {
    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName =
        TableName(desc.namespace ?: "", desc.name)

    override fun toTempTableName(tableName: TableName): TableName =
        tempTableNameGenerator.generate(tableName)

    override fun toColumnName(name: String): String {
        return if (lowercaseColumnNames) {
            toSnakeCaseColumnName(name)
        } else {
            name
        }
    }

    override fun toColumnType(fieldType: FieldType): ColumnType =
        ColumnType(fieldType.type.toString(), fieldType.nullable)
}

private val CAMEL_BOUNDARY = Regex("([a-z0-9])([A-Z])")
private val ACRONYM_BOUNDARY = Regex("([A-Z]+)([A-Z][a-z])")

fun toSnakeCaseColumnName(name: String): String {
    val snaked =
        ACRONYM_BOUNDARY.replace(
            CAMEL_BOUNDARY.replace(name) { "${it.groupValues[1]}_${it.groupValues[2]}" }
        ) { "${it.groupValues[1]}_${it.groupValues[2]}" }
    return Transformations.toAlphanumericAndUnderscore(snaked.lowercase())
}

@Factory
class S3DataLakeTableSchemaMapperFactory(
    private val config: S3DataLakeConfiguration,
) {
    @Singleton
    @Primary
    fun create(): TableSchemaMapper {
        val tempTableNameGenerator = DefaultTempTableNameGenerator()
        val catalogConfig = config.icebergCatalogConfiguration.catalogConfiguration
        return when (catalogConfig) {
            is GlueCatalogConfiguration ->
                GlueTableSchemaMapper(
                    databaseName = catalogConfig.databaseName,
                    tempTableNameGenerator = tempTableNameGenerator,
                    lowercaseColumnNames = config.lowercaseColumnNames,
                )
            else ->
                S3DataLakeDefaultTableSchemaMapper(
                    tempTableNameGenerator = tempTableNameGenerator,
                    lowercaseColumnNames = config.lowercaseColumnNames,
                )
        }
    }
}
