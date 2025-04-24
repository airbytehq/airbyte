/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.cloud.bigquery.FieldValueList
import com.google.cloud.bigquery.Schema
import com.google.cloud.bigquery.StandardSQLTypeName
import com.google.cloud.bigquery.TableResult
import io.airbyte.commons.json.Jsons.deserializeExact
import io.airbyte.commons.json.Jsons.emptyObject
import io.airbyte.commons.json.Jsons.jsonNode

object BigQuerySqlGeneratorIntegrationTest {
    /**
     * TableResult contains records in a somewhat nonintuitive format (and it avoids loading them
     * all into memory). That's annoying for us since we're working with small test data, so just
     * pull everything into a list.
     */
    fun toJsonRecords(result: TableResult): List<JsonNode> {
        return result
            .streamAll()
            .map { row: FieldValueList -> toJson(result.schema!!, row) }
            .toList()
    }

    /**
     * FieldValueList stores everything internally as string (I think?) but provides conversions to
     * more useful types. This method does that conversion, using the schema to determine which type
     * is most appropriate. Then we just dump everything into a jsonnode for interop with
     * RecordDiffer.
     */
    private fun toJson(schema: Schema, row: FieldValueList): JsonNode {
        val json = emptyObject() as ObjectNode
        for (i in schema.fields.indices) {
            val field = schema.fields[i]
            val value = row[i]
            val typedValue: JsonNode
            if (!value.isNull) {
                typedValue =
                    when (field.type.standardType) {
                        StandardSQLTypeName.BOOL -> jsonNode(value.booleanValue)
                        StandardSQLTypeName.INT64 -> jsonNode(value.longValue)
                        StandardSQLTypeName.FLOAT64 -> jsonNode(value.doubleValue)
                        StandardSQLTypeName.NUMERIC,
                        StandardSQLTypeName.BIGNUMERIC -> jsonNode(value.numericValue)
                        StandardSQLTypeName.STRING -> jsonNode(value.stringValue)
                        StandardSQLTypeName.TIMESTAMP -> jsonNode(value.timestampInstant.toString())
                        StandardSQLTypeName.DATE,
                        StandardSQLTypeName.DATETIME,
                        StandardSQLTypeName.TIME -> jsonNode(value.stringValue)
                        StandardSQLTypeName.JSON -> jsonNode(deserializeExact(value.stringValue))
                        else -> jsonNode(value.stringValue)
                    }
                json.set<JsonNode>(field.name, typedValue)
            }
        }
        return json
    }
}
