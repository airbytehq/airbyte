/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.staging

import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.csv.CsvSerializedBuffer
import io.airbyte.cdk.integrations.destination.s3.csv.StagingDatabaseCsvSheetGenerator

/**
 * Factory which can create an instance of concrete SerializedBuffer for one-time use before buffer
 * is closed. [io.airbyte.cdk.integrations.destination.s3.SerializedBufferFactory] is almost similar
 * which needs to be unified. That doesn't work well with our DV2 staging destinations, which mostly
 * support CSV only.
 */
object StagingSerializedBufferFactory {

    fun initializeBuffer(
        fileUploadFormat: FileUploadFormat,
        destinationColumns: JavaBaseConstants.DestinationColumns
    ): SerializableBuffer {
        when (fileUploadFormat) {
            FileUploadFormat.CSV -> {
                return CsvSerializedBuffer(
                    FileBuffer(CsvSerializedBuffer.CSV_GZ_SUFFIX),
                    StagingDatabaseCsvSheetGenerator(destinationColumns),
                    true,
                )
            }
            else -> {
                TODO("Only CSV is supported for Staging format")
            }
        }
    }
}
