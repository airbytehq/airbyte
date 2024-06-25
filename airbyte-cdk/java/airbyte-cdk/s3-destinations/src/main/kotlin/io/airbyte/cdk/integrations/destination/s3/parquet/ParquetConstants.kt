/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.parquet

import org.apache.parquet.hadoop.metadata.CompressionCodecName

class ParquetConstants {

    companion object {
        val DEFAULT_COMPRESSION_CODEC: CompressionCodecName = CompressionCodecName.UNCOMPRESSED
        const val DEFAULT_BLOCK_SIZE_MB: Int = 128
        const val DEFAULT_MAX_PADDING_SIZE_MB: Int = 8
        const val DEFAULT_PAGE_SIZE_KB: Int = 1024
        const val DEFAULT_DICTIONARY_PAGE_SIZE_KB: Int = 1024
        const val DEFAULT_DICTIONARY_ENCODING: Boolean = true
    }
}
