/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.io

/** Delta operations for data. */
enum class Operation {
    INSERT,
    UPDATE,
    DELETE,
}
