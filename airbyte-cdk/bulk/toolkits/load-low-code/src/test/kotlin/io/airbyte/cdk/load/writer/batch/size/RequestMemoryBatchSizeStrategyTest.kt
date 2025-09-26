package io.airbyte.cdk.load.writer.batch.size

import io.airbyte.cdk.load.writer.batch.size.memory.RequestMemoryBatchSizeStrategy
import io.airbyte.cdk.util.Jsons
import kotlin.test.assertFalse
import org.junit.jupiter.api.Test

class RequestMemoryBatchSizeStrategyTest {

    companion object {
        val RESPONSE_OF_10_BYTES = Jsons.readTree("""{"key": 1}""")
    }

    @Test
    internal fun `test given limit not reached when isFull then return false`() {
        val batchSizeStrategy = RequestMemoryBatchSizeStrategy(RESPONSE_OF_10_BYTES, 11)
        assertFalse { batchSizeStrategy.isFull() }
    }

    @Test
    internal fun `test given limit is reached when isFull then return true`() {
        val batchSizeStrategy = RequestMemoryBatchSizeStrategy(RESPONSE_OF_10_BYTES, 9)
        assertFalse { batchSizeStrategy.isFull() }
    }
}
