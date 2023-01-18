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

class DynamodbSchemaSerializerTest {

  private ObjectMapper schemaObjectMapper;

  @BeforeEach
  void setup() {
    SimpleModule module = new SimpleModule();
    module.addSerializer(AttributeValue.class, new DynamodbSchemaSerializer());
    this.schemaObjectMapper = new ObjectMapper()
        .registerModule(module)
        .configure(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS, true)
        .configure(SerializationFeature.INDENT_OUTPUT, true);
  }

  @Test
  void serializeAttributeValueToJsonSchema() throws JsonProcessingException, JSONException {

    Map<String, AttributeValue> items = Map.of(
        "sAttribute", AttributeValue.builder().s("string").build(),
        "nAttribute", AttributeValue.builder().n("123").build(),
        "bAttribute",
        AttributeValue.builder().b(SdkBytes.fromByteArray("byteArray".getBytes(StandardCharsets.UTF_8))).build(),
        "ssAttribute", AttributeValue.builder().ss("string1", "string2").build(),
        "nsAttribute", AttributeValue.builder().ns("125", "126").build(),
        "bsAttribute", AttributeValue.builder().bs(
            SdkBytes.fromByteArray("byteArray1".getBytes(StandardCharsets.UTF_8)),
            SdkBytes.fromByteArray("byteArray2".getBytes(StandardCharsets.UTF_8))).build(),
        "lAttribute", AttributeValue.builder().l(
            AttributeValue.builder().s("string3").build(),
            AttributeValue.builder().n("12.5").build()).build(),
        "mAttribute", AttributeValue.builder().m(Map.of(
            "attr1", AttributeValue.builder().s("string4").build(),
            "attr2", AttributeValue.builder().s("number4").build())).build(),
        "boolAttribute", AttributeValue.builder().bool(false).build(),
        "nulAttribute", AttributeValue.builder().nul(true).build()

    );

    var jsonSchema = schemaObjectMapper.writeValueAsString(items);

    JSONAssert.assertEquals(jsonSchema, """
                                         {
                                        	"bAttribute": {
                                        		"type": ["null", "string"],
                                        		"contentEncoding": "base64"
                                        	},
                                        	"boolAttribute": {
                                        		"type": ["null", "boolean"]
                                        	},
                                        	"bsAttribute": {
                                        		"type": ["null", "array"],
                                        		"items": {
                                        			"type": ["null", "string"],
                                        			"contentEncoding": "base64"
                                        		}
                                        	},
                                        	"lAttribute": {
                                        		"type": ["null", "array"],
                                        		"items": {
                                        			"anyOf": [{
                                        				"type": ["null", "string"]
                                        			}, {
                                        				"type": ["null", "number"]
                                        			}]
                                        		}
                                        	},
                                        	"mAttribute": {
                                        		"type": ["null", "object"],
                                        		"properties": {
                                        			"attr2": {
                                        				"type": ["null", "string"]
                                        			},
                                        			"attr1": {
                                        				"type": ["null", "string"]
                                        			}
                                        		}
                                        	},
                                        	"nAttribute": {
                                        		"type": ["null", "integer"]
                                        	},
                                        	"nsAttribute": {
                                        		"type": ["null", "array"],
                                        		"items": {
                                        			"type": ["null", "number"]
                                        		}
                                        	},
                                        	"nulAttribute": {
                                        		"type": "null"
                                        	},
                                        	"sAttribute": {
                                        		"type": ["null", "string"]
                                        	},
                                        	"ssAttribute": {
                                        		"type": ["null", "array"],
                                        		"items": {
                                        			"type": ["null", "string"]
                                        		}
                                        	}
                                        }
                                        """, true);

  }

}
