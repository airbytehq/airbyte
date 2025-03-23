/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

class QueueCapacityCalculator(
    val numProducers: Int,
    val numConsumers: Int,
    val availableResourceAmount: Long,
    val expectedUsagePerMessageAmount: Long
) {
    val numUnits: Int = numProducers + numConsumers * 2
    val maxMessageSize = availableResourceAmount / numUnits
    val clampedMessageSize = maxMessageSize.coerceAtMost(expectedUsagePerMessageAmount)
    val totalQueueCapacity: Int = (numUnits - (numProducers + numConsumers))
    // Our earlier calculations should ensure this is always at least 1, but
    // we'll clamp it to be safe.
    val queuePartitionCapacity: Int = (totalQueueCapacity / numConsumers).coerceAtLeast(1)
}
