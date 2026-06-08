/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_ID;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_EMITTED_AT;
import static org.apache.logging.log4j.util.Strings.isNotBlank;

import io.airbyte.cdk.integrations.base.CommitOnStateAirbyteMessageConsumer;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.iceberg.config.WriteConfig;
import io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfig;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;
import org.apache.iceberg.catalog.Catalog;
import org.apache.iceberg.catalog.TableIdentifier;
import org.apache.iceberg.spark.actions.SparkActions;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.destination.iceberg.util.AirbyteSchemaConverter;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.DataFrameWriterV2;
import org.apache.spark.sql.Encoders;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SaveMode;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.catalyst.expressions.GenericRow;
import org.apache.spark.sql.expressions.Window;
import org.apache.spark.sql.expressions.WindowSpec;
import org.apache.spark.sql.functions;
import org.apache.spark.sql.types.DataType;
import org.apache.spark.sql.types.StringType$;
import org.apache.spark.sql.types.StructField;
import org.apache.spark.sql.types.StructType;
import org.apache.spark.sql.types.TimestampType$;
import org.apache.spark.sql.Column;

/**
 * @author Leibniz on 2022/10/26.
 */
@Slf4j
public class IcebergConsumer extends CommitOnStateAirbyteMessageConsumer {

  private final SparkSession spark;
  private final ConfiguredAirbyteCatalog catalog;
  private final IcebergCatalogConfig catalogConfig;

  private Map<AirbyteStreamNameNamespacePair, WriteConfig> writeConfigs;

  public IcebergConsumer(SparkSession spark,
      Consumer<AirbyteMessage> outputRecordCollector,
      ConfiguredAirbyteCatalog catalog,
      IcebergCatalogConfig catalogConfig) {
    super(outputRecordCollector);
    this.spark = spark;
    this.catalog = catalog;
    this.catalogConfig = catalogConfig;
  }

  /**
   * call this method to initialize any resources that need to be created BEFORE
   * the consumer consumes
   * any messages
   */
  @Override
  protected void startTracked() throws Exception {
    Map<AirbyteStreamNameNamespacePair, WriteConfig> configs = new HashMap<>();
    Set<String> namespaceSet = new HashSet<>();
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getStream().getName().toLowerCase();
      String namespace = (isNotBlank(stream.getStream().getNamespace()) ? stream.getStream().getNamespace()
          : catalogConfig.defaultOutputDatabase()).toLowerCase();
      if (!namespaceSet.contains(namespace)) {
        namespaceSet.add(namespace);
        try {
          spark.sql("CREATE DATABASE IF NOT EXISTS " + namespace);
        } catch (Exception e) {
          log.warn("Create non-existed database failed: {}", e.getMessage(), e);
        }
      }
      final DestinationSyncMode syncMode = stream.getDestinationSyncMode();
      if (syncMode == null) {
        throw new IllegalStateException("Undefined destination sync mode");
      }
      final boolean isAppendMode = syncMode != DestinationSyncMode.OVERWRITE;
      AirbyteStreamNameNamespacePair nameNamespacePair = AirbyteStreamNameNamespacePair
          .fromAirbyteStream(stream.getStream());
      Integer flushBatchSize = catalogConfig.getFormatConfig().getFlushBatchSize();

      // Convert Airbyte Schema to Spark Schema and add metadata columns
      StructType schema = AirbyteSchemaConverter.toStructType(stream.getStream().getJsonSchema());
      schema = schema.add(COLUMN_NAME_AB_ID, StringType$.MODULE$)
          .add(COLUMN_NAME_EMITTED_AT, TimestampType$.MODULE$);

      // Dedup configuration: APPEND_DEDUP streams auto-enable merge using the stream's primary key
      // (falling back to the connector-level configured merge_keys). Other streams keep the existing
      // manual merge behavior driven by the format config.
      boolean mergeMode;
      List<String> mergeKeys;
      if (syncMode == DestinationSyncMode.APPEND_DEDUP) {
        mergeKeys = resolveMergeKeys(stream);
        if (mergeKeys.isEmpty()) {
          throw new ConfigErrorException(
              "Stream '" + streamName + "' uses Append + Dedup but has no primary key and no configured "
                  + "merge_keys. A primary key or merge_keys is required to deduplicate records.");
        }
        mergeMode = true;
        log.info("=> Stream {} is Append+Dedup; enabling merge with keys {}", streamName, mergeKeys);
      } else {
        mergeMode = catalogConfig.getFormatConfig().isMergeMode();
        mergeKeys = catalogConfig.getFormatConfig().getMergeKeys();
      }
      boolean partitionMode = catalogConfig.getFormatConfig().isPartitionMode();
      List<String> partitionKeys = catalogConfig.getFormatConfig().getPartitionKeys();

      // Capture the cursor column (if any) independent of partitioning; it drives latest-wins
      // ordering during dedup/merge.
      String cursorColumnName = null;
      List<String> cursorField = stream.getCursorField();
      if (cursorField != null && !cursorField.isEmpty()) {
        cursorColumnName = cursorField.get(cursorField.size() - 1); // last element = flattened column name
      }

      // Auto date partitioning: use the cursor field for incremental syncs.
      boolean datePartitionMode = false;
      String datePartitionSourceColumn = null;
      if (cursorColumnName != null && catalogConfig.getFormatConfig().isAutoDatePartition()) {
        log.info("=> Stream {} has cursor field: {}", streamName, cursorColumnName);
        datePartitionMode = true;
        datePartitionSourceColumn = cursorColumnName;
        log.info("=> Auto-enabling date partition mode using cursor field '{}' for year/month/day partitions",
            cursorColumnName);
      }

      WriteConfig writeConfig = new WriteConfig(namespace, streamName, isAppendMode, flushBatchSize, schema,
          mergeMode, mergeKeys, partitionMode, partitionKeys, datePartitionMode, datePartitionSourceColumn,
          cursorColumnName);
      configs.put(nameNamespacePair, writeConfig);
      try {
        spark.sql("DROP TABLE IF EXISTS " + writeConfig.getFullTempTableName());
      } catch (Exception e) {
        log.warn("Drop existed temp table failed: {}", e.getMessage(), e);
      }
    }
    this.writeConfigs = configs;
  }

  /**
   * call this method when receive a non-STATE AirbyteMessage Ref to <a href=
   * "https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#airbytemessage">AirbyteMessage</a>
   */
  @Override
  protected void acceptTracked(AirbyteMessage msg) throws Exception {
    if (msg.getType() != Type.RECORD) {
      return;
    }
    final AirbyteRecordMessage recordMessage = msg.getRecord();

    // ignore other message types.
    AirbyteStreamNameNamespacePair nameNamespacePair = AirbyteStreamNameNamespacePair.fromRecordMessage(
        recordMessage);
    WriteConfig writeConfig = writeConfigs.get(nameNamespacePair);
    if (writeConfig == null) {
      throw new IllegalArgumentException(String.format(
          "Message contained record from a stream that was not in the catalog. namespace: %s , stream: %s",
          recordMessage.getNamespace(),
          recordMessage.getStream()));
    }

    // Prepare data with metadata
    ObjectNode data = (ObjectNode) recordMessage.getData();
    data.put(COLUMN_NAME_AB_ID, UUID.randomUUID().toString());
    // Spark JSON reader expects timestamp in ISO8601 string or specific format,
    // but here we are defining the schema as TimestampType.
    // Spark's JSON parser handles ISO8601 strings for TimestampType.
    // Airbyte's emittedAt is long (millis). We need to convert it to string or let
    // Spark handle it?
    // Spark JSON reader might not handle long as Timestamp directly unless
    // configured.
    // Safer to pass it as string or use a format.
    // Let's use ISO string.
    data.put(COLUMN_NAME_EMITTED_AT, new Timestamp(recordMessage.getEmittedAt()).toInstant().toString());

    boolean needInsert = writeConfig.addData(Jsons.serialize(data));
    if (needInsert) {
      appendToTempTable(writeConfig);
    }
  }

  private void appendToTempTable(WriteConfig writeConfig) {
    String tableName = writeConfig.getFullTempTableName();
    List<String> jsonRows = writeConfig.fetchDataCache();
    // saveAsTable even if rows is empty, to ensure table is created.
    // otherwise the table would be missing, and throws exception in close()
    log.info("=> Flushing {} rows into {}", jsonRows.size(), tableName);

    if (jsonRows.isEmpty()) {
      // If empty, create an empty DataFrame with the schema
      spark.createDataFrame(new java.util.ArrayList<>(), writeConfig.getSchema())
          .write()
          .mode(SaveMode.Append)
          .option("write-format", catalogConfig.getFormatConfig().getFormat().getFormatName())
          .saveAsTable(tableName);
    } else {
      Dataset<String> jsonDS = spark.createDataset(jsonRows, Encoders.STRING());
      spark.read().schema(writeConfig.getSchema()).json(jsonDS)
          .write()
          // append data to temp table
          .mode(SaveMode.Append)
          // TODO compression config
          .option("write-format", catalogConfig.getFormatConfig().getFormat().getFormatName())
          .saveAsTable(tableName);
    }
  }

  /**
   * call this method when receive a STATE AirbyteMessage ———— it is the last
   * message
   */
  @Override
  public void commit() throws Exception {
  }

  @Override
  protected void close(boolean hasFailed) throws Exception {
    log.info("close {}, hasFailed={}", this.getClass().getSimpleName(), hasFailed);
    Catalog icebergCatalog = catalogConfig.genCatalog();
    try {
      if (!hasFailed) {
        log.info("==> Migration finished with no explicit errors. Copying data from temp tables to permanent");
        for (WriteConfig writeConfig : writeConfigs.values()) {
          appendToTempTable(writeConfig);
          String tempTableName = writeConfig.getFullTempTableName();
          String finalTableName = writeConfig.getFullTableName();
          SaveMode saveMode = writeConfig.isAppendMode() ? SaveMode.Append : SaveMode.Overwrite;
          boolean tableExists = spark.catalog().tableExists(finalTableName);

          // For dedup streams, collapse the batch to one row per key (latest by the ordering
          // column) before any write. This guarantees both the initial create and the merge never
          // see duplicate keys.
          Dataset<Row> sourceDf = spark.table(tempTableName);
          if (writeConfig.shouldMerge()) {
            String orderingColumn = effectiveOrderingColumn(sourceDf, writeConfig.getOrderingColumn());
            sourceDf = dedupeLatestPerKey(sourceDf, writeConfig.getMergeKeys(), orderingColumn);
          }

          // Check if merge mode is enabled for this write config
          if (writeConfig.shouldMerge() && tableExists) {
            log.info("=> Migration(merge) data from {} to {}",
                tempTableName,
                finalTableName);
            // Ensure the existing table is merge-on-read and keyed on the merge keys before merging.
            ensureMergeOnReadProperties(finalTableName);
            ensureIdentifierFieldsAndSortOrder(finalTableName, writeConfig.getMergeKeys());
            mergeToFinalTable(writeConfig, sourceDf, finalTableName);
          } else if (writeConfig.shouldDatePartition()) {
            // Date-based hierarchical partitioning (year/month/day)
            log.info("=> Migration({}) with date partitioning from {} to {}",
                writeConfig.isAppendMode() ? "append" : "overwrite",
                tempTableName,
                finalTableName);

            String sourceCol = writeConfig.getDatePartitionSourceColumn();
            log.info("=> Deriving year/month/day partitions from column: {}", sourceCol);

            // Add derived year/month/day columns to the (possibly deduped) source
            Dataset<Row> df = sourceDf
                .withColumn("year", functions.year(functions.col(sourceCol)))
                .withColumn("month", functions.month(functions.col(sourceCol)))
                .withColumn("day", functions.dayofmonth(functions.col(sourceCol)));

            // Write with hierarchical partitioning
            DataFrameWriterV2<Row> writer = df
                .writeTo(finalTableName)
                .using("iceberg")
                .partitionedBy(
                    functions.col("year"),
                    functions.col("month"),
                    functions.col("day")
                );
            writer = applyMergeOnReadProperties(writer, writeConfig);

            if (saveMode == SaveMode.Append && tableExists) {
              writer.append();
            } else {
              writer.createOrReplace();
            }
            // Newly created merged table: set identifier fields + sort order on the merge keys.
            if (writeConfig.shouldMerge() && !tableExists) {
              ensureIdentifierFieldsAndSortOrder(finalTableName, writeConfig.getMergeKeys());
            }
          } else {
            log.info("=> Migration({}) data from {} to {}",
                writeConfig.isAppendMode() ? "append" : "overwrite",
                tempTableName,
                finalTableName);

            DataFrameWriterV2<Row> writer = sourceDf
                .writeTo(finalTableName)
                .using("iceberg");

            if (writeConfig.shouldPartition()) {
              // Convert partition column names to Column expressions
              List<String> partitionCols = writeConfig.getPartitionKeys();
              Column first = functions.col(partitionCols.get(0));
              Column[] rest = partitionCols.subList(1, partitionCols.size())
                  .stream()
                  .map(functions::col)
                  .toArray(Column[]::new);
              writer = writer.partitionedBy(first, rest);
            }
            writer = applyMergeOnReadProperties(writer, writeConfig);

            if (saveMode == SaveMode.Append && tableExists) {
              writer.append();
            } else {
              writer.createOrReplace();
            }
            // Newly created merged table: set identifier fields + sort order on the merge keys.
            if (writeConfig.shouldMerge() && !tableExists) {
              ensureIdentifierFieldsAndSortOrder(finalTableName, writeConfig.getMergeKeys());
            }
          }

          if (catalogConfig.getFormatConfig().isAutoCompact()) {
            tryCompactTable(icebergCatalog, writeConfig);
          }
        }
        log.info("==> Copy temp tables finished...");
      } else {
        log.error("Had errors while migrations");
      }
    } finally {
      log.info("Removing temp tables...");
      for (Entry<AirbyteStreamNameNamespacePair, WriteConfig> entry : writeConfigs.entrySet()) {
        tryDropTempTable(icebergCatalog, entry.getValue());
      }
      log.info("Closing Spark Session...");
      this.spark.close();
      log.info("Finishing destination process...completed");
    }
  }

  /**
   * Resolve the columns used to deduplicate/merge a stream: prefer the stream's primary key,
   * falling back to the connector-level configured merge keys.
   *
   * @param stream the configured stream
   * @return the flattened column names to dedup on (may be empty if none defined)
   */
  private List<String> resolveMergeKeys(ConfiguredAirbyteStream stream) {
    List<List<String>> primaryKey = stream.getPrimaryKey();
    if (primaryKey != null && !primaryKey.isEmpty()) {
      List<String> keys = new ArrayList<>();
      for (List<String> keyPath : primaryKey) {
        if (keyPath != null && !keyPath.isEmpty()) {
          // Use the last path element as the flattened top-level column name
          keys.add(keyPath.get(keyPath.size() - 1));
        }
      }
      if (!keys.isEmpty()) {
        return keys;
      }
    }
    return new ArrayList<>(catalogConfig.getFormatConfig().getMergeKeys());
  }

  /**
   * Pick the column to order by for "latest wins" resolution. Uses the preferred (cursor) column
   * when it is present in the dataset, otherwise falls back to the Airbyte emitted-at column.
   */
  private String effectiveOrderingColumn(Dataset<Row> df, String preferred) {
    if (preferred != null && Arrays.asList(df.columns()).contains(preferred)) {
      return preferred;
    }
    return COLUMN_NAME_EMITTED_AT;
  }

  /**
   * Collapse a batch to a single row per key, keeping the latest record. Records are ordered by the
   * ordering column (cursor when available) descending, then {@code _airbyte_emitted_at}
   * descending, then {@code _airbyte_ab_id} descending for a deterministic tiebreak. Prevents
   * duplicate keys within a batch from being inserted multiple times by the merge.
   *
   * @param df             the source dataset
   * @param keyCols        the columns identifying a logical record
   * @param orderingColumn the column used for latest-wins ordering
   * @return the deduplicated dataset
   */
  private Dataset<Row> dedupeLatestPerKey(Dataset<Row> df, List<String> keyCols, String orderingColumn) {
    Column[] partitionCols = keyCols.stream().map(functions::col).toArray(Column[]::new);
    List<Column> orderCols = new ArrayList<>();
    orderCols.add(functions.col(orderingColumn).desc());
    if (!COLUMN_NAME_EMITTED_AT.equals(orderingColumn)) {
      orderCols.add(functions.col(COLUMN_NAME_EMITTED_AT).desc());
    }
    orderCols.add(functions.col(COLUMN_NAME_AB_ID).desc());
    WindowSpec window = Window.partitionBy(partitionCols).orderBy(orderCols.toArray(new Column[0]));
    return df
        .withColumn("_ab_dedup_rn", functions.row_number().over(window))
        .filter("_ab_dedup_rn = 1")
        .drop("_ab_dedup_rn");
  }

  /**
   * Merge an already-deduped increment dataset into the final table using the merge keys. The match
   * condition is null-safe and uses the merge keys only: when a record's partition column (the
   * cursor) changes, Iceberg moves the row to its new partition instead of leaving a duplicate
   * behind. An older record never overwrites a newer one already in the table (latest-wins on the
   * ordering column).
   *
   * @param writeConfig    The write configuration containing merge settings
   * @param increment      The deduped increment dataset
   * @param finalTableName The full final table name
   */
  private void mergeToFinalTable(WriteConfig writeConfig, Dataset<Row> increment, String finalTableName) {
    log.info("=> Starting merge operation");
    log.info("   Merge keys: {}", writeConfig.getMergeKeys());
    log.info("   Final table: {}", finalTableName);

    // When the final table is date-partitioned, derive year/month/day so the increment's columns
    // align with the partitioned table for updateAll/insertAll. These are intentionally NOT added
    // to the match condition: the partition column is the mutable cursor, so matching on it would
    // miss updated rows and reintroduce duplicates. Matching on the merge keys lets Iceberg move
    // the row across partitions on update.
    if (writeConfig.shouldDatePartition()) {
      String sourceCol = writeConfig.getDatePartitionSourceColumn();
      increment = increment
          .withColumn("year", functions.year(functions.col(sourceCol)))
          .withColumn("month", functions.month(functions.col(sourceCol)))
          .withColumn("day", functions.dayofmonth(functions.col(sourceCol)));
    }

    // Evolve the target schema to accommodate new/changed source columns before merging.
    reconcileSchema(increment, finalTableName);
    // Ensure date partition fields exist on the target if date partitioning is desired.
    if (writeConfig.shouldDatePartition()) {
      ensureDatePartitionFields(finalTableName);
    }

    String orderingColumn = effectiveOrderingColumn(increment, writeConfig.getOrderingColumn());

    StringBuilder condition = new StringBuilder();
    boolean first = true;
    for (String col : writeConfig.getMergeKeys()) {
      if (!first) {
        condition.append(" and ");
      }
      // Null-safe equality so rows whose key contains NULLs still match instead of duplicating.
      condition.append("increment.%s <=> %s.%s".formatted(col, finalTableName, col));
      first = false;
    }

    log.info("=> Merge condition: {}", condition.toString());
    log.info("=> Latest-wins ordering column: {}", orderingColumn);

    increment
        .as("increment")
        .mergeInto(
            finalTableName,
            functions.expr(condition.toString()))
        .whenMatched(functions.expr(
            "increment.%s >= %s.%s".formatted(orderingColumn, finalTableName, orderingColumn)))
        .updateAll()
        .whenNotMatched()
        .insertAll()
        .merge();
  }

  /**
   * Append the merge-on-read + format-version table properties to a writer when the stream is a
   * merged (dedup) stream, so newly created tables support row-level deletes.
   */
  private DataFrameWriterV2<Row> applyMergeOnReadProperties(DataFrameWriterV2<Row> writer, WriteConfig writeConfig) {
    if (!writeConfig.shouldMerge()) {
      return writer;
    }
    return writer
        .tableProperty("format-version", "2")
        .tableProperty("write.merge.mode", "merge-on-read")
        .tableProperty("write.update.mode", "merge-on-read")
        .tableProperty("write.delete.mode", "merge-on-read");
  }

  /**
   * Ensure an existing table uses merge-on-read for row-level operations. Idempotent.
   */
  private void ensureMergeOnReadProperties(String finalTableName) {
    try {
      spark.sql(("ALTER TABLE %s SET TBLPROPERTIES ("
          + "'format-version'='2',"
          + "'write.merge.mode'='merge-on-read',"
          + "'write.update.mode'='merge-on-read',"
          + "'write.delete.mode'='merge-on-read')").formatted(finalTableName));
    } catch (Exception e) {
      log.warn("Failed to set merge-on-read properties on {}: {}", finalTableName, e.getMessage(), e);
    }
  }

  /**
   * Mark the merge keys as Iceberg identifier fields and set a sort order on them, mirroring the
   * destination-s3-data-lake schema. Identifier fields require non-null key columns, so this first
   * promotes the key columns to NOT NULL. All steps are best-effort: if a key column contains nulls
   * the identifier-field change is skipped with a warning rather than failing the sync.
   */
  private void ensureIdentifierFieldsAndSortOrder(String finalTableName, List<String> keys) {
    if (keys == null || keys.isEmpty()) {
      return;
    }
    // Sort order is safe regardless of nullability.
    try {
      String orderBy = keys.stream().map(k -> "`" + k + "` ASC").collect(Collectors.joining(", "));
      spark.sql("ALTER TABLE %s WRITE ORDERED BY %s".formatted(finalTableName, orderBy));
    } catch (Exception e) {
      log.warn("Failed to set sort order on {}: {}", finalTableName, e.getMessage());
    }
    // Identifier fields require required (non-null) columns.
    try {
      for (String k : keys) {
        spark.sql("ALTER TABLE %s ALTER COLUMN `%s` SET NOT NULL".formatted(finalTableName, k));
      }
      String fields = keys.stream().map(k -> "`" + k + "`").collect(Collectors.joining(", "));
      spark.sql("ALTER TABLE %s SET IDENTIFIER FIELDS %s".formatted(finalTableName, fields));
      log.info("=> Set identifier fields {} on {}", keys, finalTableName);
    } catch (Exception e) {
      log.warn("Could not set identifier fields on {} (key columns may be nullable): {}",
          finalTableName, e.getMessage());
    }
  }

  /**
   * Evolve the target table schema to accommodate the increment: add columns present in the
   * increment but missing in the table, and widen existing columns to a safe supertype
   * (int->bigint, float->double, decimal precision increase). Narrowing/incompatible changes are
   * skipped. Best-effort; individual failures are logged and do not abort the sync.
   */
  private void reconcileSchema(Dataset<Row> increment, String finalTableName) {
    final StructType incoming = increment.schema();
    final StructType target = spark.table(finalTableName).schema();
    final Map<String, DataType> targetTypes = new HashMap<>();
    for (StructField f : target.fields()) {
      targetTypes.put(f.name(), f.dataType());
    }
    for (StructField field : incoming.fields()) {
      String name = field.name();
      if (!targetTypes.containsKey(name)) {
        try {
          spark.sql("ALTER TABLE %s ADD COLUMNS (`%s` %s)"
              .formatted(finalTableName, name, field.dataType().catalogString()));
          log.info("=> Schema evolution: added column `{}` {} to {}", name, field.dataType().catalogString(),
              finalTableName);
        } catch (Exception e) {
          log.warn("Failed to add column {} to {}: {}", name, finalTableName, e.getMessage());
        }
      } else {
        String widened = safeWiden(targetTypes.get(name), field.dataType());
        if (widened != null) {
          try {
            spark.sql("ALTER TABLE %s ALTER COLUMN `%s` TYPE %s".formatted(finalTableName, name, widened));
            log.info("=> Schema evolution: widened column `{}` to {} in {}", name, widened, finalTableName);
          } catch (Exception e) {
            log.warn("Failed to widen column {} in {}: {}", name, finalTableName, e.getMessage());
          }
        }
      }
    }
  }

  /**
   * Return the target catalog type string if {@code incoming} is a safe widening of {@code target},
   * or null when no (safe) widening applies. Supports int->bigint, float->double, and decimal
   * precision increases (same scale), matching Iceberg's allowed type promotions.
   */
  private String safeWiden(DataType target, DataType incoming) {
    String t = target.catalogString();
    String i = incoming.catalogString();
    if (t.equals(i)) {
      return null;
    }
    if (t.equals("int") && i.equals("bigint")) {
      return "bigint";
    }
    if (t.equals("float") && i.equals("double")) {
      return "double";
    }
    if (t.startsWith("decimal(") && i.startsWith("decimal(")) {
      int[] tp = parseDecimal(t);
      int[] ip = parseDecimal(i);
      if (tp != null && ip != null && tp[1] == ip[1] && ip[0] > tp[0]) {
        return i;
      }
    }
    return null;
  }

  private int[] parseDecimal(String catalogString) {
    try {
      String inner = catalogString.substring(catalogString.indexOf('(') + 1, catalogString.indexOf(')'));
      String[] parts = inner.split(",");
      return new int[] {Integer.parseInt(parts[0].trim()), Integer.parseInt(parts[1].trim())};
    } catch (Exception e) {
      return null;
    }
  }

  /**
   * Ensure the target table is partitioned by identity(year)/identity(month)/identity(day). Uses
   * Iceberg partition evolution (metadata-only); existing data files keep their layout. Adding a
   * field that already exists throws, which is caught and ignored.
   */
  private void ensureDatePartitionFields(String finalTableName) {
    for (String f : List.of("year", "month", "day")) {
      try {
        spark.sql("ALTER TABLE %s ADD PARTITION FIELD %s".formatted(finalTableName, f));
        log.info("=> Partition evolution: added identity partition field {} on {}", f, finalTableName);
      } catch (Exception e) {
        log.debug("Partition field {} not added on {} (likely already present): {}",
            f, finalTableName, e.getMessage());
      }
    }
  }

  private void tryDropTempTable(Catalog icebergCatalog, WriteConfig writeConfig) {
    try {
      log.info("Trying to drop temp table: {}", writeConfig.getFullTempTableName());
      TableIdentifier tempTableIdentifier = TableIdentifier.of(writeConfig.getNamespace(),
          writeConfig.getTempTableName());
      boolean dropSuccess = icebergCatalog.dropTable(tempTableIdentifier, true);
      log.info("Drop temp table: {}", writeConfig.getFullTempTableName());
    } catch (Exception e) {
      String errMsg = e.getMessage();
      log.error("Drop temp table caught exception:{}", errMsg, e);
    }
  }

  private void tryCompactTable(Catalog icebergCatalog, WriteConfig writeConfig) {
    log.info("=> Auto-Compact is enabled, try compact Iceberg data files");
    int compactTargetFileSizeBytes = catalogConfig.getFormatConfig().getCompactTargetFileSizeInMb() * 1024 * 1024;
    try {
      TableIdentifier tableIdentifier = TableIdentifier.of(writeConfig.getNamespace(),
          writeConfig.getTableName());
      SparkActions.get()
          .rewriteDataFiles(icebergCatalog.loadTable(tableIdentifier))
          .option("target-file-size-bytes", String.valueOf(compactTargetFileSizeBytes))
          .execute();
    } catch (Exception e) {
      log.warn("Compact Iceberg data files failed: {}", e.getMessage(), e);
    }
  }

}
