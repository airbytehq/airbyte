/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2.readapi

import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.JsonStringFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryArrayFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryBigNumericFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryBooleanFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryDateFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryDateTimeFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryDoubleFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryLongFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryStructFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryTimeFieldType

/**
 * Value fidelity gate of the Storage Read API read path: a table is only read through it when every
 * column, nested ones included, has a type whose Arrow decoding was verified to produce records
 * identical to the query API path's. A table with any other column type is declined and read
 * through the query API instead.
 */
object BigQueryReadApiEligibility {

    /** The top-level or nested column (dot path) whose type is not verified, or null. */
    fun unsupportedColumn(fields: List<EmittedField>): String? {
        for (field in fields) {
            unsupportedColumn(field.id, field.type)?.let {
                return it
            }
        }
        return null
    }

    /**
     * Whether [cursor] can drive the initial snapshot of an incremental stream on this path: its
     * maximum is computable with `MAX()` and the value binds back as a `WHERE cursor > ?` lower
     * bound on the query API, which is how the following syncs read the deltas. These are the nine
     * cursor types validated cold and warm on the real service (plus `STRING`).
     */
    fun isSupportedCursor(cursor: EmittedField): Boolean =
        when (cursor.type) {
            BigQueryLongFieldType,
            BigQueryDoubleFieldType,
            BigDecimalFieldType,
            BigQueryBigNumericFieldType,
            StringFieldType,
            BigQueryDateFieldType,
            BigQueryDateTimeFieldType,
            BigQueryTimeFieldType,
            OffsetDateTimeFieldType -> true
            else -> false
        }

    private fun unsupportedColumn(path: String, type: FieldType): String? =
        when (type) {
            BigQueryBooleanFieldType,
            BigQueryLongFieldType,
            BigQueryDoubleFieldType,
            BigDecimalFieldType,
            BigQueryBigNumericFieldType,
            StringFieldType,
            BytesFieldType,
            BigQueryDateFieldType,
            BigQueryDateTimeFieldType,
            BigQueryTimeFieldType,
            OffsetDateTimeFieldType,
            JsonStringFieldType -> null
            is BigQueryStructFieldType ->
                type.fields?.firstNotNullOfOrNull { unsupportedColumn("$path.${it.id}", it.type) }
                    ?: if (type.fields == null) "$path (STRUCT without a known schema)" else null
            is BigQueryArrayFieldType -> unsupportedColumn("$path[]", type.elementType)
            else -> "$path (${type::class.simpleName})"
        }
}
