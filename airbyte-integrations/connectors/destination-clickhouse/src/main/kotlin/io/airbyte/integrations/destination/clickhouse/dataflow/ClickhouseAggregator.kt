package io.airbyte.integrations.destination.clickhouse.dataflow

import com.clickhouse.client.api.Client
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.dataflow.Aggregate
import io.airbyte.cdk.load.dataflow.AggregateFactory
import io.airbyte.cdk.load.dataflow.StoreKey
import io.airbyte.cdk.load.dataflow.state.StateHistogram
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.clickhouse.write.load.BinaryRowInsertBuffer
import io.airbyte.integrations.destination.clickhouse.write.load.ClickhouseDirectLoader
import io.airbyte.integrations.destination.clickhouse.write.load.SizedWindow
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

class ClickhouseAggregate(
    @VisibleForTesting val buffer: BinaryRowInsertBuffer,
) : Aggregate {
    private val log = KotlinLogging.logger {}

    private val stateHistogram: StateHistogram = StateHistogram()

    private var recordCountWindow =
        SizedWindow(150)
    // the sum of serialized json bytes we'''ve accumulated
    private var bytesWindow = SizedWindow(ClickhouseDirectLoader.Constants.MAX_BATCH_SIZE_BYTES)

    override fun accept(fields: RecordDTO): Aggregate.Status {
        log.info { "Accumulate" }
        buffer.accumulate(fields.fields)

        recordCountWindow.increment(1)
        bytesWindow.increment(fields.sizeBytes)

        return Aggregate.Status.INCOMPLETE
    }

    override suspend fun flush() {
        log.info { "Flush" }
        buffer.flush()
        buffer.reset()
    }

    override fun getStateHistogram(): StateHistogram = stateHistogram

    // TODO: Decide if we want to push the aggregator wit the most records or the most bytes
    override fun size(): Int = buffer.numRecords
}

@Factory
class ClickhouseAggregateFactory(private val clickhouseClient: Client,): AggregateFactory {
    override fun create(key: StoreKey): Aggregate {
        val tableName = TableName(name = key.name, namespace = key.namespace ?: "default")
        val binaryRowInsertBuffer = BinaryRowInsertBuffer(
            tableName,
            clickhouseClient
        )

        return ClickhouseAggregate(binaryRowInsertBuffer)
    }
}
