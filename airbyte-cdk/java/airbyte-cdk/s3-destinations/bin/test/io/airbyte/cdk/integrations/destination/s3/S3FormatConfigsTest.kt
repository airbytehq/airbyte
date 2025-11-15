/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import io.airbyte.cdk.integrations.destination.s3.UploadFormatConfigFactory.getUploadFormatConfig
import io.airbyte.cdk.integrations.destination.s3.csv.UploadCsvFormatConfig
import io.airbyte.cdk.integrations.destination.s3.util.CompressionType
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.commons.json.Jsons.jsonNode
import java.util.Map
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

// S3FormatConfigs
class S3FormatConfigsTest {
    @Test // When CSV format is specified, it returns CSV format config
    fun testGetCsvS3FormatConfig() {
        val configJson =
            jsonNode(
                Map.of(
                    "format",
                    jsonNode(
                        Map.of(
                            "format_type",
                            FileUploadFormat.CSV.toString(),
                            "flattening",
                            Flattening.ROOT_LEVEL.value,
                            "compression",
                            jsonNode(Map.of("compression_type", "No Compression"))
                        )
                    )
                )
            )

        val formatConfig = getUploadFormatConfig(configJson)
        Assertions.assertEquals(formatConfig.format, FileUploadFormat.CSV)
        Assertions.assertTrue(formatConfig is UploadCsvFormatConfig)
        val csvFormatConfig = formatConfig as UploadCsvFormatConfig
        Assertions.assertEquals(Flattening.ROOT_LEVEL, csvFormatConfig.flattening)
        Assertions.assertEquals(CompressionType.NO_COMPRESSION, csvFormatConfig.compressionType)
    }
}
