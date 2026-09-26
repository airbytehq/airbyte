/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.ResourceType
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.annotation.PreDestroy
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import software.amazon.awssdk.services.dynamodb.DynamoDbClient

private val log = KotlinLogging.logger {}

/**
 * State shared by all partitions of a READ: the configuration, the one [DynamoDbClient] (the AWS
 * SDK client is thread-safe and pools its HTTP connections), the CDK's resources, the scan progress
 * of every table ([DynamoDbTableScan]) and the streams that have been read to the end in this run.
 */
@Singleton
class DynamoDbSharedState
@Inject
constructor(
    val configuration: DynamoDbSourceConfiguration,
    val concurrencyResource: ConcurrencyResource,
    val resourceAcquirer: ResourceAcquirer,
    /**
     * Maximum number of items per `Scan` page (DynamoDB `Limit`); 0 or less for the service default
     * of one 1 MB page. Smaller pages bound the memory used per page and make the checkpoints
     * finer, at the cost of more requests.
     */
    @Value("\${$SCAN_PAGE_LIMIT_PROPERTY:0}") val scanPageLimit: Int = 0,
    /**
     * Table bytes per parallel-scan segment: a table is split into `ceil(size / this)` segments
     * (see [DynamoDbTableScan.segmentCount]). Tables smaller than this are scanned as one segment.
     */
    @Value("\${$SEGMENT_TARGET_BYTES_PROPERTY:$DEFAULT_SEGMENT_TARGET_BYTES}")
    val segmentTargetBytes: Long = DEFAULT_SEGMENT_TARGET_BYTES,
    /** Upper bound on the segments of one table; every segment adds a key to the stream state. */
    @Value("\${$MAX_SEGMENTS_PROPERTY:$DEFAULT_MAX_SEGMENTS}")
    val maxSegments: Int = DEFAULT_MAX_SEGMENTS,
) {
    private val clientDelegate: Lazy<DynamoDbClient> = lazy {
        DynamoDbClientFactory.create(configuration)
    }

    val client: DynamoDbClient by clientDelegate

    private val completedStreams: MutableSet<StreamIdentifier> = ConcurrentHashMap.newKeySet()

    private val tableScans: MutableMap<StreamIdentifier, DynamoDbTableScan> = ConcurrentHashMap()

    /**
     * Records that the stream has been scanned to the end in this run, so that the next round of
     * partition creation for it produces no partition. The state value alone cannot tell a
     * completed incremental scan apart from the saved state of a previous sync.
     */
    fun markComplete(streamID: StreamIdentifier) {
        completedStreams.add(streamID)
    }

    fun isComplete(streamID: StreamIdentifier): Boolean = streamID in completedStreams

    /** The scan progress of a table, created by [create] on its first round of this READ. */
    fun tableScan(streamID: StreamIdentifier, create: () -> DynamoDbTableScan): DynamoDbTableScan =
        tableScans.computeIfAbsent(streamID) { create() }

    fun tryAcquireReaderResources(
        resourceTypes: List<ResourceType>,
    ): Map<ResourceType, Resource.Acquired>? = resourceAcquirer.tryAcquire(resourceTypes)

    @PreDestroy
    fun close() {
        if (clientDelegate.isInitialized()) {
            log.info { "Closing the DynamoDB client" }
            client.close()
        }
    }

    companion object {
        const val SCAN_PAGE_LIMIT_PROPERTY = "airbyte.connector.extract.dynamodb.scan-page-limit"
        const val SEGMENT_TARGET_BYTES_PROPERTY =
            "airbyte.connector.extract.dynamodb.segment-target-bytes"
        const val MAX_SEGMENTS_PROPERTY = "airbyte.connector.extract.dynamodb.max-segments"

        /** 64 MiB: the measured 10x speed-up on a 1 GB table used 16 segments. */
        const val DEFAULT_SEGMENT_TARGET_BYTES: Long = 64L * 1024 * 1024
        const val DEFAULT_MAX_SEGMENTS: Int = 128
    }
}
