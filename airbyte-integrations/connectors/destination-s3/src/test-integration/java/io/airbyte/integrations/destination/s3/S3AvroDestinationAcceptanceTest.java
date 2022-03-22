/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import static io.airbyte.integrations.standardtest.destination.DateTimeUtils.DATE;
import static io.airbyte.integrations.standardtest.destination.DateTimeUtils.DATE_TIME;

import com.amazonaws.services.s3.model.S3Object;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectReader;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.avro.AvroConstants;
import io.airbyte.integrations.destination.s3.avro.JsonFieldNameUpdater;
import io.airbyte.integrations.destination.s3.util.AvroRecordHelper;
import io.airbyte.integrations.standardtest.destination.DateTimeUtils;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.stream.StreamSupport;
import org.apache.avro.file.DataFileReader;
import org.apache.avro.file.SeekableByteArrayInput;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericData.Record;
import org.apache.avro.generic.GenericDatumReader;
import org.apache.commons.lang3.StringUtils;

public class S3AvroDestinationAcceptanceTest extends S3DestinationAcceptanceTest {

  protected S3AvroDestinationAcceptanceTest() {
    super(S3Format.AVRO);
  }

  @Override
  protected JsonNode getFormatConfig() {
    return Jsons.jsonNode(Map.of(
        "format_type", "Avro",
        "compression_codec", Map.of(
            "codec", "zstandard",
            "compression_level", 5,
            "include_checksum", true)));
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
  public boolean requiresDateTimeConversionForSync() {
    return true;
  }

  @Override
  public void convertDateTime(ObjectNode data, Map<String, String> dateTimeFieldNames) {
    var fields = StreamSupport.stream(Spliterators.spliteratorUnknownSize(data.fields(),
        Spliterator.ORDERED), false).toList();
    data.removeAll();
    fields.forEach(field -> convertField(field, field.getValue(), dateTimeFieldNames, data));
  }

  @Override
  protected void deserializeNestedObjects(List<AirbyteMessage> messages, List<AirbyteRecordMessage> actualMessages) {
    for (AirbyteMessage message : messages) {
      if (message.getType() == Type.RECORD) {
        var iterator = message.getRecord().getData().fieldNames();
        while (iterator.hasNext()) {
          var fieldName = iterator.next();
          if (message.getRecord().getData().get(fieldName).isContainerNode()) {
            message.getRecord().getData().get(fieldName).fieldNames().forEachRemaining(f -> {
              var data = message.getRecord().getData().get(fieldName).get(f);
              var wrappedData = String.format("{\"%s\":%s,\"_airbyte_additional_properties\":null}", f,
                  dateTimeFieldNames.containsKey(f) || !data.isTextual() ? data.asText() : StringUtils.wrap(data.asText(), "\""));
              try {
                ((ObjectNode) message.getRecord().getData()).set(fieldName, new ObjectMapper().readTree(wrappedData));
              } catch (JsonProcessingException e) {
                e.printStackTrace();
              }
            });
          }
        }
      }
    }
  }

  private void convertField(Entry<String, JsonNode> field, JsonNode fieldValue, Map<String, String> dateTimeFieldNames, ObjectNode data) {
    if (fieldValue.isContainerNode()) {
      var fields = StreamSupport.stream(Spliterators.spliteratorUnknownSize(fieldValue.fields(),
          Spliterator.ORDERED), false).toList();
      fields.forEach(f -> convertField(f, f.getValue(), dateTimeFieldNames, data));
    }
    var key = field.getKey();
    if (fieldValue.isContainerNode()) {
      var dataCopy = data.deepCopy();
      data.removeAll();
      data.set(key, dataCopy);
    } else if (dateTimeFieldNames.containsKey(key)) {
      switch (dateTimeFieldNames.get(key)) {
        case DATE_TIME -> data.put(key.toLowerCase(), DateTimeUtils.getEpochMicros(field.getValue().asText()));
        case DATE -> data.put(key.toLowerCase(), DateTimeUtils.getEpochDay(field.getValue().asText()));
      }
    } else {
      data.set(key.toLowerCase(), field.getValue());
    }
  }

}
