/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.check

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration

class SnowflakeChecker : DestinationChecker<SnowflakeConfiguration> {
    override fun check(config: SnowflakeConfiguration) {
        TODO("Not yet implemented")
    }
}
