/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static java.lang.String.format;
import static java.nio.charset.StandardCharsets.UTF_8;
import static java.util.UUID.randomUUID;
import static java.util.stream.Collectors.joining;
import static org.apache.iceberg.hadoop.Util.VERSION_HINT_FILENAME;
import static org.slf4j.LoggerFactory.getLogger;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.GetObjectRequest;
import com.amazonaws.services.s3.model.S3Object;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.avro.AvroConstants;
import io.airbyte.integrations.destination.s3.avro.AvroRecordFactory;
import io.airbyte.integrations.destination.s3.avro.JsonToAvroSchemaConverter;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.io.IOException;
import java.sql.Timestamp;
import java.util.UUID;
import org.apache.avro.Schema;
import org.apache.iceberg.parquet.ParquetSchemaUtil;
import org.apache.parquet.avro.AvroSchemaConverter;
import org.apache.parquet.schema.MessageType;
import org.slf4j.Logger;

/**
 * This implementation is similar to {@link StreamCopier}. The difference is that this
 * implementation creates Parquet staging file(s), instead of CSV ones.
 * <ul>
 * <li>1. Parquet writer writes data stream into tmp Iceberg table in
 * s3://bucket-name/bucket-path/namespace/schema/temp-Iceberg-table-name.</li>
 * <li>2. Creates(or modifies the schema of) the destination Iceberg table from the tmp Iceberg
 * table schema in Galaxy Amazon S3 Catalog based on the destination sync mode</li>
 * <li>3. Copies the tmp Iceberg table data into the destination Iceberg table in Amazon S3 Galaxy
 * Catalog.</li>
 * <li>5. Deletes the tmp Iceberg table.</li>
 * </ul>
 */
public class StarburstGalaxyS3StreamCopier
    extends StarburstGalaxyStreamCopier {

  private static final Logger LOGGER = getLogger(StarburstGalaxyS3StreamCopier.class);
  private final AmazonS3 s3Client;
  private final S3DestinationConfig s3Config;
  private final HadoopCatalogIcebergS3ParquetWriter icebergWriter;
  private final AvroRecordFactory avroRecordFactory;

  public StarburstGalaxyS3StreamCopier(final String stagingFolder,
                                       final String schema,
                                       final ConfiguredAirbyteStream configuredStream,
                                       final AmazonS3 s3Client,
                                       final JdbcDatabase database,
                                       final StarburstGalaxyDestinationConfig galaxyDestinationConfig,
                                       final StandardNameTransformer nameTransformer,
                                       final SqlOperations sqlOperations,
                                       final Timestamp uploadTime)
      throws Exception {
    super(stagingFolder, schema, configuredStream, database, galaxyDestinationConfig, nameTransformer, sqlOperations);
    this.s3Client = s3Client;
    this.s3Config = galaxyDestinationConfig.storageConfig().getS3DestinationConfigOrThrow();
    Schema avroSchema = getAvroSchema(configuredStream.getStream().getName(),
        configuredStream.getStream().getNamespace(), configuredStream.getStream().getJsonSchema());
    org.apache.iceberg.Schema icebergSchema = getIcebergSchema(avroSchema);
    this.icebergWriter = new HadoopCatalogIcebergS3ParquetWriter(
        galaxyDestinationConfig.storageConfig().getS3DestinationConfigOrThrow(), configuredStream, icebergSchema,
        this.schemaName, this.tmpTableName, uploadTime);
    this.avroRecordFactory = new AvroRecordFactory(avroSchema, AvroConstants.JSON_CONVERTER);
    LOGGER.info("[Stream {}] Tmp table {} location: {}", streamName, tmpTableName, getTmpTableLocation());
    LOGGER.info("[Stream {}] Iceberg schema: {}", streamName, icebergSchema);
    this.galaxySchema = convertIcebergSchemaToGalaxySchema(icebergSchema);
  }

  static org.apache.iceberg.Schema getIcebergSchema(Schema avroSchema) {
    MessageType parquetSchema = new AvroSchemaConverter().convert(avroSchema);
    return ParquetSchemaUtil.convert(parquetSchema);
  }

  static Schema getAvroSchema(String streamName, String namespace, JsonNode jsonSchema) {
    final JsonToAvroSchemaConverter schemaConverter = new JsonToAvroSchemaConverter();
    return schemaConverter.getAvroSchema(jsonSchema, streamName, namespace, true, true, false, true);
  }

  @Override
  public String prepareStagingFile() {
    return String.join("/", s3Config.getBucketPath(), stagingFolder);
  }

  @Override
  public void write(final UUID id, final AirbyteRecordMessage recordMessage, final String fileName) throws Exception {
    recordMessage.setEmittedAt(recordMessage.getEmittedAt() * 1000); // Corresponding Galaxy type expects micro precision.
    icebergWriter.write(avroRecordFactory.getAvroRecord(id, recordMessage));
  }

  @Override
  public void closeStagingUploader(final boolean hasFailed) throws Exception {
    icebergWriter.close(hasFailed);
  }

  @Override
  protected String getTmpTableLocation() {
    // Galaxy location privilege doesn't allow path starting with s3a
    String tmpTableLocation = icebergWriter.getTable().location().replace("s3a://", "s3://");
    LOGGER.info("[Stream {}] Tmp table location: {}", streamName, tmpTableLocation);
    return tmpTableLocation;
  }

  @Override
  protected String getTmpTableMetadataFileName()
      throws IOException {
    String tmpTableBasePath = icebergWriter.getTableStorageRelativePath();
    LOGGER.info("[Stream {}] Tmp table base path: {}", streamName, tmpTableBasePath);
    GetObjectRequest getObjectRequest = new GetObjectRequest(s3Config.getBucketName(),
        tmpTableBasePath + "/metadata/" + VERSION_HINT_FILENAME);
    S3Object object = s3Client.getObject(getObjectRequest);
    String currentMetadataFileVersion = new String(object.getObjectContent().readAllBytes(), UTF_8).strip();
    LOGGER.info("[Stream {}] Current metadata file version {}", streamName, currentMetadataFileVersion);
    String metadataJsonFile = "v" + currentMetadataFileVersion + ".metadata.json";
    String newMetadataJsonFileName =
        "0".repeat(5 - currentMetadataFileVersion.length()) + currentMetadataFileVersion + "-" + randomUUID() + ".metadata.json";

    // https://iceberg.apache.org/spec/#file-system-tables and
    // https://iceberg.apache.org/spec/#metastore-tables follows different metadata file naming
    // convention. Galaxy expect the version metadata file to always follow
    // https://iceberg.apache.org/spec/#metastore-tables convention.
    // Rename(copy) the metadata file name to follow Galaxy metadata file naming standards.
    s3Client.copyObject(
        s3Config.getBucketName(), tmpTableBasePath + "/metadata/" + metadataJsonFile,
        s3Config.getBucketName(), tmpTableBasePath + "/metadata/" + newMetadataJsonFileName);

    LOGGER.info("New metadata file: {}/{}/{}", tmpTableBasePath, "metadata", newMetadataJsonFileName);
    return newMetadataJsonFileName;
  }

  @Override
  public String generateMergeStatement(final String destTableName) {
    String fields = String.join(
        ", ",
        galaxySchema.columns().stream()
            .map(ColumnMetadata::name)
            .collect(joining(", ")));
    String insertData = format(
        "INSERT INTO %s.%s(%s) SELECT %s FROM %s.%s",
        quotedSchemaName,
        destTableName,
        fields,
        fields,
        quotedSchemaName,
        tmpTableName);
    LOGGER.info("[Stream {}] Insert source data into target: {}", streamName, insertData);
    return insertData;
  }

  @Override
  public void closeNonCurrentStagingFileWriters() throws Exception {
    icebergWriter.close(false);
  }

  @Override
  public String getCurrentFile() {
    return "";
  }

}
