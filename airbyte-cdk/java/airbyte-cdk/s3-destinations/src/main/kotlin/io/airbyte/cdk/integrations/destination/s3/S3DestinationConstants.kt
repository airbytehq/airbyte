/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3

import io.airbyte.cdk.integrations.destination.s3.util.CompressionType
import io.airbyte.cdk.integrations.destination.s3.util.S3NameTransformer

class S3DestinationConstants {

    companion object {
        const val YYYY_MM_DD_FORMAT_STRING: String = "yyyy_MM_dd"
        @JvmField val NAME_TRANSFORMER: S3NameTransformer = S3NameTransformer()
        const val DEFAULT_PATH_FORMAT: String =
            "\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}_\${MONTH}_\${DAY}_\${EPOCH}_"

        // gzip compression for CSV and JSONL
        const val COMPRESSION_ARG_NAME: String = "compression"
        const val COMPRESSION_TYPE_ARG_NAME: String = "compression_type"
        @JvmField val DEFAULT_COMPRESSION_TYPE: CompressionType = CompressionType.GZIP

        // Flattening for CSV and JSONL
        const val FLATTENING_ARG_NAME: String = "flattening"
    }
}
