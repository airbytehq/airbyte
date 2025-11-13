package io.airbyte.integrations.destination.mysql_v2

import io.airbyte.cdk.AirbyteDestinationRunner

/**
 * Main entry point for the MySQL v2 destination connector.
 *
 * This is a modern CDK-based connector that supports all sync modes:
 * - Append (incremental sync without deduplication)
 * - Dedupe (incremental sync with primary key deduplication)
 * - Overwrite (full refresh)
 *
 * The connector uses the Dataflow CDK framework which handles:
 * - Message parsing and transformation
 * - State management
 * - Stream lifecycle orchestration
 * - Automatic schema evolution
 */
fun main(args: Array<String>) {
    AirbyteDestinationRunner.run(*args)
}
