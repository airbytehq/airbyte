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
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.UUID;
import java.util.function.Consumer;
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
import org.apache.spark.sql.types.StringType$;
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

      // Dedup configuration: APPEND_DEDUP streams auto-enable merge using the
      // stream's primary key (falling back to configured merge_keys). Other
      // streams keep the existing manual merge behavior.
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
      
      // Auto date partitioning: use cursor field for incremental syncs
      boolean datePartitionMode = false;
      String datePartitionSourceColumn = null;
      
      List<String> cursorField = stream.getCursorField();
      if (cursorField != null && !cursorField.isEmpty() && catalogConfig.getFormatConfig().isAutoDatePartition()) {
        String cursorColumnName = cursorField.get(cursorField.size() - 1); // Get the last element (actual column name)
        log.info("=> Stream {} has cursor field: {}", streamName, cursorColumnName);
        
        // Auto-enable date partitioning for syncs with cursor field
        datePartitionMode = true;
        datePartitionSourceColumn = cursorColumnName;
        log.info("=> Auto-enabling date partition mode using cursor field '{}' for year/month/day partitions", cursorColumnName);
      }

      WriteConfig writeConfig = new WriteConfig(namespace, streamName, isAppendMode, flushBatchSize, schema,
          mergeMode, mergeKeys, partitionMode, partitionKeys, datePartitionMode, datePartitionSourceColumn);
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

          // For dedup streams, collapse the batch to one row per key (latest by
          // _airbyte_emitted_at) before any write. This guarantees the initial
          // create and the merge never see duplicate keys.
          Dataset<Row> sourceDf = spark.table(tempTableName);
          if (writeConfig.shouldMerge()) {
            sourceDf = dedupeLatestPerKey(sourceDf, writeConfig.getMergeKeys());
          }

          // Check if merge mode is enabled for this write config
          if (writeConfig.shouldMerge() && tableExists) {
            log.info("=> Migration(merge) data from {} to {}",
                tempTableName,
                finalTableName);
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
            
            if (saveMode == SaveMode.Append && tableExists) {
              writer.append();
            } else {
              writer.createOrReplace();
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

            if (saveMode == SaveMode.Append && tableExists) {
              writer.append();
            } else {
              writer.createOrReplace();
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
   * Resolve the columns used to deduplicate a stream: prefer the stream's
   * primary key, falling back to the connector-level configured merge keys.
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
   * Collapse a batch to a single row per key, keeping the latest record ordered
   * by {@code _airbyte_emitted_at} descending. Prevents duplicate keys within a
   * batch from being inserted multiple times by the merge.
   *
   * @param df       the source dataset
   * @param keyCols  the columns identifying a logical record
   * @return the deduplicated dataset
   */
  private Dataset<Row> dedupeLatestPerKey(Dataset<Row> df, List<String> keyCols) {
    Column[] partitionCols = keyCols.stream().map(functions::col).toArray(Column[]::new);
    WindowSpec window = Window.partitionBy(partitionCols)
        .orderBy(functions.col(COLUMN_NAME_EMITTED_AT).desc());
    return df
        .withColumn("_ab_dedup_rn", functions.row_number().over(window))
        .filter("_ab_dedup_rn = 1")
        .drop("_ab_dedup_rn");
  }

  /**
   * Merge an already-deduped increment dataset into the final table using merge
   * keys. The match condition is on the merge keys only: when a record's
   * partition column (the cursor) changes, Iceberg moves the row to its new
   * partition instead of leaving a duplicate behind. An older record (smaller
   * {@code _airbyte_emitted_at}) never overwrites a newer one already in the table.
   *
   * @param writeConfig    The write configuration containing merge settings
   * @param increment      The deduped increment dataset
   * @param finalTableName The full final table name
   */
  private void mergeToFinalTable(WriteConfig writeConfig, Dataset<Row> increment, String finalTableName) {
    log.info("=> Starting merge operation");
    log.info("   Merge keys: {}", writeConfig.getMergeKeys());
    log.info("   Final table: {}", finalTableName);

    // When the final table is date-partitioned, derive year/month/day so the
    // increment's columns align with the partitioned table for updateAll/insertAll.
    // These are intentionally NOT added to the match condition: the partition
    // column is the mutable cursor, so matching on it would miss updated rows
    // and reintroduce duplicates. Matching on the merge keys lets Iceberg move
    // the row across partitions on update.
    if (writeConfig.shouldDatePartition()) {
      String sourceCol = writeConfig.getDatePartitionSourceColumn();
      increment = increment
          .withColumn("year", functions.year(functions.col(sourceCol)))
          .withColumn("month", functions.month(functions.col(sourceCol)))
          .withColumn("day", functions.dayofmonth(functions.col(sourceCol)));
    }

    StringBuilder condition = new StringBuilder();
    boolean first = true;
    for (String col : writeConfig.getMergeKeys()) {
      if (!first) {
        condition.append(" and ");
      }
      condition.append("increment.%s = %s.%s".formatted(col, finalTableName, col));
      first = false;
    }

    log.info("=> Merge condition: {}", condition.toString());

    increment
        .as("increment")
        .mergeInto(
            finalTableName,
            functions.expr(condition.toString()))
        .whenMatched(functions.expr(
            "increment.%s >= %s.%s".formatted(COLUMN_NAME_EMITTED_AT, finalTableName, COLUMN_NAME_EMITTED_AT)))
        .updateAll()
        .whenNotMatched()
        .insertAll()
        .merge();
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
