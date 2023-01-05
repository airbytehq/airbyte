/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.JsonSerializer;
import com.fasterxml.jackson.databind.SerializerProvider;
import java.io.IOException;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;

public class DynamodbSchemaSerializer extends JsonSerializer<AttributeValue> {

  @Override
  public void serialize(AttributeValue value, JsonGenerator gen, SerializerProvider serializers) throws IOException {
    switch (value.type()) {
      case S -> {
        gen.writeStartObject();

        gen.writeFieldName("type");
        gen.writeArray(new String[] {"null", "string"}, 0, 2);

        gen.writeEndObject();
      }
      case N -> {

        gen.writeStartObject();

        gen.writeFieldName("type");

        try {
          Long.parseLong(value.n());
          gen.writeArray(new String[] {"null", "integer"}, 0, 2);
        } catch (NumberFormatException e) {
          gen.writeArray(new String[] {"null", "number"}, 0, 2);
        }

        gen.writeEndObject();

      }
      case B -> {
        gen.writeStartObject();

        gen.writeFieldName("type");
        gen.writeArray(new String[] {"null", "string"}, 0, 2);

        gen.writeStringField("contentEncoding", "base64");

        gen.writeEndObject();
      }
      case SS -> {
        gen.writeStartObject();

        gen.writeFieldName("type");
        gen.writeArray(new String[] {"null", "array"}, 0, 2);

        gen.writeObjectFieldStart("items");

        gen.writeFieldName("type");
        gen.writeArray(new String[] {"null", "string"}, 0, 2);

        gen.writeEndObject();

        gen.writeEndObject();
      }
      case NS -> {
        gen.writeStartObject();

        gen.writeFieldName("type");
        gen.writeArray(new String[] {"null", "array"}, 0, 2);

        gen.writeObjectFieldStart("items");

        gen.writeFieldName("type");
        // array can contain mixed integer and decimal values
        gen.writeArray(new String[] {"null", "number"}, 0, 2);

        gen.writeEndObject();

        gen.writeEndObject();
      }
      case BS -> {
        gen.writeStartObject();

        gen.writeFieldName("type");
        gen.writeArray(new String[] {"null", "array"}, 0, 2);

        gen.writeObjectFieldStart("items");

        gen.writeFieldName("type");
        gen.writeArray(new String[] {"null", "string"}, 0, 2);

        gen.writeStringField("contentEncoding", "base64");

        gen.writeEndObject();

        gen.writeEndObject();
      }
      case M -> {
        gen.writeStartObject();

        gen.writeFieldName("type");
        gen.writeArray(new String[] {"null", "object"}, 0, 2);

        gen.writeObjectFieldStart("properties");

        for (var attr : value.m().entrySet()) {
          gen.writeFieldName(attr.getKey());
          // recursively iterate over nested attributes and create json schema fields
          serialize(attr.getValue(), gen, serializers);
        }

        gen.writeEndObject();

        gen.writeEndObject();
      }
      case L -> {
        // TODO (itaseski) perform deduplication on same type schema elements

        gen.writeStartObject();

        gen.writeFieldName("type");
        gen.writeArray(new String[] {"null", "array"}, 0, 2);

        gen.writeObjectFieldStart("items");

        gen.writeArrayFieldStart("anyOf");

        // recursively iterate over nested attributes and create json schema fields
        for (var attr : value.l()) {
          serialize(attr, gen, serializers);
        }

        gen.writeEndArray();

        gen.writeEndObject();

        gen.writeEndObject();
      }
      case BOOL -> {
        gen.writeStartObject();

        gen.writeFieldName("type");
        gen.writeArray(new String[] {"null", "boolean"}, 0, 2);

        gen.writeEndObject();
      }
      case NUL -> {
        gen.writeStartObject();
        gen.writeStringField("type", "null");
        gen.writeEndObject();
      }
      case UNKNOWN_TO_SDK_VERSION -> {
        // ignore unknown fields
      }
    }
  }

}
