/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

enum class Command {
    SPEC,
    CHECK,
    DISCOVER,
    READ,
    WRITE
}
