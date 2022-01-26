/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import static io.airbyte.integrations.standardtest.destination.DateTimeUtils.DATE;
import static io.airbyte.integrations.standardtest.destination.DateTimeUtils.DATE_TIME;

import com.amazonaws.services.s3.model.S3Object;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectReader;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.avro.AvroConstants;
import io.airbyte.integrations.destination.s3.avro.JsonFieldNameUpdater;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetWriter;
import io.airbyte.integrations.destination.s3.util.AvroRecordHelper;
import io.airbyte.integrations.standardtest.destination.DateTimeUtils;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.stream.StreamSupport;
import org.apache.avro.generic.GenericData;
import org.apache.hadoop.conf.Configuration;
import org.apache.parquet.avro.AvroReadSupport;
import org.apache.parquet.hadoop.ParquetReader;

public class S3ParquetDestinationAcceptanceTest extends S3DestinationAcceptanceTest {

  protected S3ParquetDestinationAcceptanceTest() {
    super(S3Format.PARQUET);
  }

  @Override
  protected JsonNode getFormatConfig() {
    return Jsons.deserialize("{\n"
        + "  \"format_type\": \"Parquet\",\n"
        + "  \"compression_codec\": \"GZIP\"\n"
        + "}");
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
      final Configuration hadoopConfig = S3ParquetWriter.getHadoopConfig(config);

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
  public boolean requiresDateTimeConversionForSync() {
    return true;
  }

  @Override
  public void convertDateTime(ObjectNode data, Map<String, String> dateTimeFieldNames) {
    var fields = StreamSupport.stream(Spliterators.spliteratorUnknownSize(data.fields(),
        Spliterator.ORDERED), false).toList();
    data.removeAll();
    fields.forEach(field -> {
      var key = field.getKey();
      if (dateTimeFieldNames.containsKey(key)) {
        switch (dateTimeFieldNames.get(key)) {
          case DATE_TIME -> data.put(key.toLowerCase(), DateTimeUtils.getEpochMicros(field.getValue().asText()));
          case DATE -> data.put(key.toLowerCase(), DateTimeUtils.getEpochDay(field.getValue().asText()));
        }
      } else {
        data.set(key.toLowerCase(), field.getValue());
      }
    });
  }

}
