/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2.io

/** Delta operations for data. */
enum class Operation {
    INSERT,
    UPDATE,
    DELETE,
}
