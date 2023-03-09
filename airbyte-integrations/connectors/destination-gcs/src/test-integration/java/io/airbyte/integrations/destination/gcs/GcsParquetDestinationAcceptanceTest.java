/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import com.amazonaws.services.s3.model.S3Object;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectReader;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.gcs.parquet.GcsParquetWriter;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.avro.AvroConstants;
import io.airbyte.integrations.destination.s3.avro.JsonFieldNameUpdater;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetWriter;
import io.airbyte.integrations.destination.s3.util.AvroRecordHelper;
import io.airbyte.integrations.standardtest.destination.ProtocolVersion;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.apache.avro.Schema.Type;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericData.Record;
import org.apache.hadoop.conf.Configuration;
import org.apache.parquet.avro.AvroReadSupport;
import org.apache.parquet.hadoop.ParquetReader;

public class GcsParquetDestinationAcceptanceTest extends GcsAvroParquetDestinationAcceptanceTest {

  public GcsParquetDestinationAcceptanceTest() {
    super(S3Format.PARQUET);
  }

  @Override
  public ProtocolVersion getProtocolVersion() {
    return ProtocolVersion.V1;
  }

  @Override
  protected JsonNode getFormatConfig() {
    return Jsons.jsonNode(Map.of(
        "format_type", "Parquet",
        "compression_codec", "GZIP"));
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new GcsAvroTestDataComparator();
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws IOException, URISyntaxException {
    final JsonFieldNameUpdater nameUpdater = AvroRecordHelper.getFieldNameUpdater(streamName, namespace, streamSchema);

    final List<S3ObjectSummary> objectSummaries = getAllSyncedObjects(streamName, namespace);
    final List<JsonNode> jsonRecords = new LinkedList<>();

    for (final S3ObjectSummary objectSummary : objectSummaries) {
      final S3Object object = s3Client.getObject(objectSummary.getBucketName(), objectSummary.getKey());
      final URI uri = new URI(String.format("s3a://%s/%s", object.getBucketName(), object.getKey()));
      final var path = new org.apache.hadoop.fs.Path(uri);
      final Configuration hadoopConfig = GcsParquetWriter.getHadoopConfig(config);

      try (final ParquetReader<GenericData.Record> parquetReader = ParquetReader.<GenericData.Record>builder(new AvroReadSupport<>(), path)
          .withConf(hadoopConfig)
          .build()) {
        final ObjectReader jsonReader = MAPPER.reader();
        GenericData.Record record;
        while ((record = parquetReader.read()) != null) {
          final byte[] jsonBytes = AvroConstants.JSON_CONVERTER.convertToJson(record);
          JsonNode jsonRecord = jsonReader.readTree(jsonBytes);
          jsonRecord = nameUpdater.getJsonWithOriginalFieldNames(jsonRecord);
          jsonRecords.add(AvroRecordHelper.pruneAirbyteJson(jsonRecord));
        }
      }
    }

    return jsonRecords;
  }

  @Override
  protected Map<String, Set<Type>> retrieveDataTypesFromPersistedFiles(final String streamName, final String namespace) throws Exception {

    final List<S3ObjectSummary> objectSummaries = getAllSyncedObjects(streamName, namespace);
    final Map<String, Set<Type>> resultDataTypes = new HashMap<>();

    for (final S3ObjectSummary objectSummary : objectSummaries) {
      final S3Object object = s3Client.getObject(objectSummary.getBucketName(), objectSummary.getKey());
      final URI uri = new URI(String.format("s3a://%s/%s", object.getBucketName(), object.getKey()));
      final var path = new org.apache.hadoop.fs.Path(uri);
      final Configuration hadoopConfig = S3ParquetWriter.getHadoopConfig(config);

      try (final ParquetReader<Record> parquetReader = ParquetReader.<GenericData.Record>builder(new AvroReadSupport<>(), path)
          .withConf(hadoopConfig)
          .build()) {
        GenericData.Record record;
        while ((record = parquetReader.read()) != null) {
          final Map<String, Set<Type>> actualDataTypes = getTypes(record);
          resultDataTypes.putAll(actualDataTypes);
        }
      }
    }

    return resultDataTypes;
  }

}
