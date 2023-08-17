/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.TypingAndDedupingFlag;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.util.UUID;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import tech.allegro.schema.json2avro.converter.JsonAvroConverter;

public class AvroRecordFactory {

  private static final ObjectMapper MAPPER = MoreMappers.initMapper();
  private static final ObjectWriter WRITER = MAPPER.writer();

  private final Schema schema;
  private final JsonAvroConverter converter;

  public AvroRecordFactory(final Schema schema, final JsonAvroConverter converter) {
    this.schema = schema;
    this.converter = converter;
  }

  public GenericData.Record getAvroRecord(final UUID id, final AirbyteRecordMessage recordMessage) throws JsonProcessingException {
    final ObjectNode jsonRecord = MAPPER.createObjectNode();
    if (TypingAndDedupingFlag.isDestinationV2()) {
      jsonRecord.put(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID, id.toString());
      jsonRecord.put(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT, recordMessage.getEmittedAt());
      jsonRecord.put(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT, (Long) null);
    } else {
      jsonRecord.put(JavaBaseConstants.COLUMN_NAME_AB_ID, id.toString());
      jsonRecord.put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, recordMessage.getEmittedAt());
    }
    jsonRecord.setAll((ObjectNode) recordMessage.getData());

    return converter.convertToGenericDataRecord(WRITER.writeValueAsBytes(jsonRecord), schema);
  }

  public GenericData.Record getAvroRecord(JsonNode formattedData) throws JsonProcessingException {
    var bytes = WRITER.writeValueAsBytes(formattedData);
    return converter.convertToGenericDataRecord(bytes, schema);
  }

}
