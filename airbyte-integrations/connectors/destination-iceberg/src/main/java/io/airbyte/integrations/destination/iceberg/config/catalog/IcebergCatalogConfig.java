/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.catalog;

import static org.apache.commons.lang3.StringUtils.isBlank;

import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.iceberg.IcebergConstants;
import io.airbyte.integrations.destination.iceberg.config.format.FormatConfig;
import io.airbyte.integrations.destination.iceberg.config.storage.StorageConfig;
import java.util.Map;
import lombok.Data;
import lombok.ToString;
import lombok.extern.slf4j.Slf4j;
import org.apache.iceberg.Schema;
import org.apache.iceberg.Table;
import org.apache.iceberg.TableScan;
import org.apache.iceberg.catalog.Catalog;
import org.apache.iceberg.catalog.TableIdentifier;
import org.apache.iceberg.data.IcebergGenerics;
import org.apache.iceberg.data.Record;
import org.apache.iceberg.io.CloseableIterable;
import org.apache.iceberg.types.Types;
import org.apache.iceberg.types.Types.NestedField;

/**
 * @author Leibniz on 2022/10/26.
 */
@Data
@ToString
@Slf4j
public abstract class IcebergCatalogConfig {

  protected StorageConfig storageConfig;
  protected FormatConfig formatConfig;

  private String defaultOutputDatabase;

  public void check() throws Exception {
    // Catalog check, only checks catalog metadata
    Catalog catalog = genCatalog();
    String tempTableName = "temp_" + System.currentTimeMillis();
    TableIdentifier tempTableId = TableIdentifier.of(defaultOutputDatabase(), tempTableName);
    Schema schema = new Schema(
        NestedField.required(0, JavaBaseConstants.COLUMN_NAME_AB_ID, Types.StringType.get()),
        NestedField.optional(1, JavaBaseConstants.COLUMN_NAME_EMITTED_AT, Types.TimestampType.withZone()),
        NestedField.required(2, JavaBaseConstants.COLUMN_NAME_DATA, Types.StringType.get()));
    Table tempTable = catalog.createTable(tempTableId, schema);
    TableScan tableScan = tempTable.newScan();
    log.info("Created temp table: {}", tempTableName);
    log.info("Temp table's schema: {}", tableScan.schema());

    try (CloseableIterable<Record> records = IcebergGenerics.read(tempTable).build()) {
      for (Record record : records) {
        // never reach
        log.info("Record in temp table: {}", record);
      }
    }

    boolean dropSuccess = catalog.dropTable(tempTableId);
    log.info("Dropped temp table: {}, success: {}", tempTableName, dropSuccess);

    // storage check
    this.storageConfig.check();
  }

  public abstract Map<String, String> sparkConfigMap();

  public abstract Catalog genCatalog();

  public String defaultOutputDatabase() {
    return isBlank(defaultOutputDatabase) ? IcebergConstants.DEFAULT_DATABASE : defaultOutputDatabase;
  }

}
