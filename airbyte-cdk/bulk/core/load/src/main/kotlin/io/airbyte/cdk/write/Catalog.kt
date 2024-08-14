package io.airbyte.cdk.write

/**
 * Dummy catalog for protoyping
 */
class Catalog {
    val streams: List<Stream> = listOf(
        Stream("stream1"),
        Stream("stream2")
    )
}
