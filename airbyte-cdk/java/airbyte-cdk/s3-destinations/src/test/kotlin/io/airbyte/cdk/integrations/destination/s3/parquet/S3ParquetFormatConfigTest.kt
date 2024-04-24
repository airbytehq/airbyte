/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.parquet

import io.airbyte.commons.json.Jsons.deserialize
import org.apache.parquet.hadoop.metadata.CompressionCodecName
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class S3ParquetFormatConfigTest {
    @Test
    fun testConfigConstruction() {
        val formatConfig =
            deserialize(
                "{\n" +
                    "\t\"compression_codec\": \"GZIP\",\n" +
                    "\t\"block_size_mb\": 1,\n" +
                    "\t\"max_padding_size_mb\": 1,\n" +
                    "\t\"page_size_kb\": 1,\n" +
                    "\t\"dictionary_page_size_kb\": 1,\n" +
                    "\t\"dictionary_encoding\": false\n" +
                    "}"
            )

        val config = UploadParquetFormatConfig(formatConfig)

        // The constructor should automatically convert MB or KB to bytes.
        Assertions.assertEquals(1024 * 1024, config.blockSize)
        Assertions.assertEquals(1024 * 1024, config.maxPaddingSize)
        Assertions.assertEquals(1024, config.pageSize)
        Assertions.assertEquals(1024, config.dictionaryPageSize)

        Assertions.assertEquals(CompressionCodecName.GZIP, config.compressionCodec)
        Assertions.assertFalse(config.isDictionaryEncoding)
    }
}
