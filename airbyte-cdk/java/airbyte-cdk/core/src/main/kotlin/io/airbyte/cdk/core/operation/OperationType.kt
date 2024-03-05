/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation

/**
 * Defines the operations that may be invoked via the CLI arguments. Not all connectors will
 * implement all of these operations.
 */
enum class OperationType(val requiresCatalog: Boolean, val requiresConfiguration: Boolean, ) {
    SPEC(requiresCatalog = false, requiresConfiguration = false,),
    CHECK(requiresCatalog = false, requiresConfiguration = true),
    DISCOVER(requiresCatalog = false, requiresConfiguration = true),
    READ(requiresCatalog = true, requiresConfiguration = true),
    WRITE(requiresCatalog = true, requiresConfiguration = true),
}
