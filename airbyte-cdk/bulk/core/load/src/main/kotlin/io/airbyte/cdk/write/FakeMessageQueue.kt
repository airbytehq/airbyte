package io.airbyte.cdk.write

/**
 * Just for prototyping. It emits a fixed number of records per stream,
 * with a fixed frequency of state (not yet implemented), and switches
 * between the streams randomly per `shuffledness`.
 */
class FakeMessageQueue(
    catalog: Catalog,
    private val sizePerStream: Int,
    private val stateFrequency: Int,
    private val shuffledness: Double
) {
    private val streams = catalog.streams.map { it }.toMutableList()
    private var currentStream = catalog.streams[0]
    private val emittedPerStream = mutableMapOf<Stream, Int>()

    fun take(stream: Stream): List<DestinationRecord> {
        // randomly switch streams if rand() < shuffledness
        if (Math.random() < shuffledness) {
            if (streams.isEmpty()) {
                return emptyList()
            }
            currentStream = streams.random()
        }

        if (currentStream != stream) {
            return emptyList()
        }

        val currentIndex = emittedPerStream.getOrDefault(currentStream, 0)
        emittedPerStream[currentStream] = currentIndex + 1

        if (currentIndex % stateFrequency == 0) {
            return emptyList()
        }

        return listOf(DestinationRecord("$stream: $currentIndex"))
    }

    fun streamComplete(stream: Stream): Boolean {
        return emittedPerStream.getOrDefault(stream, 0) >= sizePerStream
    }
}
