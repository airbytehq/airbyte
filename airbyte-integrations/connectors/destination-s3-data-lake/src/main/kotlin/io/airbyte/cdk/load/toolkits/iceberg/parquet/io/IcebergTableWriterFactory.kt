/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.Overwrite
import jakarta.inject.Singleton
import java.util.UUID
import org.apache.iceberg.FileFormat
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties.DEFAULT_FILE_FORMAT
import org.apache.iceberg.TableProperties.DEFAULT_FILE_FORMAT_DEFAULT
import org.apache.iceberg.TableProperties.WRITE_TARGET_FILE_SIZE_BYTES
import org.apache.iceberg.TableProperties.WRITE_TARGET_FILE_SIZE_BYTES_DEFAULT
import org.apache.iceberg.data.GenericAppenderFactory
import org.apache.iceberg.data.Record
import org.apache.iceberg.io.BaseTaskWriter
import org.apache.iceberg.io.OutputFileFactory
import org.apache.iceberg.types.TypeUtil
import org.apache.iceberg.util.PropertyUtil

/**
 * Factory that creates Iceberg [BaseTaskWriter] instances to support writing records to Iceberg
 * data files. <p/> The factory takes into account whether partitioning is used on the target table
 * and whether primary keys are configured on the destination table's schema.
 */
@Singleton
class IcebergTableWriterFactory(private val icebergUtil: IcebergUtil) {
    /**
     * Creates a new [BaseTaskWriter] based on the configuration of the destination target [Table].
     *
     * @param table An Iceberg [Table]
     * @param generationId ID assigned to the data generation associated with the incoming data.
     * @param importType The [ImportType] of the sync job.
     * @return The [BaseTaskWriter] that writes records to the target [Table].
     */
    fun create(
        table: Table,
        generationId: String,
        importType: ImportType,
        schema: Schema
    ): BaseTaskWriter<Record> {
        icebergUtil.assertGenerationIdSuffixIsOfValidFormat(generationId)
        val format =
            FileFormat.valueOf(
                table
                    .properties()
                    .getOrDefault(DEFAULT_FILE_FORMAT, DEFAULT_FILE_FORMAT_DEFAULT)
                    .uppercase()
            )
        val identifierFieldIds = schema.identifierFieldIds()
        val appenderFactory =
            createAppenderFactory(
                table = table,
                schema = schema,
                identifierFieldIds = identifierFieldIds
            )
        val outputFileFactory =
            createOutputFileFactory(table = table, format = format, generationId = generationId)
        val targetFileSize =
            PropertyUtil.propertyAsLong(
                table.properties(),
                WRITE_TARGET_FILE_SIZE_BYTES,
                WRITE_TARGET_FILE_SIZE_BYTES_DEFAULT
            )
        return when (importType) {
            is Append,
            Overwrite ->
                newAppendWriter(
                    table = table,
                    schema = schema,
                    appenderFactory = appenderFactory,
                    targetFileSize = targetFileSize,
                    outputFileFactory = outputFileFactory,
                    format = format
                )
            is Dedupe ->
                newDeltaWriter(
                    table = table,
                    schema = schema,
                    identifierFieldIds = identifierFieldIds,
                    appenderFactory = appenderFactory,
                    targetFileSize = targetFileSize,
                    outputFileFactory = outputFileFactory,
                    format = format
                )
        }
    }

    private fun createAppenderFactory(
        table: Table,
        schema: Schema,
        identifierFieldIds: Set<Int>?
    ): GenericAppenderFactory {
        return GenericAppenderFactory(
                schema,
                table.spec(),
                identifierFieldIds?.toIntArray(),
                if (identifierFieldIds != null) TypeUtil.select(schema, identifierFieldIds.toSet())
                else null,
                null
            )
            .setAll(table.properties())
    }

    private fun createOutputFileFactory(
        table: Table,
        format: FileFormat,
        generationId: String
    ): OutputFileFactory {
        return OutputFileFactory.builderFor(table, 0, 1L)
            .defaultSpec(table.spec())
            .operationId(UUID.randomUUID().toString())
            .format(format)
            .suffix(generationId)
            .build()
    }

    private fun newAppendWriter(
        table: Table,
        schema: Schema,
        format: FileFormat,
        appenderFactory: GenericAppenderFactory,
        outputFileFactory: OutputFileFactory,
        targetFileSize: Long
    ): BaseTaskWriter<Record> {
        return if (table.spec().isUnpartitioned) {
            UnpartitionedAppendWriter(
                spec = table.spec(),
                format = format,
                appenderFactory = appenderFactory,
                outputFileFactory = outputFileFactory,
                io = table.io(),
                targetFileSize = targetFileSize
            )
        } else {
            PartitionedAppendWriter(
                spec = table.spec(),
                format = format,
                appenderFactory = appenderFactory,
                outputFileFactory = outputFileFactory,
                io = table.io(),
                targetFileSize = targetFileSize,
                schema = schema
            )
        }
    }

    private fun newDeltaWriter(
        table: Table,
        schema: Schema,
        format: FileFormat,
        appenderFactory: GenericAppenderFactory,
        outputFileFactory: OutputFileFactory,
        targetFileSize: Long,
        identifierFieldIds: Set<Int>
    ): BaseTaskWriter<Record> {
        return if (table.spec().isUnpartitioned) {
            UnpartitionedDeltaWriter(
                table,
                spec = table.spec(),
                format = format,
                appenderFactory = appenderFactory,
                outputFileFactory = outputFileFactory,
                io = table.io(),
                targetFileSize = targetFileSize,
                schema = schema,
                identifierFieldIds = identifierFieldIds
            )
        } else {
            PartitionedDeltaWriter(
                table,
                spec = table.spec(),
                format = format,
                appenderFactory = appenderFactory,
                outputFileFactory = outputFileFactory,
                io = table.io(),
                targetFileSize = targetFileSize,
                schema = schema,
                identifierFieldIds = identifierFieldIds
            )
        }
    }
}
