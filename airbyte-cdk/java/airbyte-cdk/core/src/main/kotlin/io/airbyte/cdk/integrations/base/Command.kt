/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

enum class Command {
    SPEC,
    CHECK,
    DISCOVER,
    READ,
    WRITE
}
