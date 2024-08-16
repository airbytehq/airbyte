package io.airbyte.cdk.write

/**
 * Dummy catalog for protoyping
 */
class DummyCatalog {
    val streams: List<Stream> = listOf(
        Stream("stream1"),
        Stream("stream2")
    )
}
