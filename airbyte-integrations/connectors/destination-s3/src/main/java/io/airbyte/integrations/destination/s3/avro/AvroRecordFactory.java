/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
