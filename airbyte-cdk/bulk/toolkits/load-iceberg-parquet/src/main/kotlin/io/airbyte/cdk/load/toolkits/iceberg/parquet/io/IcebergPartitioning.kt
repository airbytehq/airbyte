/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.expressions.Expressions
import org.apache.iceberg.transforms.Transforms

private val logger = KotlinLogging.logger {}

enum class IcebergPartitionTransform {
    IDENTITY,
    YEAR,
    MONTH,
    DAY,
    HOUR,
    BUCKET,
    TRUNCATE,
}

data class IcebergPartitionField(
    val sourceColumn: String,
    val transform: IcebergPartitionTransform,
    val argument: Int? = null,
)

object IcebergPartitioning {
    /** Builds a partition spec against [schema], skipping fields that cannot be bound. */
    fun buildSpec(schema: Schema, fields: List<IcebergPartitionField>): PartitionSpec {
        val builder = PartitionSpec.builderFor(schema)
        val included = mutableSetOf<Pair<Int, String>>()
        fields.forEach { field ->
            val source = schema.findField(field.sourceColumn)
            if (source == null) {
                logger.warn {
                    "Skipping partition field for missing column '${field.sourceColumn}'."
                }
                return@forEach
            }
            if (!canTransform(field, source.type())) {
                logger.warn {
                    "Skipping partition field '${field.sourceColumn}' with transform " +
                        "${field.transform}: it cannot bind to ${source.type()}."
                }
                return@forEach
            }
            val transformName = transformName(field)
            if (!included.add(source.fieldId() to transformName)) {
                return@forEach
            }
            addField(builder, field)
        }
        return builder.build()
    }

    /** Adds declared fields that are missing from the table's current partition spec. */
    fun evolveSpec(table: Table, fields: List<IcebergPartitionField>): Boolean {
        val schema = table.schema()
        val currentFields =
            table.spec().fields().mapTo(mutableSetOf()) {
                it.sourceId() to it.transform().toString()
            }
        val update = table.updateSpec()
        var changed = false
        fields.forEach { field ->
            val source = schema.findField(field.sourceColumn)
            if (source == null) {
                logger.warn {
                    "Skipping partition field for missing table column '${field.sourceColumn}'."
                }
                return@forEach
            }
            if (!canTransform(field, source.type())) {
                logger.warn {
                    "Skipping partition field '${field.sourceColumn}' with transform " +
                        "${field.transform}: it cannot bind to ${source.type()}."
                }
                return@forEach
            }
            val key = source.fieldId() to transformName(field)
            if (key in currentFields) {
                return@forEach
            }
            currentFields.add(key)
            addField(update, field)
            changed = true
        }
        if (changed) {
            update.commit()
        }
        return changed
    }

    private fun canTransform(
        field: IcebergPartitionField,
        sourceType: org.apache.iceberg.types.Type,
    ) =
        when (field.transform) {
            IcebergPartitionTransform.IDENTITY ->
                Transforms.identity<Any?>().canTransform(sourceType)
            IcebergPartitionTransform.YEAR -> Transforms.year<Any?>().canTransform(sourceType)
            IcebergPartitionTransform.MONTH -> Transforms.month<Any?>().canTransform(sourceType)
            IcebergPartitionTransform.DAY -> Transforms.day<Any?>().canTransform(sourceType)
            IcebergPartitionTransform.HOUR -> Transforms.hour<Any?>().canTransform(sourceType)
            IcebergPartitionTransform.BUCKET ->
                Transforms.bucket<Any?>(requireArgument(field)).canTransform(sourceType)
            IcebergPartitionTransform.TRUNCATE ->
                Transforms.truncate<Any?>(requireArgument(field)).canTransform(sourceType)
        }

    private fun transformName(field: IcebergPartitionField): String =
        when (field.transform) {
            IcebergPartitionTransform.IDENTITY -> "identity"
            IcebergPartitionTransform.YEAR -> "year"
            IcebergPartitionTransform.MONTH -> "month"
            IcebergPartitionTransform.DAY -> "day"
            IcebergPartitionTransform.HOUR -> "hour"
            IcebergPartitionTransform.BUCKET -> "bucket[${requireArgument(field)}]"
            IcebergPartitionTransform.TRUNCATE -> "truncate[${requireArgument(field)}]"
        }

    private fun requireArgument(field: IcebergPartitionField): Int =
        requireNotNull(field.argument) {
                "${field.transform} partitioning requires an argument."
            }
            .also {
                require(it >= 1) { "${field.transform} partition argument must be at least 1." }
            }

    private fun addField(
        builder: PartitionSpec.Builder,
        field: IcebergPartitionField,
    ) {
        when (field.transform) {
            IcebergPartitionTransform.IDENTITY -> builder.identity(field.sourceColumn)
            IcebergPartitionTransform.YEAR -> builder.year(field.sourceColumn)
            IcebergPartitionTransform.MONTH -> builder.month(field.sourceColumn)
            IcebergPartitionTransform.DAY -> builder.day(field.sourceColumn)
            IcebergPartitionTransform.HOUR -> builder.hour(field.sourceColumn)
            IcebergPartitionTransform.BUCKET ->
                builder.bucket(field.sourceColumn, requireArgument(field))
            IcebergPartitionTransform.TRUNCATE ->
                builder.truncate(field.sourceColumn, requireArgument(field))
        }
    }

    private fun addField(
        update: org.apache.iceberg.UpdatePartitionSpec,
        field: IcebergPartitionField,
    ) {
        val expression =
            when (field.transform) {
                IcebergPartitionTransform.IDENTITY -> Expressions.ref<Any?>(field.sourceColumn)
                IcebergPartitionTransform.YEAR -> Expressions.year<Any?>(field.sourceColumn)
                IcebergPartitionTransform.MONTH -> Expressions.month<Any?>(field.sourceColumn)
                IcebergPartitionTransform.DAY -> Expressions.day<Any?>(field.sourceColumn)
                IcebergPartitionTransform.HOUR -> Expressions.hour<Any?>(field.sourceColumn)
                IcebergPartitionTransform.BUCKET ->
                    Expressions.bucket<Any?>(field.sourceColumn, requireArgument(field))
                IcebergPartitionTransform.TRUNCATE ->
                    Expressions.truncate<Any?>(field.sourceColumn, requireArgument(field))
            }
        update.addField(expression)
    }
}
