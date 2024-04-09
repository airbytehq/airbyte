/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.parquet

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.S3Format
import io.airbyte.cdk.integrations.destination.s3.S3FormatConfig
import java.util.*
import org.apache.parquet.hadoop.metadata.CompressionCodecName

class S3ParquetFormatConfig(formatConfig: JsonNode) : S3FormatConfig {
    @JvmField val compressionCodec: CompressionCodecName
    @JvmField val blockSize: Int
    @JvmField val maxPaddingSize: Int
    @JvmField val pageSize: Int
    @JvmField val dictionaryPageSize: Int
    val isDictionaryEncoding: Boolean
    override val fileExtension: String = PARQUET_SUFFIX

    init {
        val blockSizeMb: Int =
            S3FormatConfig.Companion.withDefault(
                formatConfig,
                "block_size_mb",
                S3ParquetConstants.DEFAULT_BLOCK_SIZE_MB
            )
        val maxPaddingSizeMb: Int =
            S3FormatConfig.Companion.withDefault(
                formatConfig,
                "max_padding_size_mb",
                S3ParquetConstants.DEFAULT_MAX_PADDING_SIZE_MB
            )
        val pageSizeKb: Int =
            S3FormatConfig.Companion.withDefault(
                formatConfig,
                "page_size_kb",
                S3ParquetConstants.DEFAULT_PAGE_SIZE_KB
            )
        val dictionaryPageSizeKb: Int =
            S3FormatConfig.Companion.withDefault(
                formatConfig,
                "dictionary_page_size_kb",
                S3ParquetConstants.DEFAULT_DICTIONARY_PAGE_SIZE_KB
            )

        this.compressionCodec =
            CompressionCodecName.valueOf(
                S3FormatConfig.Companion.withDefault(
                        formatConfig,
                        "compression_codec",
                        S3ParquetConstants.DEFAULT_COMPRESSION_CODEC.name
                    )
                    .uppercase(Locale.getDefault())
            )
        this.blockSize = blockSizeMb * 1024 * 1024
        this.maxPaddingSize = maxPaddingSizeMb * 1024 * 1024
        this.pageSize = pageSizeKb * 1024
        this.dictionaryPageSize = dictionaryPageSizeKb * 1024
        this.isDictionaryEncoding =
            S3FormatConfig.Companion.withDefault(
                formatConfig,
                "dictionary_encoding",
                S3ParquetConstants.DEFAULT_DICTIONARY_ENCODING
            )
    }

    override val format: S3Format
        get() = S3Format.PARQUET

    override fun toString(): String {
        return "S3ParquetFormatConfig{" +
            "compressionCodec=" +
            compressionCodec +
            ", " +
            "blockSize=" +
            blockSize +
            ", " +
            "maxPaddingSize=" +
            maxPaddingSize +
            ", " +
            "pageSize=" +
            pageSize +
            ", " +
            "dictionaryPageSize=" +
            dictionaryPageSize +
            ", " +
            "dictionaryEncoding=" +
            isDictionaryEncoding +
            ", " +
            '}'
    }

    companion object {
        @JvmField val PARQUET_SUFFIX: String = ".parquet"
    }
}
