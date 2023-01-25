/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg;

import static io.airbyte.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_ID;
import static io.airbyte.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static io.airbyte.integrations.base.JavaBaseConstants.COLUMN_NAME_EMITTED_AT;
import static org.apache.logging.log4j.util.Strings.isNotBlank;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.CommitOnStateAirbyteMessageConsumer;
import io.airbyte.integrations.destination.iceberg.config.WriteConfig;
import io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfig;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.sql.Timestamp;
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
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SaveMode;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.catalyst.expressions.GenericRow;
import org.apache.spark.sql.types.StringType$;
import org.apache.spark.sql.types.StructType;
import org.apache.spark.sql.types.TimestampType$;

/**
 * @author Leibniz on 2022/10/26.
 */
@Slf4j
public class IcebergConsumer extends CommitOnStateAirbyteMessageConsumer {

  private final SparkSession spark;
  private final ConfiguredAirbyteCatalog catalog;
  private final IcebergCatalogConfig catalogConfig;

  private Map<AirbyteStreamNameNamespacePair, WriteConfig> writeConfigs;

  private final StructType normalizationSchema;

  public IcebergConsumer(SparkSession spark,
                         Consumer<AirbyteMessage> outputRecordCollector,
                         ConfiguredAirbyteCatalog catalog,
                         IcebergCatalogConfig catalogConfig) {
    super(outputRecordCollector);
    this.spark = spark;
    this.catalog = catalog;
    this.catalogConfig = catalogConfig;
    this.normalizationSchema = new StructType().add(COLUMN_NAME_AB_ID, StringType$.MODULE$)
        .add(COLUMN_NAME_EMITTED_AT, TimestampType$.MODULE$)
        .add(COLUMN_NAME_DATA, StringType$.MODULE$);
  }

  /**
   * call this method to initialize any resources that need to be created BEFORE the consumer consumes
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
      AirbyteStreamNameNamespacePair nameNamespacePair = AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream.getStream());
      Integer flushBatchSize = catalogConfig.getFormatConfig().getFlushBatchSize();
      WriteConfig writeConfig = new WriteConfig(namespace, streamName, isAppendMode, flushBatchSize);
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

    // write data
    Row row = new GenericRow(new Object[] {UUID.randomUUID().toString(), new Timestamp(recordMessage.getEmittedAt()),
      Jsons.serialize(recordMessage.getData())});
    boolean needInsert = writeConfig.addData(row);
    if (needInsert) {
      appendToTempTable(writeConfig);
    }
  }

  private void appendToTempTable(WriteConfig writeConfig) {
    String tableName = writeConfig.getFullTempTableName();
    List<Row> rows = writeConfig.fetchDataCache();
    // saveAsTable even if rows is empty, to ensure table is created.
    // otherwise the table would be missing, and throws exception in close()
    log.info("=> Flushing {} rows into {}", rows.size(), tableName);
    spark.createDataFrame(rows, normalizationSchema).write()
        // append data to temp table
        .mode(SaveMode.Append)
        // TODO compression config
        .option("write-format", catalogConfig.getFormatConfig().getFormat().getFormatName()).saveAsTable(tableName);
  }

  /**
   * call this method when receive a STATE AirbyteMessage ———— it is the last message
   */
  @Override
  public void commit() throws Exception {}

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
          log.info("=> Migration({}) data from {} to {}",
              writeConfig.isAppendMode() ? "append" : "overwrite",
              tempTableName,
              finalTableName);
          spark.sql("SELECT * FROM %s".formatted(tempTableName))
              .write()
              .mode(writeConfig.isAppendMode() ? SaveMode.Append : SaveMode.Overwrite)
              .saveAsTable(finalTableName);
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
    int compactTargetFileSizeBytes =
        catalogConfig.getFormatConfig().getCompactTargetFileSizeInMb() * 1024 * 1024;
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
