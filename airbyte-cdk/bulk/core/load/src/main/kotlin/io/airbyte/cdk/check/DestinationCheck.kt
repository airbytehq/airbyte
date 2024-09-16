/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.check

interface DestinationCheck {
    fun check()
    fun cleanup() {}
}
