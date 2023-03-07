/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.JsonSerializer;
import com.fasterxml.jackson.databind.SerializerProvider;
import java.io.IOException;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;

public class DynamodbAttributeSerializer extends JsonSerializer<AttributeValue> {

  @Override
  public void serialize(AttributeValue value, JsonGenerator gen, SerializerProvider serializers) throws IOException {
    switch (value.type()) {
      case S -> gen.writeString(value.s());
      case N -> {
        try {
          Long.parseLong(value.n());
          gen.writeNumber(Long.parseLong(value.n()));
        } catch (NumberFormatException e) {
          gen.writeNumber(Double.parseDouble(value.n()));
        }
      }
      case B -> gen.writeBinary(value.b().asByteArray());
      case SS -> {
        gen.writeStartArray();
        for (var str : value.ss()) {
          gen.writeString(str);
        }
        gen.writeEndArray();
      }
      case NS -> {
        gen.writeStartArray();
        for (var str : value.ns()) {
          gen.writeNumber(str);
        }
        gen.writeEndArray();
      }
      case BS -> {
        gen.writeStartArray();
        for (var sb : value.bs()) {
          gen.writeBinary(sb.asByteArray());
        }
        gen.writeEndArray();
      }
      case M -> {
        gen.writeStartObject();
        for (var attr : value.m().entrySet()) {
          gen.writeFieldName(attr.getKey());
          serialize(attr.getValue(), gen, serializers);
        }
        gen.writeEndObject();
      }
      case L -> {
        gen.writeStartArray();
        for (var attr : value.l()) {
          serialize(attr, gen, serializers);
        }
        gen.writeEndArray();
      }
      case BOOL -> gen.writeBoolean(value.bool());
      case NUL -> gen.writeNull();
      case UNKNOWN_TO_SDK_VERSION -> {
        // ignore unknown fields
      }
    }
  }

}
