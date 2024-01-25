package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.protocol.models.v0.StreamDescriptor
import org.apache.commons.lang3.concurrent.BasicThreadFactory
import org.slf4j.Logger
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.locks.Lock

class NoMigrationNoFinalTableTyperDeduper<DialectTableDefinition>(
    private val sqlGenerator: SqlGenerator<DialectTableDefinition>,
    private val destinationHandler: DestinationHandler<DialectTableDefinition>,
    private val parsedCatalog: ParsedCatalog,
    ): TyperDeduper {

    private val executorService: ExecutorService = Executors.newFixedThreadPool(
        FutureUtils.countOfTypingDedupingThreads(8),
        BasicThreadFactory.Builder().namingPattern(IntegrationRunner.TYPE_AND_DEDUPE_THREAD_NAME)
            .build()
    );

    private val logger: Logger by logger()


    override fun prepareTables() {
        prepareAllSchemas(parsedCatalog, sqlGenerator, destinationHandler)
    }

    override fun typeAndDedupe(
        originalNamespace: String?,
        originalName: String?,
        mustRun: Boolean
    ) {
        logger.info("Destination Does not support Typing and Deduping, Skipping")
    }

    override fun getRawTableInsertLock(originalNamespace: String?, originalName: String?): Lock {
        return NoOpRawTableTDLock();
    }

    override fun typeAndDedupe(streamSyncSummaries: MutableMap<StreamDescriptor, StreamSyncSummary>?) {
        logger.info("Destination Does not support Typing and Deduping, Skipping 'typeAndDedupe'")
    }

    override fun commitFinalTables() {
        logger.info("Destination does not support final tables, Skipping 'commitFinalTables'")
    }

    override fun cleanup() {
        logger.info("Shutting down type and dedupe threads")
        executorService.shutdown()
    }
}
