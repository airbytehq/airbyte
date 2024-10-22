/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3

enum class FileUploadFormat(val fileExtension: String) {
    AVRO("avro"),
    CSV("csv"),
    JSONL("jsonl"),
    PARQUET("parquet"),
}
