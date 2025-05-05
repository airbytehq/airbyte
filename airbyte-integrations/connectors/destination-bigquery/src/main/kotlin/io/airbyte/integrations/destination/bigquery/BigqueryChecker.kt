/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import javax.inject.Singleton

@Singleton
class BigqueryChecker : DestinationChecker<BigqueryConfiguration> {
    override fun check(config: BigqueryConfiguration) {
        // TODO implement a real checker in the CDK; kill this class
    }
}
