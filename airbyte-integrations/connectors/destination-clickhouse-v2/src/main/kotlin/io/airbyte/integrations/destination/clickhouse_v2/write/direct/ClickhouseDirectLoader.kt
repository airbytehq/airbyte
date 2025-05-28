package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import com.clickhouse.data.ClickHouseFormat
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.integrations.destination.clickhouse_v2.log
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.InputStream
import org.apache.commons.io.IOUtils


class ClickhouseDirectLoader(private val clickhouseClient: Client) : DirectLoader {
    private var buffer: ByteArrayOutputStream = ByteArrayOutputStream()
    private var recordsPerStream: MutableMap<DestinationStream.Descriptor, MutableList<JsonNode>> = mutableMapOf()
    private var recordCount = 0

    override fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
         val streamRecords: MutableList<JsonNode> = recordsPerStream.getOrDefault(record.stream.descriptor, mutableListOf())
         streamRecords.addLast(record.rawData.record.data)
        recordsPerStream[record.stream.descriptor] = streamRecords

        // Increment the record count
        recordCount++

         if (recordCount > 10000) {
             flush()
             recordCount = 0
             recordsPerStream = mutableMapOf()
             return DirectLoader.Incomplete
         }

        log.error { record.rawData.record.data.toPrettyString() }
        // rely on the CDK to tell us when to finish()
        return DirectLoader.Incomplete
    }

    private fun flush() {
        recordsPerStream.forEach { (descriptor, records) ->
            val inputStream = IOUtils.toInputStream(
                records.joinToString(separator = "\n") { it.toString() },
                Charsets.UTF_8
            )
            val insertResult = clickhouseClient.insert(
                "${descriptor.name}",
                inputStream,
                ClickHouseFormat.JSONEachRow
            ).get()

            log.error { "Inserted ${insertResult.writtenRows} rows into ${descriptor.name}" }
        }
    }

    // only calls this on force complete
    override fun finish() {
        flush()

        log.error { "Finish" }
    }

    // this is always called on complete
    override fun close() {
        flush()
        clickhouseClient.close()
        log.error { "Close" }
    }
}
