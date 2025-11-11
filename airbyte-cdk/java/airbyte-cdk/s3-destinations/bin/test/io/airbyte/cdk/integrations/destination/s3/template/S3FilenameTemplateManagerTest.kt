/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.template

import io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants
import java.io.IOException
import java.text.DateFormat
import java.text.SimpleDateFormat
import java.time.Instant
import java.util.TimeZone
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class S3FilenameTemplateManagerTest {

    private val s3FilenameTemplateManager = S3FilenameTemplateManager()

    @Test
    @Throws(IOException::class)
    internal fun testDatePlaceholder() {
        val fileNamePattern = "test-{date}"
        val fileExtension = "csv"
        val partId = "1"

        val actual: String =
            s3FilenameTemplateManager.applyPatternToFilename(
                S3FilenameTemplateParameterObject.builder()
                    .objectPath("")
                    .fileNamePattern(fileNamePattern)
                    .fileExtension(fileExtension)
                    .partId(partId)
                    .build(),
            )

        val defaultDateFormat: DateFormat =
            SimpleDateFormat(S3DestinationConstants.YYYY_MM_DD_FORMAT_STRING)
        defaultDateFormat.timeZone = TimeZone.getTimeZone("UTC")

        val currentTimeInMillis = Instant.now().toEpochMilli()

        val expected = "test-${defaultDateFormat.format(currentTimeInMillis)}"
        assertEquals(expected, actual)
    }

    @Test
    @Throws(IOException::class)
    internal fun testIfFilenameTemplateStringWasSanitized() {
        val fileNamePattern = "  te  st.csv  "
        val actual =
            s3FilenameTemplateManager.applyPatternToFilename(
                S3FilenameTemplateParameterObject.builder()
                    .objectPath("")
                    .fileNamePattern(fileNamePattern)
                    .fileExtension("csv")
                    .partId("1")
                    .build(),
            )

        assertEquals("te__st.csv", actual)
    }
}
