package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import com.clickhouse.data.ClickHouseFormat
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.integrations.destination.clickhouse_v2.log
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.io.ByteArrayOutputStream
import java.util.UUID
import org.apache.commons.io.IOUtils


class ClickhouseDirectLoader(private val clickhouseClient: Client) : DirectLoader {
    private var buffer: ByteArrayOutputStream = ByteArrayOutputStream()
    private var streamRecords: MutableList<AirbyteRecordMessage> = mutableListOf()
    private var recordCount = 0
    private var descriptor: DestinationStream.Descriptor? = null
    override fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        streamRecords.addLast(record.rawData.record)
        //record.rawData.record.meta.
        // Increment the record count
        recordCount++

        descriptor = record.stream.descriptor

         if (recordCount > 10000) {
             flush(descriptor)
             recordCount = 0
             streamRecords = mutableListOf()
             return DirectLoader.Complete
         }

        // log.error { record.rawData.record.data.toPrettyString() }
        // rely on the CDK to tell us when to finish()
        return DirectLoader.Incomplete
    }

    private fun flush(descriptor: DestinationStream.Descriptor?) {
        if (descriptor == null) {
            log.info { "No record to flush." }
            return
        }
        val records =
            streamRecords.map { message ->
                val record = message.data as ObjectNode
                record.put("_airbyte_raw_id", UUID.randomUUID().toString())
                record.put("_airbyte_extracted_at", System.currentTimeMillis())
                record.put("_airbyte_meta", "${message.meta.serializeToString()}")
                record.put("_airbyte_generation_id", 0L)
                //log.error { "Record: ${record.toPrettyString()}" }
                record
            }
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

    // only calls this on force complete
    override fun finish() {
        flush(descriptor)
    }

    // this is always called on complete
    override fun close() {
    }
}
