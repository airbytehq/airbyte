/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.parquet

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.UploadFormatConfig
import java.util.*
import org.apache.parquet.hadoop.metadata.CompressionCodecName

class UploadParquetFormatConfig(formatConfig: JsonNode) : UploadFormatConfig {
    val compressionCodec: CompressionCodecName
    val blockSize: Int
    val maxPaddingSize: Int
    val pageSize: Int
    val dictionaryPageSize: Int
    val isDictionaryEncoding: Boolean
    override val fileExtension: String = PARQUET_SUFFIX

    init {
        val blockSizeMb: Int =
            UploadFormatConfig.withDefault(
                formatConfig,
                "block_size_mb",
                ParquetConstants.DEFAULT_BLOCK_SIZE_MB
            )
        val maxPaddingSizeMb: Int =
            UploadFormatConfig.withDefault(
                formatConfig,
                "max_padding_size_mb",
                ParquetConstants.DEFAULT_MAX_PADDING_SIZE_MB
            )
        val pageSizeKb: Int =
            UploadFormatConfig.withDefault(
                formatConfig,
                "page_size_kb",
                ParquetConstants.DEFAULT_PAGE_SIZE_KB
            )
        val dictionaryPageSizeKb: Int =
            UploadFormatConfig.withDefault(
                formatConfig,
                "dictionary_page_size_kb",
                ParquetConstants.DEFAULT_DICTIONARY_PAGE_SIZE_KB
            )

        this.compressionCodec =
            CompressionCodecName.valueOf(
                UploadFormatConfig.withDefault(
                        formatConfig,
                        "compression_codec",
                        ParquetConstants.DEFAULT_COMPRESSION_CODEC.name
                    )
                    .uppercase(Locale.getDefault())
            )
        this.blockSize = blockSizeMb * 1024 * 1024
        this.maxPaddingSize = maxPaddingSizeMb * 1024 * 1024
        this.pageSize = pageSizeKb * 1024
        this.dictionaryPageSize = dictionaryPageSizeKb * 1024
        this.isDictionaryEncoding =
            UploadFormatConfig.withDefault(
                formatConfig,
                "dictionary_encoding",
                ParquetConstants.DEFAULT_DICTIONARY_ENCODING
            )
    }

    override val format: FileUploadFormat
        get() = FileUploadFormat.PARQUET

    override fun toString(): String {
        return "UploadParquetFormatConfig{" +
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
