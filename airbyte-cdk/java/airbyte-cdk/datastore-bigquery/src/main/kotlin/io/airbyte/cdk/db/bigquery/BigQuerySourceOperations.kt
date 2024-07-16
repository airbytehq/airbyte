/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.bigquery

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ContainerNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.FieldValue
import com.google.cloud.bigquery.QueryParameterValue
import com.google.cloud.bigquery.StandardSQLTypeName
import io.airbyte.cdk.db.DataTypeSupplier
import io.airbyte.cdk.db.DataTypeUtils.dateFormat
import io.airbyte.cdk.db.DataTypeUtils.returnNullIfInvalid
import io.airbyte.cdk.db.DataTypeUtils.toISO8601String
import io.airbyte.cdk.db.SourceOperations
import io.airbyte.cdk.db.util.JsonUtil.putBigDecimalValueIntoJson
import io.airbyte.cdk.db.util.JsonUtil.putBooleanValueIntoJson
import io.airbyte.cdk.db.util.JsonUtil.putBytesValueIntoJson
import io.airbyte.cdk.db.util.JsonUtil.putDoubleValueIntoJson
import io.airbyte.cdk.db.util.JsonUtil.putLongValueIntoJson
import io.airbyte.cdk.db.util.JsonUtil.putStringValueIntoJson
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.JsonSchemaType
import io.github.oshai.kotlinlogging.KotlinLogging
import java.text.DateFormat
import java.text.ParseException
import java.text.SimpleDateFormat
import java.util.*
import java.util.function.Consumer

private val LOGGER = KotlinLogging.logger {}

class BigQuerySourceOperations : SourceOperations<BigQueryResultSet, StandardSQLTypeName> {
    private val BIG_QUERY_DATE_FORMAT: DateFormat = SimpleDateFormat("yyyy-MM-dd")
    private val BIG_QUERY_DATETIME_FORMAT: DateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss")
    private val BIG_QUERY_TIMESTAMP_FORMAT: DateFormat =
        SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSSSS z")

    override fun rowToJson(queryResult: BigQueryResultSet): JsonNode {
        val jsonNode = Jsons.jsonNode(emptyMap<Any, Any>()) as ObjectNode
        queryResult.fieldList.forEach(
            Consumer { field: Field ->
                setJsonField(field, queryResult.rowValues[field.name], jsonNode)
            }
        )
        return jsonNode
    }

    private fun fillObjectNode(
        fieldName: String,
        fieldType: StandardSQLTypeName,
        fieldValue: FieldValue,
        node: ContainerNode<*>
    ) {
        when (fieldType) {
            StandardSQLTypeName.BOOL ->
                putBooleanValueIntoJson(node, fieldValue.booleanValue, fieldName)
            StandardSQLTypeName.INT64 -> putLongValueIntoJson(node, fieldValue.longValue, fieldName)
            StandardSQLTypeName.FLOAT64 ->
                putDoubleValueIntoJson(node, fieldValue.doubleValue, fieldName)
            StandardSQLTypeName.NUMERIC ->
                putBigDecimalValueIntoJson(node, fieldValue.numericValue, fieldName)
            StandardSQLTypeName.BIGNUMERIC ->
                putBigDecimalValueIntoJson(
                    node,
                    returnNullIfInvalid(DataTypeSupplier { fieldValue.numericValue }),
                    fieldName
                )
            StandardSQLTypeName.STRING,
            StandardSQLTypeName.TIME ->
                putStringValueIntoJson(node, fieldValue.stringValue, fieldName)
            StandardSQLTypeName.BYTES ->
                putBytesValueIntoJson(node, fieldValue.bytesValue, fieldName)
            StandardSQLTypeName.DATE ->
                putStringValueIntoJson(
                    node,
                    toISO8601String(getDateValue(fieldValue, BIG_QUERY_DATE_FORMAT)),
                    fieldName
                )
            StandardSQLTypeName.DATETIME ->
                putStringValueIntoJson(
                    node,
                    toISO8601String(getDateValue(fieldValue, BIG_QUERY_DATETIME_FORMAT)),
                    fieldName
                )
            StandardSQLTypeName.TIMESTAMP ->
                putStringValueIntoJson(
                    node,
                    toISO8601String(fieldValue.timestampValue / 1000),
                    fieldName
                )
            else -> putStringValueIntoJson(node, fieldValue.stringValue, fieldName)
        }
    }

    private fun setJsonField(field: Field, fieldValue: FieldValue, node: ObjectNode) {
        val fieldName = field.name
        if (fieldValue.attribute == FieldValue.Attribute.PRIMITIVE) {
            if (fieldValue.isNull) {
                node.put(fieldName, null as String?)
            } else {
                fillObjectNode(fieldName, field.type.standardType, fieldValue, node)
            }
        } else if (fieldValue.attribute == FieldValue.Attribute.REPEATED) {
            val arrayNode = node.putArray(fieldName)
            val fieldType = field.type.standardType
            val subFields = field.subFields
            // Array of primitive
            if (subFields == null || subFields.isEmpty()) {
                fieldValue.repeatedValue.forEach(
                    Consumer { arrayFieldValue: FieldValue ->
                        fillObjectNode(fieldName, fieldType, arrayFieldValue, arrayNode)
                    }
                )
                // Array of records
            } else {
                for (arrayFieldValue in fieldValue.repeatedValue) {
                    var count = 0 // named get doesn't work here for some reasons.
                    val newNode = arrayNode.addObject()
                    for (repeatedField in subFields) {
                        setJsonField(repeatedField, arrayFieldValue.recordValue[count++], newNode)
                    }
                }
            }
        } else if (fieldValue.attribute == FieldValue.Attribute.RECORD) {
            val newNode = node.putObject(fieldName)
            val subFields = field.subFields
            try {
                // named get doesn't work here with nested arrays and objects; index is the only
                // correlation between
                // field and field value
                if (subFields != null && !subFields.isEmpty()) {
                    for (i in subFields.indices) {
                        setJsonField(field.subFields[i], fieldValue.recordValue[i], newNode)
                    }
                }
            } catch (e: UnsupportedOperationException) {
                LOGGER.error { "Failed to parse Object field with name: $fieldName, ${e.message}" }
            }
        }
    }

    fun getDateValue(fieldValue: FieldValue, dateFormat: DateFormat): Date? {
        var parsedValue: Date? = null
        val value = fieldValue.stringValue
        try {
            parsedValue = dateFormat.parse(value)
        } catch (e: ParseException) {
            LOGGER.error { "Fail to parse date value : $value. Null is returned." }
        }
        return parsedValue
    }

    override fun getAirbyteType(sourceType: StandardSQLTypeName): JsonSchemaType {
        return when (sourceType) {
            StandardSQLTypeName.BOOL -> JsonSchemaType.BOOLEAN
            StandardSQLTypeName.INT64 -> JsonSchemaType.INTEGER
            StandardSQLTypeName.FLOAT64,
            StandardSQLTypeName.NUMERIC,
            StandardSQLTypeName.BIGNUMERIC -> JsonSchemaType.NUMBER
            StandardSQLTypeName.STRING,
            StandardSQLTypeName.BYTES,
            StandardSQLTypeName.TIMESTAMP,
            StandardSQLTypeName.DATE,
            StandardSQLTypeName.TIME,
            StandardSQLTypeName.DATETIME -> JsonSchemaType.STRING
            StandardSQLTypeName.ARRAY -> JsonSchemaType.ARRAY
            StandardSQLTypeName.STRUCT -> JsonSchemaType.OBJECT
            else -> JsonSchemaType.STRING
        }
    }

    private fun getFormattedValue(paramType: StandardSQLTypeName, paramValue: String): String {
        try {
            return when (paramType) {
                StandardSQLTypeName.DATE ->
                    BIG_QUERY_DATE_FORMAT.format(dateFormat.parse(paramValue))
                StandardSQLTypeName.DATETIME ->
                    BIG_QUERY_DATETIME_FORMAT.format(dateFormat.parse(paramValue))
                StandardSQLTypeName.TIMESTAMP ->
                    BIG_QUERY_TIMESTAMP_FORMAT.format(dateFormat.parse(paramValue))
                else -> paramValue
            }
        } catch (e: ParseException) {
            throw RuntimeException(
                "Fail to parse value " + paramValue + " to type " + paramType.name,
                e
            )
        }
    }

    fun getQueryParameter(paramType: StandardSQLTypeName, paramValue: String): QueryParameterValue {
        val value = getFormattedValue(paramType, paramValue)
        LOGGER.info { "Query parameter for set : $value. Type: ${paramType.name}" }
        return QueryParameterValue.newBuilder().setType(paramType).setValue(value).build()
    }

    companion object {}
}
