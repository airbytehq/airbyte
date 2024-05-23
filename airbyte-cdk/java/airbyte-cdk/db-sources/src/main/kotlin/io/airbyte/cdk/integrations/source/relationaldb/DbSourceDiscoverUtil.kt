/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb

import com.google.common.collect.Lists
import io.airbyte.protocol.models.CommonField
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.SyncMode
import java.util.*
import java.util.function.Consumer
import java.util.function.Function
import java.util.stream.Collectors
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/** Contains utilities and helper classes for discovering schemas in database sources. */
object DbSourceDiscoverUtil {
    private val LOGGER: Logger = LoggerFactory.getLogger(DbSourceDiscoverUtil::class.java)
    private val AIRBYTE_METADATA: List<String> =
        mutableListOf("_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at")

    /*
     * This method logs schema drift between source table and the catalog. This can happen if (i)
     * underlying table schema changed between syncs (ii) The source connector's mapping of datatypes to
     * Airbyte types changed between runs
     */
    @JvmStatic
    fun <DataType> logSourceSchemaChange(
        fullyQualifiedTableNameToInfo: Map<String?, TableInfo<CommonField<DataType>>>,
        catalog: ConfiguredAirbyteCatalog,
        airbyteTypeConverter: Function<DataType, JsonSchemaType>
    ) {
        for (airbyteStream in catalog.streams) {
            val stream = airbyteStream.stream
            val fullyQualifiedTableName = getFullyQualifiedTableName(stream.namespace, stream.name)
            if (!fullyQualifiedTableNameToInfo.containsKey(fullyQualifiedTableName)) {
                continue
            }
            val table = fullyQualifiedTableNameToInfo[fullyQualifiedTableName]!!
            val fields =
                table.fields
                    .stream()
                    .map { commonField: CommonField<DataType> ->
                        toField(commonField, airbyteTypeConverter)
                    }
                    .distinct()
                    .toList()
            val currentJsonSchema = CatalogHelpers.fieldsToJsonSchema(fields)
            val catalogSchema = stream.jsonSchema
            val currentSchemaProperties = currentJsonSchema["properties"]
            val catalogProperties = catalogSchema["properties"]
            val mismatchedFields: MutableList<String> = ArrayList()
            catalogProperties.fieldNames().forEachRemaining { fieldName: String ->
                // Ignoring metadata fields since those are automatically added onto the catalog
                // schema by Airbyte
                // and don't exist in the source schema. They should not be considered a change
                if (AIRBYTE_METADATA.contains(fieldName)) {
                    return@forEachRemaining
                }
                if (
                    !currentSchemaProperties.has(fieldName) ||
                        currentSchemaProperties[fieldName] != catalogProperties[fieldName]
                ) {
                    mismatchedFields.add(fieldName)
                }
            }

            if (!mismatchedFields.isEmpty()) {
                LOGGER.warn(
                    "Source schema changed for table {}! Potential mismatches: {}. Actual schema: {}. Catalog schema: {}",
                    fullyQualifiedTableName,
                    java.lang.String.join(", ", mismatchedFields.toString()),
                    currentJsonSchema,
                    catalogSchema
                )
            }
        }
    }

    fun <DataType> convertTableInfosToAirbyteCatalog(
        tableInfos: List<TableInfo<CommonField<DataType>>>,
        fullyQualifiedTableNameToPrimaryKeys: Map<String, MutableList<String>>,
        airbyteTypeConverter: Function<DataType, JsonSchemaType>
    ): AirbyteCatalog {
        val tableInfoFieldList =
            tableInfos
                .stream()
                .map { t: TableInfo<CommonField<DataType>> ->
                    // some databases return multiple copies of the same record for a column (e.g.
                    // redshift) because
                    // they have at least once delivery guarantees. we want to dedupe these, but
                    // first we check that the
                    // records are actually the same and provide a good error message if they are
                    // not.
                    assertColumnsWithSameNameAreSame(t.nameSpace, t.name, t.fields)
                    val fields =
                        t.fields
                            .stream()
                            .map { commonField: CommonField<DataType> ->
                                toField(commonField, airbyteTypeConverter)
                            }
                            .distinct()
                            .toList()
                    val fullyQualifiedTableName = getFullyQualifiedTableName(t.nameSpace, t.name)
                    val primaryKeys =
                        fullyQualifiedTableNameToPrimaryKeys.getOrDefault(
                            fullyQualifiedTableName,
                            emptyList()
                        )
                    TableInfo(
                        nameSpace = t.nameSpace,
                        name = t.name,
                        fields = fields,
                        primaryKeys = primaryKeys,
                        cursorFields = t.cursorFields
                    )
                }
                .toList()

        val streams =
            tableInfoFieldList
                .map { tableInfo: TableInfo<Field> ->
                    val primaryKeys =
                        tableInfo.primaryKeys
                            .stream()
                            .filter { obj: String -> Objects.nonNull(obj) }
                            .map { listOf(it) }
                            .toList()
                    CatalogHelpers.createAirbyteStream(
                            tableInfo.name,
                            tableInfo.nameSpace,
                            tableInfo.fields
                        )
                        .withSupportedSyncModes(
                            if (tableInfo.cursorFields.isEmpty())
                                Lists.newArrayList(SyncMode.FULL_REFRESH)
                            else Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                        )
                        .withSourceDefinedPrimaryKey(primaryKeys)
                }
                .toMutableList() // This is ugly, but we modify this list in
        // JdbcSourceAcceptanceTest.testDiscoverWithMultipleSchemas
        return AirbyteCatalog().withStreams(streams)
    }

    @JvmStatic
    fun getFullyQualifiedTableName(nameSpace: String?, tableName: String): String {
        return if (nameSpace != null) "$nameSpace.$tableName" else tableName
    }

    private fun <DataType> toField(
        commonField: CommonField<DataType>,
        airbyteTypeConverter: Function<DataType, JsonSchemaType>
    ): Field {
        if (
            airbyteTypeConverter.apply(commonField.type) === JsonSchemaType.OBJECT &&
                commonField.properties != null &&
                !commonField.properties.isEmpty()
        ) {
            val properties =
                commonField.properties
                    .stream()
                    .map { commField: CommonField<DataType> ->
                        toField(commField, airbyteTypeConverter)
                    }
                    .toList()
            return Field.of(
                commonField.name,
                airbyteTypeConverter.apply(commonField.type),
                properties
            )
        } else {
            return Field.of(commonField.name, airbyteTypeConverter.apply(commonField.type))
        }
    }

    private fun <DataType> assertColumnsWithSameNameAreSame(
        nameSpace: String,
        tableName: String,
        columns: List<CommonField<DataType>>
    ) {
        columns
            .stream()
            .collect(Collectors.groupingBy(Function { obj: CommonField<DataType> -> obj.name }))
            .values
            .forEach(
                Consumer { columnsWithSameName: List<CommonField<DataType>> ->
                    val comparisonColumn = columnsWithSameName[0]
                    columnsWithSameName.forEach(
                        Consumer { column: CommonField<DataType> ->
                            if (column != comparisonColumn) {
                                throw RuntimeException(
                                    String.format(
                                        "Found multiple columns with same name: %s in table: %s.%s but the columns are not the same. columns: %s",
                                        comparisonColumn.name,
                                        nameSpace,
                                        tableName,
                                        columns
                                    )
                                )
                            }
                        }
                    )
                }
            )
    }
}
