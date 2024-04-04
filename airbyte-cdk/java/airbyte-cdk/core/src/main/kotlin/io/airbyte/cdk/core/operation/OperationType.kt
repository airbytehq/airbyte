/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation

/**
 * Defines the operations that may be invoked via the CLI arguments.  Not all connectors will
 * implement all of these operations.
 */
enum class OperationType {
    SPEC,
    CHECK,
    DISCOVER,
    READ,
    WRITE,
}
