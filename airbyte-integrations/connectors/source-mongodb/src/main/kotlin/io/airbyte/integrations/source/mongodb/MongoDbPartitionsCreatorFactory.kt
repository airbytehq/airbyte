/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import com.mongodb.client.MongoClient
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.Global
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.PartitionsCreatorFactorySupplier
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

/**
 * Factory for creating [MongoDbPartitionsCreator] instances.
 *
 * This is the DI entry point that the CDK calls during read operations.
 * It creates a shared MongoDB client and produces partition creators
 * for each stream in the catalog.
 *
 * MongoDB does not use the JDBC toolkit, so this implements the core
 * [PartitionsCreatorFactory] interface directly.
 */
@Singleton
class MongoDbPartitionsCreatorFactory(
    private val config: MongoDbSourceConfiguration,
    private val concurrencyResource: ConcurrencyResource,
) : PartitionsCreatorFactory {

    /** Shared MongoDB client for all partition creators. */
    private val mongoClient: MongoClient by lazy {
        config.createMongoClient()
    }

    override fun make(feedBootstrap: FeedBootstrap<*>): PartitionsCreator? {
        // MongoDB does not support global (CDC) feeds yet
        if (feedBootstrap.feed is Global) {
            log.warn { "MongoDB does not support CDC/Global feeds yet." }
            return null
        }

        val streamBootstrap = feedBootstrap as? StreamFeedBootstrap
            ?: return null

        log.info { "Creating partitions creator for stream: ${streamBootstrap.feed.label}" }

        return MongoDbPartitionsCreator(
            mongoClient = mongoClient,
            config = config,
            feedBootstrap = streamBootstrap,
            concurrencyResource = concurrencyResource,
        )
    }
}

/**
 * Supplier to register the [MongoDbPartitionsCreatorFactory] with the CDK.
 *
 * The CDK uses this supplier pattern to discover available partition creator
 * factories via Micronaut DI.
 */
@Singleton
class MongoDbPartitionsCreatorFactorySupplier(
    private val factory: MongoDbPartitionsCreatorFactory,
) : PartitionsCreatorFactorySupplier<MongoDbPartitionsCreatorFactory> {
    override fun get(): MongoDbPartitionsCreatorFactory = factory
}
