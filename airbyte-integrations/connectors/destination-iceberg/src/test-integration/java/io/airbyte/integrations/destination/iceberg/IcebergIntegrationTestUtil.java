/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg;

import static org.sparkproject.jetty.util.StringUtil.isNotBlank;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.Bucket;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfig;
import io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfigFactory;
import io.airbyte.integrations.destination.iceberg.config.storage.S3Config;
import java.io.IOException;
import java.sql.Timestamp;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;
import org.apache.iceberg.Table;
import org.apache.iceberg.catalog.Catalog;
import org.apache.iceberg.catalog.TableIdentifier;
import org.apache.iceberg.data.IcebergGenerics;
import org.apache.iceberg.data.Record;
import org.apache.iceberg.io.CloseableIterable;
import org.glassfish.jersey.internal.guava.Lists;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.lifecycle.Startable;

/**
 * @author Leibniz on 2022/11/3.
 */
public class IcebergIntegrationTestUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(IcebergIntegrationTestUtil.class);
  public static final String ICEBERG_IMAGE_NAME = "airbyte/destination-iceberg:dev";
  public static final String WAREHOUSE_BUCKET_NAME = "warehouse";
  private static final NamingConventionTransformer namingResolver = new StandardNameTransformer();

  public static void stopAndCloseContainer(Startable container, String name) {
    container.stop();
    container.close();
    LOGGER.info("<== Closed {} docker container...", name);
  }

  public static void createS3WarehouseBucket(JsonNode config) {
    IcebergCatalogConfig catalogConfig = IcebergCatalogConfigFactory.fromJsonNodeConfig(config);
    AmazonS3 client = ((S3Config) catalogConfig.getStorageConfig()).getS3Client();
    Bucket bucket = client.createBucket(WAREHOUSE_BUCKET_NAME);
    LOGGER.info("Created s3 bucket: {}", bucket.getName());
    List<Bucket> buckets = client.listBuckets();
    LOGGER.info("All s3 buckets: {}", buckets);
  }

  public static List<JsonNode> retrieveRecords(JsonNode config, String namespace, String streamName)
      throws IOException {
    IcebergCatalogConfig catalogConfig = IcebergCatalogConfigFactory.fromJsonNodeConfig(config);
    Catalog catalog = catalogConfig.genCatalog();
    String dbName = namingResolver.getNamespace(
        isNotBlank(namespace) ? namespace : catalogConfig.defaultOutputDatabase()).toLowerCase();
    String tableName = namingResolver.getIdentifier("airbyte_raw_" + streamName).toLowerCase();
    LOGGER.info("Select data from:{}", tableName);
    Table table = catalog.loadTable(TableIdentifier.of(dbName, tableName));
    ArrayList<Record> records;
    try (CloseableIterable<Record> recordItr = IcebergGenerics.read(table).build()) {
      records = Lists.newArrayList(recordItr);
    }
    return records.stream()
        .sorted(Comparator.comparingLong(r -> offsetDataTimeToTimestamp((OffsetDateTime) r.getField(
            JavaBaseConstants.COLUMN_NAME_EMITTED_AT))))
        .map(r -> Jsons.deserialize((String) r.getField(JavaBaseConstants.COLUMN_NAME_DATA)))
        .collect(Collectors.toList());
  }

  private static long offsetDataTimeToTimestamp(OffsetDateTime offsetDateTime) {
    return Timestamp.valueOf(offsetDateTime.atZoneSameInstant(ZoneOffset.UTC).toLocalDateTime()).getTime();
  }

}
