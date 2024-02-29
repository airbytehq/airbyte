package io.airbyte.integrations.base.destination.typing_deduping

import com.google.common.collect.Streams
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil.getResultsOrLogAndThrowFirst
import io.airbyte.commons.concurrency.CompletableFutures
import java.util.*
import java.util.concurrent.CompletableFuture
import java.util.concurrent.CompletionStage
import java.util.concurrent.ExecutorService


class TyperDeduperUtil {
  companion object {

    @JvmStatic
    fun executeRawTableMigrations(
        executorService: ExecutorService,
        sqlGenerator: SqlGenerator,
        destinationHandler: DestinationHandler,
        v1V2Migrator: DestinationV1V2Migrator,
        v2TableMigrator: V2TableMigrator,
        parsedCatalog: ParsedCatalog
    ) {
      // TODO: Either the migrations run the soft reset and create v2 tables or the actual prepare tables.
      // unify the logic
      // with current state of raw tables & final tables. This is done first before gather initial state
      // to avoid recreating
      // final tables later again.
      val runMigrationsResult =
          CompletableFutures.allOf(parsedCatalog.streams().stream()
              .map { streamConfig -> runMigrationsAsync(executorService, sqlGenerator, destinationHandler, v1V2Migrator, v2TableMigrator, streamConfig) }
              .toList()).toCompletableFuture().join()
      getResultsOrLogAndThrowFirst("The following exceptions were thrown attempting to run migrations:\n", runMigrationsResult)
    }

    /**
     * Extracts all the "raw" and "final" schemas identified in the [parsedCatalog] and ensures they
     * exist in the Destination Database.
     */
    @JvmStatic
    fun prepareSchemas(
        sqlGenerator: SqlGenerator,
        destinationHandler: DestinationHandler,
        parsedCatalog: ParsedCatalog) {
      val rawSchema = parsedCatalog.streams.stream().map { it.id.rawNamespace }
      val finalSchema = parsedCatalog.streams.stream().map { it.id.finalNamespace }
      val createAllSchemasSql = Streams.concat<String>(rawSchema, finalSchema)
          .filter(Objects::nonNull)
          .distinct()
          .map(sqlGenerator::createSchema)
          .toList()
      destinationHandler.execute(Sql.concat(createAllSchemasSql))
    }

    private fun runMigrationsAsync(
        executorService: ExecutorService,
        sqlGenerator: SqlGenerator,
        destinationHandler: DestinationHandler,
        v1V2Migrator: DestinationV1V2Migrator,
        v2TableMigrator: V2TableMigrator,
        streamConfig: StreamConfig): CompletionStage<Void> {
      return CompletableFuture.runAsync({
        try {
          v1V2Migrator.migrateIfNecessary(sqlGenerator, destinationHandler, streamConfig)
          v2TableMigrator.migrateIfNecessary(streamConfig)
        } catch (e: java.lang.Exception) {
          throw RuntimeException(e)
        }
      }, executorService)
    }
  }
}
