package io.airbyte.integrations.source.postgres.ctid;

import com.google.common.base.Preconditions;
import com.google.common.collect.AbstractIterator;
import io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.postgres.StreamingPostgresDatabase;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import org.apache.commons.lang3.tuple.Pair;
import org.jetbrains.annotations.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.util.*;
import java.util.concurrent.*;

import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;
import static io.airbyte.integrations.source.postgres.ctid.InitialSyncCtidIterator.ctidLegacyQueryPlan;
import static io.airbyte.integrations.source.postgres.ctid.InitialSyncCtidIterator.ctidQueryPlan;
import static io.airbyte.integrations.source.postgres.ctid.InitialSyncCtidIteratorConstants.*;
import static io.airbyte.integrations.source.postgres.ctid.InitialSyncCtidIteratorConstants.GIGABYTE;

public class CopyInitialSyncCtidIterator extends AbstractIterator<String> implements AutoCloseableIterator<String> {
    private static final Logger LOGGER = LoggerFactory.getLogger(CopyInitialSyncCtidIterator.class);
    private final ExecutorService executor;
    private boolean executorInitialized = false;
    private BlockingDeque<Future<String>> results;
    final Queue<Pair<Ctid, Ctid>> subQueriesPlan;
    boolean subQueriesInitialized = false;
    private final boolean useTestPageSize;
    private final CtidStateManager ctidStateManager;
    private Long lastKnownFileNode;
    private final boolean tidRangeScanCapableDBServer;
    private final AirbyteStreamNameNamespacePair airbyteStream;
    private final long tableSize;
    private final long blockSize;
    private final int maxTuple;
    private final List<String> columnNames;
    private final String quoteString;
    private final String schemaName;
    private final String tableName;
    private final StreamingPostgresDatabase database;
    private AutoCloseableIterator<String> currentIterator;

    public CopyInitialSyncCtidIterator(CtidStateManager ctidStateManager, StreamingPostgresDatabase database, CtidPostgresSourceOperations sourceOperations, String quoteString, List<String> columnNames, String schemaName, String tableName, long tableSize, long blockSize, int maxTuple, FileNodeHandler fileNodeHandler, boolean tidRangeScanCapableDBServer, boolean useTestPageSize, final ExecutorService executor) {
        this.ctidStateManager = ctidStateManager;
        this.tidRangeScanCapableDBServer = tidRangeScanCapableDBServer;
        this.airbyteStream = AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName);
        this.useTestPageSize = useTestPageSize;
        this.tableSize = tableSize;
        this.blockSize = blockSize;
        this.executor = executor;
        this.maxTuple = maxTuple;
        this.columnNames = columnNames;
        this.quoteString = quoteString;
        this.schemaName = schemaName;
        this.tableName = tableName;
        this.database = database;
        this.subQueriesPlan = new LinkedBlockingDeque<>();
    }

    @Nullable
    @Override
    protected String computeNext() {
        try {
            if (!subQueriesInitialized) {
                initSubQueries();
                subQueriesInitialized = true;
            }

            if (!executorInitialized) {
                initExecutor();
                executorInitialized = true;
            }

            if (currentIterator == null || !currentIterator.hasNext()) {
                do {
                    if (currentIterator != null) {
                        currentIterator.close();
                    }
                    if (results.isEmpty()) {
                        return endOfData();
                    }
                    final var currentResult = Optional.ofNullable(results.peek());
                    if (currentResult.isPresent()) {
                        results.pop();
                        final var filePath = currentResult.get().get();
                        assert(currentResult.get().isDone() && !currentResult.get().isCancelled());
                        final var binReader = new BinaryCopyFileReaderRecordIterator(filePath);
                        currentIterator = AutoCloseableIterators.fromIterator(binReader, binReader::close, null);
                    } else {
                        throw new RuntimeException("no chunk file");
                    }
                } while (!currentIterator.hasNext());
            }
            return currentIterator.next();
        } catch (final Exception e) {
            throw new RuntimeException(e);
        }
    }

    private void initExecutor() {
        results = new LinkedBlockingDeque<>();
        subQueriesPlan.stream()
                .map(p -> new Callable<String>() {
                    private Pair<Ctid, Ctid> pair;

                    public Callable<String> init(Pair<Ctid, Ctid> pair) {
                        this.pair = pair;
                        return this;
                    }

                    @Override
                    public String call() throws Exception {
                        final var query = getCopyQuery(getCtidQuery(pair.getLeft(), pair.getRight()));
                        LOGGER.info("*** pair {}-{}: {}", pair.getLeft(), pair.getRight(), query);
                        final File chunkFile = File.createTempFile("abc", null);
                        final FileOutputStream fileOutputStream = new FileOutputStream(chunkFile);
                        final BufferedOutputStream bufferedOutputStream = new BufferedOutputStream(fileOutputStream);
                        LOGGER.info("*** writing to {}", chunkFile.getAbsolutePath());
                        try {
                            database.bulkCopyOut(query, bufferedOutputStream);
                        } catch (final Exception e) {
                            throw new RuntimeException(e);
                        }
                        bufferedOutputStream.close();
                        chunkFile.toPath().toFile().deleteOnExit();
                        return chunkFile.getAbsolutePath();
                    }
                }.init(p))
                .forEachOrdered(c -> results.add(executor.submit(c)));
    }

    @Override
    public void close() throws Exception {
        executor.shutdown();
    }

    void initSubQueries() {
        if (useTestPageSize) {
            LOGGER.warn("Using test page size");
        }
        final CtidStatus currentCtidStatus = ctidStateManager.getCtidStatus(airbyteStream);
        subQueriesPlan.clear();

        subQueriesPlan.addAll(getQueryPlan(currentCtidStatus));
        lastKnownFileNode = currentCtidStatus != null ? currentCtidStatus.getRelationFilenode() : null;
    }

    private List<Pair<Ctid, Ctid>> getQueryPlan(final CtidStatus currentCtidStatus) {
        final List<Pair<Ctid, Ctid>> queryPlan = tidRangeScanCapableDBServer
                ? ctidQueryPlan((currentCtidStatus == null) ? Ctid.ZERO : Ctid.of(currentCtidStatus.getCtid()),
                tableSize, blockSize, QUERY_TARGET_SIZE_GB, useTestPageSize ? EIGHT_KB : GIGABYTE)
                : ctidLegacyQueryPlan((currentCtidStatus == null) ? Ctid.ZERO : Ctid.of(currentCtidStatus.getCtid()),
                tableSize, blockSize, QUERY_TARGET_SIZE_GB, useTestPageSize ? EIGHT_KB : GIGABYTE, maxTuple);
        return queryPlan;
    }

    private String getCtidQuery(final Ctid lowerBound,
                                               final Ctid upperBound) {
        final String ctidStatement = tidRangeScanCapableDBServer ? createCtidQuery(lowerBound, upperBound)
                : createCtidLegacyQuery(lowerBound, upperBound);
        return ctidStatement;
    }

    public String createCtidQuery(final Ctid lowerBound, final Ctid upperBound) {
        LOGGER.info("Preparing query for table: {}", tableName);
        final String fullTableName = getFullyQualifiedTableNameWithQuoting(schemaName, tableName,
                quoteString);
        if (upperBound != null) {
            final String sql = "SELECT %s FROM %s WHERE ctid > '%s'::tid AND ctid <= '%s'::tid"
                    .formatted(generetaFormat(), fullTableName, lowerBound.toString(), upperBound.toString());

            LOGGER.info("Executing query for table {}: {} with bindings {} and {}", tableName, sql, lowerBound, upperBound);
            return sql;
        } else {
            final String sql = "SELECT %s FROM %s WHERE ctid > '%s'::tid"
                    .formatted(generetaFormat(), fullTableName, lowerBound.toString());

            LOGGER.info("Executing query for table {}: {} with binding {}", tableName, sql, lowerBound);
            return sql;
        }
    }

    private String generetaFormat() {
        StringBuilder sb = new StringBuilder();
        List<String> left = new ArrayList<>();
        List<String> right = new ArrayList<>();
        sb.append("format('{");
        columnNames.stream().forEachOrdered(c -> {
            left.add("\"%s\":\"%%s\"".formatted(c));
            right.add(c);
        });
        sb.append(String.join(",", left));
        sb.append("}',");
        sb.append(String.join(",", right));
        sb.append(")");
        return sb.toString();
    }

    public String createCtidLegacyQuery(final Ctid lowerBound,
                                                            final Ctid upperBound) {
        Preconditions.checkArgument(lowerBound != null, "Lower bound ctid expected");
        Preconditions.checkArgument(upperBound != null, "Upper bound ctid expected");
        LOGGER.info("Preparing query for table: {}", tableName);
        final String fullTableName = getFullyQualifiedTableNameWithQuoting(schemaName, tableName,
                quoteString);
        final String wrappedColumnNames = RelationalDbQueryUtils.enquoteIdentifierList(columnNames, quoteString);
        final String sql =
                "SELECT %s FROM %s WHERE ctid = ANY (ARRAY (SELECT FORMAT('(%%s,%%s)', page, tuple)::tid tid_addr FROM generate_series(%d, %d) as page, generate_series(%d,%d) as tuple ORDER BY tid_addr))"
                        .formatted(
                                wrappedColumnNames, fullTableName,
                                lowerBound.page, upperBound.page,
                                lowerBound.tuple, upperBound.tuple);
        LOGGER.info("Executing query for table {}: {}", tableName, sql);

        return sql;
    }

    private String getCopyQuery(final String query) {
        StringBuilder builder = new StringBuilder();
        builder.append("COPY (")
                .append(query)
                .append(") to STDOUT (format binary)");
        return builder.toString();

    }
}
