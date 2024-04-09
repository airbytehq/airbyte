/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import io.airbyte.cdk.integrations.destination.s3.S3FormatConfigs.getS3FormatConfig
import io.airbyte.cdk.integrations.destination.s3.csv.S3CsvFormatConfig
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
                            S3Format.CSV.toString(),
                            "flattening",
                            Flattening.ROOT_LEVEL.value,
                            "compression",
                            jsonNode(Map.of("compression_type", "No Compression"))
                        )
                    )
                )
            )

        val formatConfig = getS3FormatConfig(configJson)
        Assertions.assertEquals(formatConfig.format, S3Format.CSV)
        Assertions.assertTrue(formatConfig is S3CsvFormatConfig)
        val csvFormatConfig = formatConfig as S3CsvFormatConfig
        Assertions.assertEquals(Flattening.ROOT_LEVEL, csvFormatConfig.flattening)
        Assertions.assertEquals(CompressionType.NO_COMPRESSION, csvFormatConfig.compressionType)
    }
}
