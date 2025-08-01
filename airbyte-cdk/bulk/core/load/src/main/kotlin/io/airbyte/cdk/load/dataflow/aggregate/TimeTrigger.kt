package io.airbyte.cdk.load.dataflow.aggregate

/*
 * Encapsulates basic sized windowing logic. As we implement other windowing,
 * we should look to break out a shared interface.
 */
class TimeTrigger(
    private val size: Long,
) {
    private var timestamp = 0L

    fun update(value: Long): TimeTrigger = this.apply { timestamp = value }

    fun watermark() = timestamp

    fun isComplete(now: Long): Boolean = now - timestamp >= size
}
