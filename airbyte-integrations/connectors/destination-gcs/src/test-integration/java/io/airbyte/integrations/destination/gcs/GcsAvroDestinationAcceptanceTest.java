/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import com.amazonaws.services.s3.model.S3Object;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectReader;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.avro.AvroConstants;
import io.airbyte.integrations.destination.s3.avro.JsonFieldNameUpdater;
import io.airbyte.integrations.destination.s3.util.AvroRecordHelper;
import io.airbyte.integrations.standardtest.destination.ProtocolVersion;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.apache.avro.Schema.Type;
import org.apache.avro.file.DataFileReader;
import org.apache.avro.file.SeekableByteArrayInput;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericData.Record;
import org.apache.avro.generic.GenericDatumReader;

public class GcsAvroDestinationAcceptanceTest extends GcsAvroParquetDestinationAcceptanceTest {

  public GcsAvroDestinationAcceptanceTest() {
    super(S3Format.AVRO);
  }

  @Override
  protected JsonNode getFormatConfig() {
    return Jsons.deserialize("{\n"
        + "  \"format_type\": \"Avro\",\n"
        + "  \"compression_codec\": { \"codec\": \"no compression\", \"compression_level\": 5, \"include_checksum\": true }\n"
        + "}");
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
      throws Exception {
    final JsonFieldNameUpdater nameUpdater = AvroRecordHelper.getFieldNameUpdater(streamName, namespace, streamSchema);

    final List<S3ObjectSummary> objectSummaries = getAllSyncedObjects(streamName, namespace);
    final List<JsonNode> jsonRecords = new LinkedList<>();

    for (final S3ObjectSummary objectSummary : objectSummaries) {
      final S3Object object = s3Client.getObject(objectSummary.getBucketName(), objectSummary.getKey());
      try (final DataFileReader<Record> dataFileReader = new DataFileReader<>(
          new SeekableByteArrayInput(object.getObjectContent().readAllBytes()),
          new GenericDatumReader<>())) {
        final ObjectReader jsonReader = MAPPER.reader();
        while (dataFileReader.hasNext()) {
          final GenericData.Record record = dataFileReader.next();
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
      try (final DataFileReader<Record> dataFileReader = new DataFileReader<>(
          new SeekableByteArrayInput(object.getObjectContent().readAllBytes()),
          new GenericDatumReader<>())) {
        while (dataFileReader.hasNext()) {
          final GenericData.Record record = dataFileReader.next();
          final Map<String, Set<Type>> actualDataTypes = getTypes(record);
          resultDataTypes.putAll(actualDataTypes);
        }
      }
    }
    return resultDataTypes;
  }

  @Override
  public ProtocolVersion getProtocolVersion() {
    return ProtocolVersion.V1;
  }

}
