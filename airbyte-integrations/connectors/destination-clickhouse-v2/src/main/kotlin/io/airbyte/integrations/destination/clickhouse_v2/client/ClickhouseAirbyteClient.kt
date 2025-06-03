package io.airbyte.integrations.destination.clickhouse_v2.client

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.data_formats.ClickHouseBinaryFormatReader
import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

val log = KotlinLogging.logger {  }

@Singleton
class ClickhouseAirbyteClient(private val client: Client): AirbyteClient() {
    override fun getNumberOfRecordsInTable(database: String, table: String): Long {
        try {
            val response = client.query("SELECT count(1) cnt FROM $database.$table;").get()
            val reader: ClickHouseBinaryFormatReader = client.newBinaryFormatReader(response)
            reader.next()
            val count = reader.getLong("cnt")
            return count
        } catch (e: Exception) {
            // TODO: That's sus
            log.error { "Error while getting number of records in table $database.$table: ${e.message}" }
            log.info { "Table: $database.$table doesn't exist, return 0 record." }
            return 0L
        }
    }
}
