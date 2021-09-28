/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.UUID;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import tech.allegro.schema.json2avro.converter.JsonAvroConverter;

public class AvroRecordFactory {

  private static final ObjectMapper MAPPER = MoreMappers.initMapper();
  private static final ObjectWriter WRITER = MAPPER.writer();

  private final Schema schema;
  private final JsonFieldNameUpdater nameUpdater;
  private final JsonAvroConverter converter = new JsonAvroConverter();

  public AvroRecordFactory(Schema schema, JsonFieldNameUpdater nameUpdater) {
    this.schema = schema;
    this.nameUpdater = nameUpdater;
  }

  public GenericData.Record getAvroRecord(UUID id, AirbyteRecordMessage recordMessage) throws JsonProcessingException {
    JsonNode inputData = recordMessage.getData();
    inputData = nameUpdater.getJsonWithStandardizedFieldNames(inputData);

    ObjectNode jsonRecord = MAPPER.createObjectNode();
    jsonRecord.put(JavaBaseConstants.COLUMN_NAME_AB_ID, id.toString());
    jsonRecord.put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, recordMessage.getEmittedAt());
    jsonRecord.setAll((ObjectNode) inputData);

    return converter.convertToGenericDataRecord(WRITER.writeValueAsBytes(jsonRecord), schema);
  }

}
