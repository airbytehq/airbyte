/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.sql.Connection
import javax.sql.DataSource

@Factory
class SnowflakeBeansFactory {
    @Singleton fun getConfig(config: DestinationConfiguration) = config as SnowflakeConfiguration

    @Singleton
    fun getSnowflakeClient(snowflakeClient: AirbyteSnowflakeClient): Connection {
        return snowflakeClient.getConnection()
    }
}
