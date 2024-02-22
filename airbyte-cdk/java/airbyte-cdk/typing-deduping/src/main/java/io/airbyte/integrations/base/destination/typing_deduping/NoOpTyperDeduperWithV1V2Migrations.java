/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static io.airbyte.cdk.integrations.base.IntegrationRunner.TYPE_AND_DEDUPE_THREAD_NAME;
import static io.airbyte.integrations.base.destination.typing_deduping.FutureUtils.getCountOfTypeAndDedupeThreads;
import static io.airbyte.integrations.base.destination.typing_deduping.FutureUtils.reduceExceptions;
import static io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtilKt.prepareAllSchemas;

import io.airbyte.cdk.integrations.destination.StreamSyncSummary;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.HashSet;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.locks.Lock;
import kotlin.NotImplementedError;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.NotImplementedException;
import org.apache.commons.lang3.concurrent.BasicThreadFactory;

/**
 * This is a NoOp implementation which skips and Typing and Deduping operations and does not emit
 * the final tables. However, this implementation still performs V1->V2 migrations and V2
 * json->string migrations in the raw tables.
 */
@Slf4j
public class NoOpTyperDeduperWithV1V2Migrations<DialectTableDefinition> implements TyperDeduper {

  private final DestinationV1V2Migrator<DialectTableDefinition> v1V2Migrator;
  private final V2TableMigrator v2TableMigrator;
  private final ExecutorService executorService;
  private final ParsedCatalog parsedCatalog;
  private final SqlGenerator<DialectTableDefinition> sqlGenerator;
  private final DestinationHandler<DialectTableDefinition> destinationHandler;

  public NoOpTyperDeduperWithV1V2Migrations(final SqlGenerator<DialectTableDefinition> sqlGenerator,
                                            final DestinationHandler<DialectTableDefinition> destinationHandler,
                                            final ParsedCatalog parsedCatalog,
                                            final DestinationV1V2Migrator<DialectTableDefinition> v1V2Migrator,
                                            final V2TableMigrator v2TableMigrator) {
    this.sqlGenerator = sqlGenerator;
    this.destinationHandler = destinationHandler;
    this.parsedCatalog = parsedCatalog;
    this.v1V2Migrator = v1V2Migrator;
    this.v2TableMigrator = v2TableMigrator;
    this.executorService = Executors.newFixedThreadPool(getCountOfTypeAndDedupeThreads(),
        new BasicThreadFactory.Builder().namingPattern(TYPE_AND_DEDUPE_THREAD_NAME).build());
  }

  @Override
  public void prepareTables() throws Exception {
    try {
      log.info("Ensuring schemas exist for prepareTables with V1V2 migrations");
      prepareAllSchemas(parsedCatalog, sqlGenerator, destinationHandler);
      final Set<CompletableFuture<Optional<Exception>>> prepareTablesTasks = new HashSet<>();
      for (final StreamConfig stream : parsedCatalog.streams()) {
        prepareTablesTasks.add(CompletableFuture.supplyAsync(() -> {
          // Migrate the Raw Tables if this is the first v2 sync after a v1 sync
          try {
            log.info("Migrating V1->V2 for stream {}", stream.id());
            v1V2Migrator.migrateIfNecessary(sqlGenerator, destinationHandler, stream);
            log.info("Migrating V2 legacy for stream {}", stream.id());
            v2TableMigrator.migrateIfNecessary(stream);
            return Optional.empty();
          } catch (final Exception e) {
            return Optional.of(e);
          }
        }, executorService));
      }
      CompletableFuture.allOf(prepareTablesTasks.toArray(CompletableFuture[]::new)).join();
      reduceExceptions(prepareTablesTasks, "The following exceptions were thrown attempting to prepare tables:\n");
    } catch (NotImplementedError | NotImplementedException e) {
      log.warn(
          "Could not prepare schemas or tables because this is not implemented for this destination, this should not be required for this destination to succeed");
    }
  }

  @Override
  public void typeAndDedupe(final String originalNamespace, final String originalName, final boolean mustRun) {
    log.info("Skipping TypeAndDedupe");
  }

  @Override
  public Lock getRawTableInsertLock(final String originalNamespace, final String originalName) {
    return new NoOpRawTableTDLock();
  }

  @Override
  public void typeAndDedupe(final Map<StreamDescriptor, StreamSyncSummary> streamSyncSummaries) {
    log.info("Skipping TypeAndDedupe final");
  }

  @Override
  public void commitFinalTables() {
    log.info("Skipping commitFinalTables final");
  }

  @Override
  public void cleanup() {
    log.info("Cleaning Up type-and-dedupe thread pool");
    this.executorService.shutdown();
  }

}
