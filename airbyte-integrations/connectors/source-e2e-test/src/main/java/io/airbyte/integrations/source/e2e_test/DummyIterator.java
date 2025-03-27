/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.fasterxml.jackson.module.afterburner.AfterburnerModule;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;

public class DummyIterator implements AutoCloseableIterator<AirbyteMessage> {

  public static final ObjectMapper OBJECT_MAPPER = initMapper();
  public static final long MAX_RECORDS = 50_000_000;
  private static final String STREAM = "stream1";
  private static final String FIELD_1 = "field1";
  private static final String FIELD_2 = "field2";
  private static final String FIELD_3 = "field3";
  private static final String FIELD_4 = "field4";
  private static final String FIELD_5 = "field5";
  private static final String STRING_VALUE = "valuevaluevaluevaluevalue1";

  private final AtomicLong counter = new AtomicLong(0);

  private static final Map<String, String> CONSTANT_DATA = createConstantData();

  private static final JsonNode CONSTANT_JSON_DATA = OBJECT_MAPPER.valueToTree(CONSTANT_DATA);

  private static final AirbyteMessage CONSTANT_MESSAGE = new AirbyteMessage()
      .withType(AirbyteMessage.Type.RECORD)
      .withRecord(
          new AirbyteRecordMessage()
              .withStream(STREAM)
              .withEmittedAt(Instant.now().toEpochMilli())
              .withData(CONSTANT_JSON_DATA));

  private static Map<String, String> createConstantData() {
    Map<String, String> data = new HashMap<>();
    data.put(FIELD_1, STRING_VALUE);
    data.put(FIELD_2, STRING_VALUE);
    data.put(FIELD_3, STRING_VALUE);
    data.put(FIELD_4, STRING_VALUE);
    data.put(FIELD_5, STRING_VALUE);
    return data;
  }

  @Override
  public boolean hasNext() {
    return counter.get() <= MAX_RECORDS;
  }

  @Override
  public AirbyteMessage next() {
    counter.getAndIncrement();
    return CONSTANT_MESSAGE;
  }

  @Override
  public void close() {
    System.out.println("Closing iterator...");
  }

  public static ObjectMapper initMapper() {
    return configure(new ObjectMapper());
  }

  public static ObjectMapper configure(final ObjectMapper objectMapper) {
    if (objectMapper != null) {
      objectMapper
          .enable(MapperFeature.ACCEPT_CASE_INSENSITIVE_ENUMS)
          .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
          .configure(JsonGenerator.Feature.WRITE_BIGDECIMAL_AS_PLAIN, true)
          .registerModule(new JavaTimeModule())
          .registerModule(new AfterburnerModule());
    }
    return objectMapper;
  }

}
