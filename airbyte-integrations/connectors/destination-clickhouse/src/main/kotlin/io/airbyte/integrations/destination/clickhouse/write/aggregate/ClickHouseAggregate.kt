package io.airbyte.integrations.destination.clickhouse.write.aggregate

import io.airbyte.cdk.load.dataflow.Aggregate
import io.airbyte.cdk.load.dataflow.AggregateFactory
import io.airbyte.cdk.load.dataflow.StoreKey
import io.airbyte.cdk.load.dataflow.state.StateHistogram
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

class ClickHouseAggregate: Aggregate {
    private var count = 0L

    private val log = KotlinLogging.logger {}

    override fun accept(fields: RecordDTO): Aggregate.Status {
        count += 1

        log.info { "Count = $count" }

        return if (count < 1000) {
            Aggregate.Status.INCOMPLETE
        } else {
            Aggregate.Status.COMPLETE
        }
    }

    override fun getStateHistogram(): StateHistogram {
        return StateHistogram()
    }

    override suspend fun flush() {
        log.info { "flushing" }
    }

    override fun size(): Int {
        return 10
    }
}

@Singleton
class ClickHouseAggregateFactory: AggregateFactory {
    override fun create(key: StoreKey): Aggregate {
        return ClickHouseAggregate()
    }
}
