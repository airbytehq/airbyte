/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.util

enum class CompressionType(val fileExtension: String) {
    NO_COMPRESSION(""),
    GZIP(".gz")
}
