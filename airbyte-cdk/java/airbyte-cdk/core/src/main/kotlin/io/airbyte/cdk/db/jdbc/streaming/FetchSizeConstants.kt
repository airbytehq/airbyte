/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc.streaming

object FetchSizeConstants {
    // The desired buffer size in memory to store the fetched rows.
    // This size is not enforced. It is only used to calculate a proper
    // fetch size. The max row size the connector can handle is actually
    // limited by the heap size.
    const val TARGET_BUFFER_SIZE_RATIO: Double = 0.6
    const val MIN_BUFFER_BYTE_SIZE: Long = 250L * 1024L * 1024L // 250 MB

    // sample size for making the first estimation of the row size
    const val INITIAL_SAMPLE_SIZE: Int = 10

    // sample every N rows during the post-initial stage
    const val SAMPLE_FREQUENCY: Int = 100

    const val MIN_FETCH_SIZE: Int = 1
    const val DEFAULT_FETCH_SIZE: Int = 1000
    const val MAX_FETCH_SIZE: Int = 1000000000
}
