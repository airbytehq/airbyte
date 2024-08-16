package io.airbyte.cdk.write

import java.io.InputStream
import java.nio.charset.StandardCharsets
import kotlinx.coroutines.flow.asFlow

class InputStreamReader(
    private val inputStream: InputStream
) {
    /**
     * Push from the input stream until it's drained.
     */
    suspend fun run() {
        val queue = MessageQueue.instance
        inputStream.bufferedReader(StandardCharsets.UTF_8).use {
            it.lineSequence().asFlow().collect { line ->
                queue.publish(line)
            }
        }
    }
}
