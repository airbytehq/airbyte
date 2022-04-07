/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

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
import io.airbyte.integrations.destination.gcs.parquet.GcsParquetWriter;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.avro.AvroConstants;
import io.airbyte.integrations.destination.s3.avro.JsonFieldNameUpdater;
import io.airbyte.integrations.destination.s3.util.AvroRecordHelper;
import io.airbyte.integrations.standardtest.destination.DateTimeUtils;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import org.apache.avro.generic.GenericData;
import org.apache.commons.lang3.StringUtils;
import org.apache.hadoop.conf.Configuration;
import org.apache.parquet.avro.AvroReadSupport;
import org.apache.parquet.hadoop.ParquetReader;

public class GcsParquetDestinationAcceptanceTest extends GcsDestinationAcceptanceTest {

  protected GcsParquetDestinationAcceptanceTest() {
    super(S3Format.PARQUET);
  }

  @Override
  protected JsonNode getFormatConfig() {
    return Jsons.jsonNode(Map.of(
        "format_type", "Parquet",
        "compression_codec", "GZIP"));
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
  public boolean requiresDateTimeConversionForSync() {
    return true;
  }

  @Override
  public void convertDateTime(final ObjectNode data, final Map<String, String> dateTimeFieldNames) {
    for (final String path : dateTimeFieldNames.keySet()) {
      if (!data.at(path).isMissingNode() && DateTimeUtils.isDateTimeValue(data.at(path).asText())) {
        final var pathFields = new ArrayList<>(Arrays.asList(path.split("/")));
        pathFields.remove(0); // first element always empty string
        // if pathFields.size() == 1 -> /field else /field/nestedField..
        final var pathWithoutLastField = pathFields.size() == 1 ? "/" + pathFields.get(0)
            : "/" + String.join("/", pathFields.subList(0, pathFields.size() - 1));
        switch (dateTimeFieldNames.get(path)) {
          case DATE_TIME -> {
            if (pathFields.size() == 1) {
              data.put(pathFields.get(0).toLowerCase(),
                  (DateTimeUtils.getEpochMicros(data.get(pathFields.get(0)).asText()) / 1000)
                      * 1000);
            } else {
              ((ObjectNode) data.at(pathWithoutLastField)).put(
                  pathFields.get(pathFields.size() - 1),
                  (DateTimeUtils.getEpochMicros(data.at(path).asText()) / 1000) * 1000);
            }
          }
          case DATE -> {
            if (pathFields.size() == 1) {
              data.put(pathFields.get(0).toLowerCase(),
                  DateTimeUtils.getEpochDay(data.get(pathFields.get(0)).asText()));
            } else {
              ((ObjectNode) data.at(pathWithoutLastField)).put(pathFields.get(pathFields.size() - 1),
                  DateTimeUtils.getEpochDay((data.at(path).asText())));
            }
          }
        }
      }
    }
  }

  @Override
  protected void deserializeNestedObjects(final List<AirbyteMessage> messages, final List<AirbyteRecordMessage> actualMessages) {
    for (final AirbyteMessage message : messages) {
      if (message.getType() == Type.RECORD) {
        final var iterator = message.getRecord().getData().fieldNames();
        while (iterator.hasNext()) {
          final var fieldName = iterator.next();
          if (message.getRecord().getData().get(fieldName).isContainerNode()) {
            message.getRecord().getData().get(fieldName).fieldNames().forEachRemaining(f -> {
              final var data = message.getRecord().getData().get(fieldName).get(f);
              final var wrappedData = String.format("{\"%s\":%s,\"_airbyte_additional_properties\":null}", f,
                  dateTimeFieldNames.containsKey(f) || !data.isTextual() ? data.asText() : StringUtils.wrap(data.asText(), "\""));
              try {
                ((ObjectNode) message.getRecord().getData()).set(fieldName, new ObjectMapper().readTree(wrappedData));
              } catch (final JsonProcessingException e) {
                e.printStackTrace();
              }
            });
          }
        }
      }
    }
  }

}
