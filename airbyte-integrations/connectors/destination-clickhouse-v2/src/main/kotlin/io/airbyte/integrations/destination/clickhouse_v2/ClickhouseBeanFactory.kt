package io.airbyte.integrations.destination.clickhouse_v2

import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.integrations.destination.clickhouse_v2.write.ClickhouseWriter
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class ClickhouseBeanFactory {
    @Singleton
    fun getWriter(): DestinationWriter {
        return ClickhouseWriter()
    }
}
