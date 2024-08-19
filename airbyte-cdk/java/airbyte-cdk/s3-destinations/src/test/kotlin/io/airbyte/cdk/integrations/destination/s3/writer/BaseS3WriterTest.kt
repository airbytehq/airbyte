/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.writer

import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.template.S3FilenameTemplateParameterObject.Companion.builder
import io.airbyte.cdk.integrations.destination.s3.writer.BaseS3Writer.Companion.determineOutputFilename
import java.io.IOException
import java.sql.Timestamp
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class BaseS3WriterTest {
    @Test
    @Throws(IOException::class)
    fun testGetOutputFilename() {
        val timestamp = Timestamp(1471461319000L)
        Assertions.assertEquals(
            "2016_08_17_1471461319000_0.csv",
            determineOutputFilename(
                builder().s3Format(FileUploadFormat.CSV).timestamp(timestamp).build()
            )
        )
    }
}
