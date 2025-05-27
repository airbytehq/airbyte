package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import com.clickhouse.data.ClickHouseFormat
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.integrations.destination.clickhouse_v2.log
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.InputStream

// this is an aggregate window — it is in-charge of uploading itself
class ClickhouseDirectLoader(private val clickhouseClient: Client) : DirectLoader {
    private var buffer: ByteArrayOutputStream = ByteArrayOutputStream()

    override fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
//         val byteArray = "${record.rawData.record.data}\n".toByteArray()
//
//         buffer.write(byteArray)
//         if (buffer!!.size() > 15 * 1024 * 1024) {
//             val inputStream: InputStream = ByteArrayInputStream(buffer.toByteArray())
//             clickhouseClient.insert("test", inputStream, ClickHouseFormat.JSONEachRow)
//             return DirectLoader.Incomplete
//         }

        log.error { record.rawData.record.data.toPrettyString() }
        // rely on the CDK to tell us when to finish()
        return DirectLoader.Incomplete
    }

    // only calls this on force complete
    override fun finish() {
        log.error { "Finish" }
    }

    // this is always called on complete
    override fun close() {
        log.error { "Close" }
    }
}
