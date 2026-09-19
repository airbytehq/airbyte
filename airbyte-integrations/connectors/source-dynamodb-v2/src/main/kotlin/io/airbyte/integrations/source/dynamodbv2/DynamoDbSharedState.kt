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
 * SDK client is thread-safe and pools its HTTP connections), the CDK's resources, and the streams
 * that have been read to the end in this run.
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
) {
    private val clientDelegate: Lazy<DynamoDbClient> = lazy {
        DynamoDbClientFactory.create(configuration)
    }

    val client: DynamoDbClient by clientDelegate

    private val completedStreams: MutableSet<StreamIdentifier> = ConcurrentHashMap.newKeySet()

    /**
     * Records that the stream has been scanned to the end in this run, so that the next round of
     * partition creation for it produces no partition. The state value alone cannot tell a
     * completed incremental scan apart from the saved state of a previous sync.
     */
    fun markComplete(streamID: StreamIdentifier) {
        completedStreams.add(streamID)
    }

    fun isComplete(streamID: StreamIdentifier): Boolean = streamID in completedStreams

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
    }
}
