/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.config

/**
 * Configuration interface for dataflow socket settings.
 *
 * Destination connectors using the dataflow CDK can implement this interface to override the
 * default socket behavior. If no bean implementing this interface is provided, the CDK will use all
 * sockets provided by the platform.
 *
 * Example usage in a destination connector:
 * ```kotlin
 * @Singleton
 * class MyDestinationSocketConfig : DataFlowSocketConfig {
 *     override val numSockets: Int = 4
 * }
 * ```
 */
interface DataFlowSocketConfig {
    /**
     * The number of sockets this connector wants to use. If the platform provides more sockets than
     * this value, only this many sockets will be used (taking the first N from the provided list).
     * If the platform provides fewer sockets than this value, all provided sockets will be used.
     */
    val numSockets: Int
}
