/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer
import io.airbyte.cdk.integrations.destination.s3.csv.CsvSerializedBuffer
import io.airbyte.cdk.integrations.destination.s3.csv.StagingDatabaseCsvSheetGenerator
import io.airbyte.cdk.integrations.destination.staging.StagingOperations
import io.airbyte.commons.json.Jsons.jsonNode
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.util.Map

abstract class SnowflakeSqlStagingOperations : SnowflakeSqlOperations(), StagingOperations {
    /**
     * This method is used in Check connection method to make sure that user has the Write
     * permission
     */
    @Suppress("deprecation")
    @Throws(Exception::class)
    internal fun attemptWriteToStage(
        outputSchema: String?,
        stageName: String,
        database: JdbcDatabase?
    ) {
        val csvSerializedBuffer =
            CsvSerializedBuffer(
                FileBuffer(CsvSerializedBuffer.CSV_GZ_SUFFIX),
                StagingDatabaseCsvSheetGenerator(
                    JavaBaseConstants.DestinationColumns.V2_WITHOUT_META
                ),
                true
            )

        // create a dummy stream\records that will bed used to test uploading
        csvSerializedBuffer.accept(
            AirbyteRecordMessage()
                .withData(jsonNode(Map.of("testKey", "testValue")))
                .withEmittedAt(System.currentTimeMillis())
        )
        csvSerializedBuffer.flush()

        uploadRecordsToStage(
            database,
            csvSerializedBuffer,
            outputSchema,
            stageName,
            if (stageName.endsWith("/")) stageName else "$stageName/"
        )
    }
}
