/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.config.properties

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.micronaut.core.util.StringUtils

class S3ConnectorOutputFormat private constructor(
    @JsonProperty("format_type") val formatType: String?,
    @JsonProperty("flattening") val flattening: String?,
    val compression: S3Compression?,
    @JsonProperty("compression_codec") val compressionCodec: S3CompressionCodec?,
    @JsonProperty("block_size_mb") val blockSizeMb: Int?,
    @JsonProperty("max_padding_size_mb") val maxPaddingSizeMb: Int?,
    @JsonProperty("page_size_kb") val pageSizeKb: Int?,
    @JsonProperty("dictionary_page_size_kb") val dictionaryPageSizeKb: Int?,
    @JsonProperty("dictionary_encoding") val dictionaryEncoding: Boolean?,
) {
    data class Builder(
        var formatType: String? = null,
        var flattening: String? = null,
        var compression: S3Compression? = null,
        var compressionCodec: S3CompressionCodec? = null,
        var blockSizeMb: Int? = null,
        var maxPaddingSizeMb: Int? = null,
        var pageSizeKb: Int? = null,
        var dictionaryPageSizeKb: Int? = null,
        var dictionaryEncoding: Boolean? = null,
    ) {
        fun withBlockSizeMb(blockSizeMb: Int) = apply { this.blockSizeMb = blockSizeMb }

        fun withCompression(compression: Map<String, String>) = apply { this.compression = S3Compression(compression) }

        fun withCompressionCodec(compressionCodec: Map<String, Any>) =
            apply {
                this.compressionCodec =
                    S3CompressionCodec(
                        compressionCodec,
                    )
            }

        fun withDictionaryEncoding(dictionaryEncoding: Boolean) = apply { this.dictionaryEncoding = dictionaryEncoding }

        fun withDictionaryPageSizeKb(dictionaryPageSizeKb: Int) = apply { this.dictionaryPageSizeKb = dictionaryPageSizeKb }

        fun withFlattening(flattening: String) = apply { this.flattening = flattening }

        fun withFormatType(formatType: String) = apply { this.formatType = formatType }

        fun withMaxPaddingSizeMb(maxPaddingSizeMb: Int) = apply { this.maxPaddingSizeMb = maxPaddingSizeMb }

        fun withPageSizeKb(pageSizeKb: Int) = apply { this.pageSizeKb = pageSizeKb }

        fun build() =
            S3ConnectorOutputFormat(
                formatType = formatType, flattening = flattening, compression = compression, compressionCodec = compressionCodec,
                blockSizeMb = blockSizeMb, maxPaddingSizeMb = maxPaddingSizeMb, pageSizeKb = pageSizeKb,
                dictionaryPageSizeKb = dictionaryPageSizeKb, dictionaryEncoding = dictionaryEncoding,
            )
    }

    fun getFlattening(): Flattening {
        return if(StringUtils.isNotEmpty(flattening)) {
            Flattening.fromValue(flattening!!)
        } else {
            Flattening.NO
        }
    }
}
