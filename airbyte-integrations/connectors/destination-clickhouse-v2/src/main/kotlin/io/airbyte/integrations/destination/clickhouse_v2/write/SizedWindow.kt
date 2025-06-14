package io.airbyte.integrations.destination.clickhouse_v2.write

class SizedWindow(private val size: Long) {
    private var accumulated = 0L

    fun increment(quantity: Long): SizedWindow = this.apply { accumulated += quantity }

    fun isComplete(): Boolean = accumulated >= size
}
