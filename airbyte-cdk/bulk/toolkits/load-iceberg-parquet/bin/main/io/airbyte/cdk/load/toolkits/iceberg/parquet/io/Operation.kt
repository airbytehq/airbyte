/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

/** Delta operations for data. */
enum class Operation {
    INSERT,
    UPDATE,
    DELETE,
}
