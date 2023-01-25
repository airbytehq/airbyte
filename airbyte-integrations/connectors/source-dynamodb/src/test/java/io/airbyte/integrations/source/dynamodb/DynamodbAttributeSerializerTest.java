/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.module.SimpleModule;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import org.json.JSONException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.skyscreamer.jsonassert.JSONAssert;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;

class DynamodbAttributeSerializerTest {

  private ObjectMapper attributeObjectMapper;

  @BeforeEach
  void setup() {
    SimpleModule module = new SimpleModule();
    module.addSerializer(AttributeValue.class, new DynamodbAttributeSerializer());
    this.attributeObjectMapper = new ObjectMapper()
        .registerModule(module)
        .configure(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS, true)
        .configure(SerializationFeature.INDENT_OUTPUT, true);
  }

  @Test
  void serializeAttributeValueToJson() throws JSONException, JsonProcessingException {

    Map<String, AttributeValue> items = Map.of(
        "sAttribute", AttributeValue.builder().s("string").build(),
        "nAttribute", AttributeValue.builder().n("123").build(),
        "bAttribute",
        AttributeValue.builder().b(SdkBytes.fromByteArray("byteArray".getBytes(StandardCharsets.UTF_8))).build(),
        "ssAttribute", AttributeValue.builder().ss("string1", "string2").build(),
        "nsAttribute", AttributeValue.builder().ns("12.5", "25.5").build(),
        "bsAttribute", AttributeValue.builder().bs(
            SdkBytes.fromByteArray("byteArray1".getBytes(StandardCharsets.UTF_8)),
            SdkBytes.fromByteArray("byteArray2".getBytes(StandardCharsets.UTF_8))).build(),
        "lAttribute", AttributeValue.builder().l(
            AttributeValue.builder().s("string3").build(),
            AttributeValue.builder().n("125").build()).build(),
        "mAttribute", AttributeValue.builder().m(Map.of(
            "attr1", AttributeValue.builder().s("string4").build(),
            "attr2", AttributeValue.builder().s("string5").build())).build(),
        "boolAttribute", AttributeValue.builder().bool(false).build(),
        "nulAttribute", AttributeValue.builder().nul(true).build());

    var jsonNode = attributeObjectMapper.writeValueAsString(items);

    JSONAssert.assertEquals(jsonNode, """
                                       {
                                           "bAttribute": "Ynl0ZUFycmF5",
                                           "boolAttribute": false,
                                           "bsAttribute": ["Ynl0ZUFycmF5MQ==", "Ynl0ZUFycmF5Mg=="],
                                           "lAttribute": ["string3", 125],
                                           "mAttribute": {
                                               "attr1": "string4",
                                               "attr2": "string5"
                                           },
                                           "nAttribute": 123,
                                           "nsAttribute": [12.5, 25.5],
                                           "nulAttribute": null,
                                           "sAttribute": "string",
                                           "ssAttribute": ["string1", "string2"]
                                       }
                                      """, true);
  }

}
