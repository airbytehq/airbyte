package io.airbyte.integrations.destination.clickhouse_v2

import com.clickhouse.client.api.Client
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

    @Singleton
    fun getClient(): Client {
        return Client.Builder()
            .addEndpoint("http://localhost:8123/default") // Example endpoint, replace with actual configuration
            .setUsername("Mon voisin")
            .setPassword("totoro") // Replace with actual password
            .build()
    }
}
