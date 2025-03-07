/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.check.DestinationChecker
import javax.inject.Singleton

@Singleton
class BigqueryChecker : DestinationChecker<BigqueryConfiguration> {
    override fun check(config: BigqueryConfiguration) {
        // Do nothing
    }
}
