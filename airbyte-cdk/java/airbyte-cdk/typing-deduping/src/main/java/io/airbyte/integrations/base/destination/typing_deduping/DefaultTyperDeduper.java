/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static io.airbyte.cdk.integrations.base.IntegrationRunner.TYPE_AND_DEDUPE_THREAD_NAME;
import static io.airbyte.integrations.base.destination.typing_deduping.FutureUtils.countOfTypingDedupingThreads;
import static io.airbyte.integrations.base.destination.typing_deduping.FutureUtils.reduceExceptions;
import static java.util.Collections.singleton;

import com.google.common.collect.Streams;
import io.airbyte.cdk.integrations.destination.StreamSyncSummary;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.HashSet;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.concurrent.BasicThreadFactory;
import org.apache.commons.lang3.tuple.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * An abstraction over SqlGenerator and DestinationHandler. Destinations will still need to call
 * {@code new CatalogParser(new FooSqlGenerator()).parseCatalog()}, but should otherwise avoid
 * interacting directly with these classes.
 * <p>
 * In a typical sync, destinations should call the methods:
 * <ol>
 * <li>{@link #prepareTables()} once at the start of the sync</li>
 * <li>{@link #typeAndDedupe(String, String, boolean)} as needed throughout the sync</li>
 * <li>{@link #commitFinalTables()} once at the end of the sync</li>
 * </ol>
 * Note that #prepareTables() initializes some internal state. The other methods will throw an
 * exception if that method was not called.
 */
public class DefaultTyperDeduper<DialectTableDefinition> implements TyperDeduper {

  private static final Logger LOGGER = LoggerFactory.getLogger(TyperDeduper.class);

  private static final String NO_SUFFIX = "";
  private static final String TMP_OVERWRITE_TABLE_SUFFIX = "_airbyte_tmp";

  private final SqlGenerator<DialectTableDefinition> sqlGenerator;
  private final DestinationHandler<DialectTableDefinition> destinationHandler;

  private final DestinationV1V2Migrator<DialectTableDefinition> v1V2Migrator;
  private final V2TableMigrator v2TableMigrator;
  private final ParsedCatalog parsedCatalog;
  private Set<StreamId> overwriteStreamsWithTmpTable;
  private final Set<Pair<String, String>> streamsWithSuccessfulSetup;
  private final Map<StreamId, DestinationHandler.InitialRawTableState> initialRawTableStateByStream;
  // We only want to run a single instance of T+D per stream at a time. These objects are used for
  // synchronization per stream.
  // Use a read-write lock because we need the same semantics:
  // * any number of threads can insert to the raw tables at the same time, as long as T+D isn't
  // running (i.e. "read lock")
  // * T+D must run in complete isolation (i.e. "write lock")
  private final Map<StreamId, ReadWriteLock> tdLocks;
  // These locks are used to prevent multiple simultaneous attempts to T+D the same stream.
  // We use tryLock with these so that we don't queue up multiple T+D runs for the same stream.
  private final Map<StreamId, Lock> internalTdLocks;

  private final ExecutorService executorService;

  public DefaultTyperDeduper(final SqlGenerator<DialectTableDefinition> sqlGenerator,
                             final DestinationHandler<DialectTableDefinition> destinationHandler,
                             final ParsedCatalog parsedCatalog,
                             final DestinationV1V2Migrator<DialectTableDefinition> v1V2Migrator,
                             final V2TableMigrator v2TableMigrator,
                             final int defaultThreadCount) {
    this.sqlGenerator = sqlGenerator;
    this.destinationHandler = destinationHandler;
    this.parsedCatalog = parsedCatalog;
    this.v1V2Migrator = v1V2Migrator;
    this.v2TableMigrator = v2TableMigrator;
    this.initialRawTableStateByStream = new ConcurrentHashMap<>();
    this.streamsWithSuccessfulSetup = ConcurrentHashMap.newKeySet(parsedCatalog.streams().size());
    this.tdLocks = new ConcurrentHashMap<>();
    this.internalTdLocks = new ConcurrentHashMap<>();
    this.executorService = Executors.newFixedThreadPool(countOfTypingDedupingThreads(defaultThreadCount),
        new BasicThreadFactory.Builder().namingPattern(TYPE_AND_DEDUPE_THREAD_NAME).build());
  }

  public DefaultTyperDeduper(
                             final SqlGenerator<DialectTableDefinition> sqlGenerator,
                             final DestinationHandler<DialectTableDefinition> destinationHandler,
                             final ParsedCatalog parsedCatalog,
                             final DestinationV1V2Migrator<DialectTableDefinition> v1V2Migrator,
                             final int defaultThreadCount) {
    this(sqlGenerator, destinationHandler, parsedCatalog, v1V2Migrator, new NoopV2TableMigrator(), defaultThreadCount);
  }

  private void prepareSchemas(final ParsedCatalog parsedCatalog) throws Exception {
    final var rawSchema = parsedCatalog.streams().stream().map(stream -> stream.id().rawNamespace());
    final var finalSchema = parsedCatalog.streams().stream().map(stream -> stream.id().finalNamespace());
    final var createAllSchemasSql = Streams.concat(rawSchema, finalSchema)
        .filter(Objects::nonNull)
        .distinct()
        .map(sqlGenerator::createSchema)
        .toList();
    destinationHandler.execute(Sql.concat(createAllSchemasSql));
  }

  @Override
  public void prepareTables() throws Exception {
    if (overwriteStreamsWithTmpTable != null) {
      throw new IllegalStateException("Tables were already prepared.");
    }
    overwriteStreamsWithTmpTable = ConcurrentHashMap.newKeySet();
    LOGGER.info("Preparing tables");

    prepareSchemas(parsedCatalog);
    final Set<CompletableFuture<Optional<Exception>>> prepareTablesTasks = new HashSet<>();
    for (final StreamConfig stream : parsedCatalog.streams()) {
      prepareTablesTasks.add(prepareTablesFuture(stream));
    }
    CompletableFuture.allOf(prepareTablesTasks.toArray(CompletableFuture[]::new)).join();
    reduceExceptions(prepareTablesTasks, "The following exceptions were thrown attempting to prepare tables:\n");
  }

  private CompletableFuture<Optional<Exception>> prepareTablesFuture(final StreamConfig stream) {
    // For each stream, make sure that its corresponding final table exists.
    // Also, for OVERWRITE streams, decide if we're writing directly to the final table, or into an
    // _airbyte_tmp table.
    return CompletableFuture.supplyAsync(() -> {
      try {
        // Migrate the Raw Tables if this is the first v2 sync after a v1 sync
        v1V2Migrator.migrateIfNecessary(sqlGenerator, destinationHandler, stream);
        v2TableMigrator.migrateIfNecessary(stream);

        final Optional<DialectTableDefinition> existingTable = destinationHandler.findExistingTable(stream.id());
        if (existingTable.isPresent()) {
          LOGGER.info("Final Table exists for stream {}", stream.id().finalName());
          // The table already exists. Decide whether we're writing to it directly, or using a tmp table.
          if (stream.destinationSyncMode() == DestinationSyncMode.OVERWRITE) {
            if (!destinationHandler.isFinalTableEmpty(stream.id()) || !sqlGenerator.existingSchemaMatchesStreamConfig(stream, existingTable.get())) {
              // We want to overwrite an existing table. Write into a tmp table. We'll overwrite the table at the
              // end of the sync.
              overwriteStreamsWithTmpTable.add(stream.id());
              // overwrite an existing tmp table if needed.
              destinationHandler.execute(sqlGenerator.createTable(stream, TMP_OVERWRITE_TABLE_SUFFIX, true));
              LOGGER.info("Using temp final table for stream {}, will overwrite existing table at end of sync", stream.id().finalName());
            } else {
              LOGGER.info("Final Table for stream {} is empty and matches the expected v2 format, writing to table directly",
                  stream.id().finalName());
            }

          } else if (!sqlGenerator.existingSchemaMatchesStreamConfig(stream, existingTable.get())) {
            // We're loading data directly into the existing table. Make sure it has the right schema.
            TypeAndDedupeTransaction.executeSoftReset(sqlGenerator, destinationHandler, stream);
          }
        } else {
          LOGGER.info("Final Table does not exist for stream {}, creating.", stream.id().finalName());
          // The table doesn't exist. Create it. Don't force.
          destinationHandler.execute(sqlGenerator.createTable(stream, NO_SUFFIX, false));
        }
        final DestinationHandler.InitialRawTableState initialRawTableState = destinationHandler.getInitialRawTableState(stream.id());
        initialRawTableStateByStream.put(stream.id(), initialRawTableState);

        streamsWithSuccessfulSetup.add(Pair.of(stream.id().originalNamespace(), stream.id().originalName()));

        // Use fair locking. This slows down lock operations, but that performance hit is by far dwarfed
        // by our IO costs. This lock needs to be fair because the raw table writers are running almost
        // constantly,
        // and we don't want them to starve T+D.
        tdLocks.put(stream.id(), new ReentrantReadWriteLock(true));
        // This lock doesn't need to be fair; any T+D instance is equivalent and we'll skip T+D if we can't
        // immediately acquire the lock.
        internalTdLocks.put(stream.id(), new ReentrantLock());

        return Optional.empty();
      } catch (final Exception e) {
        LOGGER.error("Exception occurred while preparing tables for stream " + stream.id().originalName(), e);
        return Optional.of(e);
      }
    }, this.executorService);
  }

  public void typeAndDedupe(final String originalNamespace, final String originalName, final boolean mustRun) throws Exception {
    final var streamConfig = parsedCatalog.getStream(originalNamespace, originalName);
    final CompletableFuture<Optional<Exception>> task = typeAndDedupeTask(streamConfig, mustRun);
    reduceExceptions(
        singleton(task),
        String.format(
            "The Following Exceptions were thrown while typing and deduping %s.%s:\n",
            originalNamespace,
            originalName));
  }

  @Override
  public Lock getRawTableInsertLock(final String originalNamespace, final String originalName) {
    final var streamConfig = parsedCatalog.getStream(originalNamespace, originalName);
    return tdLocks.get(streamConfig.id()).readLock();
  }

  private boolean streamSetupSucceeded(final StreamConfig streamConfig) {
    final var originalNamespace = streamConfig.id().originalNamespace();
    final var originalName = streamConfig.id().originalName();
    if (!streamsWithSuccessfulSetup.contains(Pair.of(originalNamespace, originalName))) {
      // For example, if T+D setup fails, but the consumer tries to run T+D on all streams during close,
      // we should skip it.
      LOGGER.warn("Skipping typing and deduping for {}.{} because we could not set up the tables for this stream.", originalNamespace,
          originalName);
      return false;
    }
    return true;
  }

  public CompletableFuture<Optional<Exception>> typeAndDedupeTask(final StreamConfig streamConfig, final boolean mustRun) {
    return CompletableFuture.supplyAsync(() -> {
      final var originalNamespace = streamConfig.id().originalNamespace();
      final var originalName = streamConfig.id().originalName();
      try {
        if (!streamSetupSucceeded(streamConfig)) {
          return Optional.empty();
        }

        final boolean run;
        final Lock internalLock = internalTdLocks.get(streamConfig.id());
        if (mustRun) {
          // If we must run T+D, then wait until we acquire the lock.
          internalLock.lock();
          run = true;
        } else {
          // Otherwise, try and get the lock. If another thread already has it, then we should noop here.
          run = internalLock.tryLock();
        }

        if (run) {
          LOGGER.info("Waiting for raw table writes to pause for {}.{}", originalNamespace, originalName);
          final Lock externalLock = tdLocks.get(streamConfig.id()).writeLock();
          externalLock.lock();
          try {
            final DestinationHandler.InitialRawTableState initialRawTableState = initialRawTableStateByStream.get(streamConfig.id());
            TypeAndDedupeTransaction.executeTypeAndDedupe(
                sqlGenerator,
                destinationHandler,
                streamConfig,
                initialRawTableState.maxProcessedTimestamp(),
                getFinalTableSuffix(streamConfig.id()));
          } finally {
            LOGGER.info("Allowing other threads to proceed for {}.{}", originalNamespace, originalName);
            externalLock.unlock();
            internalLock.unlock();
          }
        } else {
          LOGGER.info("Another thread is already trying to run typing and deduping for {}.{}. Skipping it here.", originalNamespace,
              originalName);
        }
        return Optional.empty();
      } catch (final Exception e) {
        LOGGER.error("Exception occurred while typing and deduping stream " + originalName, e);
        return Optional.of(e);
      }
    }, this.executorService);
  }

  @Override
  public void typeAndDedupe(final Map<StreamDescriptor, StreamSyncSummary> streamSyncSummaries) throws Exception {
    LOGGER.info("Typing and deduping all tables");
    final Set<CompletableFuture<Optional<Exception>>> typeAndDedupeTasks = new HashSet<>();
    parsedCatalog.streams().stream()
        .filter(streamConfig -> {
          // Skip if stream setup failed.
          if (!streamSetupSucceeded(streamConfig)) {
            return false;
          }
          // Skip if we don't have any records for this stream.
          final StreamSyncSummary streamSyncSummary = streamSyncSummaries.getOrDefault(
              streamConfig.id().asStreamDescriptor(),
              StreamSyncSummary.DEFAULT);
          final boolean nonzeroRecords = streamSyncSummary.recordsWritten()
              .map(r -> r > 0)
              // If we didn't track record counts during the sync, assume we had nonzero records for this stream
              .orElse(true);
          final boolean unprocessedRecordsPreexist = initialRawTableStateByStream.get(streamConfig.id()).hasUnprocessedRecords();
          // If this sync emitted records, or the previous sync left behind some unprocessed records,
          // then the raw table has some unprocessed records right now.
          // Run T+D if either of those conditions are true.
          final boolean shouldRunTypingDeduping = nonzeroRecords || unprocessedRecordsPreexist;
          if (!shouldRunTypingDeduping) {
            LOGGER.info(
                "Skipping typing and deduping for stream {}.{} because it had no records during this sync and no unprocessed records from a previous sync.",
                streamConfig.id().originalNamespace(),
                streamConfig.id().originalName());
          }
          return shouldRunTypingDeduping;
        }).forEach(streamConfig -> typeAndDedupeTasks.add(typeAndDedupeTask(streamConfig, true)));
    CompletableFuture.allOf(typeAndDedupeTasks.toArray(CompletableFuture[]::new)).join();
    reduceExceptions(typeAndDedupeTasks, "The Following Exceptions were thrown while typing and deduping tables:\n");
  }

  /**
   * Does any "end of sync" work. For most streams, this is a noop.
   * <p>
   * For OVERWRITE streams where we're writing to a temp table, this is where we swap the temp table
   * into the final table.
   */
  @Override
  public void commitFinalTables() throws Exception {
    LOGGER.info("Committing final tables");
    final Set<CompletableFuture<Optional<Exception>>> tableCommitTasks = new HashSet<>();
    for (final StreamConfig streamConfig : parsedCatalog.streams()) {
      if (!streamsWithSuccessfulSetup.contains(Pair.of(streamConfig.id().originalNamespace(),
          streamConfig.id().originalName()))) {
        LOGGER.warn("Skipping committing final table for for {}.{} because we could not set up the tables for this stream.",
            streamConfig.id().originalNamespace(), streamConfig.id().originalName());
        continue;
      }
      if (DestinationSyncMode.OVERWRITE.equals(streamConfig.destinationSyncMode())) {
        tableCommitTasks.add(commitFinalTableTask(streamConfig));
      }
    }
    CompletableFuture.allOf(tableCommitTasks.toArray(CompletableFuture[]::new)).join();
    reduceExceptions(tableCommitTasks, "The Following Exceptions were thrown while committing final tables:\n");
  }

  private CompletableFuture<Optional<Exception>> commitFinalTableTask(final StreamConfig streamConfig) {
    return CompletableFuture.supplyAsync(() -> {
      final StreamId streamId = streamConfig.id();
      final String finalSuffix = getFinalTableSuffix(streamId);
      if (!StringUtils.isEmpty(finalSuffix)) {
        final Sql overwriteFinalTable = sqlGenerator.overwriteFinalTable(streamId, finalSuffix);
        LOGGER.info("Overwriting final table with tmp table for stream {}.{}", streamId.originalNamespace(), streamId.originalName());
        try {
          destinationHandler.execute(overwriteFinalTable);
        } catch (final Exception e) {
          LOGGER.error("Exception Occurred while committing final table for stream " + streamId.originalName(), e);
          return Optional.of(e);
        }
      }
      return Optional.empty();
    }, this.executorService);
  }

  private String getFinalTableSuffix(final StreamId streamId) {
    return overwriteStreamsWithTmpTable.contains(streamId) ? TMP_OVERWRITE_TABLE_SUFFIX : NO_SUFFIX;
  }

  @Override
  public void cleanup() {
    LOGGER.info("Cleaning Up type-and-dedupe thread pool");
    this.executorService.shutdown();
  }

}
