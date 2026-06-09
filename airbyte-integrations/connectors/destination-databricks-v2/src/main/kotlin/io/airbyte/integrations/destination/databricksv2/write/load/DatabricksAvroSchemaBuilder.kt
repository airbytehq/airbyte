/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.write.load

import io.airbyte.cdk.load.component.ColumnType
import org.apache.avro.LogicalTypes
import org.apache.avro.Schema

/** Builds an Avro [Schema] from Databricks column schema (map of column names to [ColumnType]) */
object DatabricksAvroSchemaBuilder {

    private val DECIMAL_SCHEMA: Schema =
        Schema.create(Schema.Type.BYTES).also { LogicalTypes.decimal(38, 10).addToSchema(it) }

    private val DATE_SCHEMA: Schema =
        Schema.create(Schema.Type.INT).also { LogicalTypes.date().addToSchema(it) }

    private val TIMESTAMP_SCHEMA: Schema =
        Schema.create(Schema.Type.LONG).also { LogicalTypes.timestampMicros().addToSchema(it) }

    private val TIMESTAMP_NTZ_SCHEMA: Schema =
        Schema.create(Schema.Type.LONG).also { LogicalTypes.localTimestampMicros().addToSchema(it) }

    /** Builds an Avro record schema from Databricks column types. */
    fun buildAvroSchema(columnSchema: Map<String, ColumnType>): Schema {
        val fields =
            columnSchema.map { (name, colType) ->
                val baseType = databricksTypeToAvro(colType.type)
                val fieldSchema = Schema.createUnion(Schema.create(Schema.Type.NULL), baseType)
                Schema.Field(name, fieldSchema, null, null as Any?)
            }
        return Schema.createRecord("record", null, null, false, fields)
    }

    /** Maps a Databricks SQL type string to an Avro [Schema] */
    private fun databricksTypeToAvro(databricksType: String): Schema {
        val upperType = databricksType.uppercase().trim()
        return when {
            upperType == "STRING" -> Schema.create(Schema.Type.STRING)
            upperType == "BOOLEAN" -> Schema.create(Schema.Type.BOOLEAN)
            upperType == "LONG" || upperType == "BIGINT" -> Schema.create(Schema.Type.LONG)
            upperType.startsWith("DECIMAL") -> DECIMAL_SCHEMA
            upperType == "TIMESTAMP_NTZ" -> TIMESTAMP_NTZ_SCHEMA
            upperType == "TIMESTAMP" -> TIMESTAMP_SCHEMA
            upperType == "DATE" -> DATE_SCHEMA
            else -> Schema.create(Schema.Type.STRING)
        }
    }
}
