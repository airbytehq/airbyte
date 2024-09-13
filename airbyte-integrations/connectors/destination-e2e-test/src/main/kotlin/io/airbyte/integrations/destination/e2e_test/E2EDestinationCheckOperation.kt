/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test

import io.airbyte.cdk.check.DestinationCheckOperation
import jakarta.inject.Singleton

@Singleton
class E2EDestinationCheckOperation() : DestinationCheckOperation<E2EDestinationConfiguration> {
    override fun check(config: E2EDestinationConfiguration) {
        // Do nothing
    }
}
