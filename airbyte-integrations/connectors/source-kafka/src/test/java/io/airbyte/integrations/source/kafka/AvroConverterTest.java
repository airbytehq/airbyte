/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.integrations.source.kafka.format.Avro2JsonConvert;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class AvroConverterTest {

    ObjectMapper mapper = new ObjectMapper();

    String avroSimpleSchema = """
            {
                "type": "record",
                "name": "sampleAvro",
                "namespace": "AVRO",
                "fields": [
                    {"name": "name", "type": "string"},
                    {"name": "age", "type": ["int", "null"]},
                    {"name": "address", "type": ["float", "null"]},
                    {"name": "street", "type": "float"},
                    {"name": "valid", "type": "boolean"}
                ]
            }
                """;

    String jsonSimpleSchema = """
            {"address": {"type": ["number", "null"]},
              "age": {"type": ["integer", "null"]},
              "name": {"type": ["string", "null"]},
              "street": {"type": ["number", "null"]},
              "valid": {"type": ["boolean", "null"]}
            }
              
             """;


    String avroNestedRecordsSchema = """
              {
                "type": "record",
                "name": "sampleAvroNested",
                "namespace": "AVRO",
                "fields": [
                    {"name": "lastname", "type": "string"},
                    {"name": "address","type": {
                                    "type" : "record",
                                    "name" : "AddressUSRecord",
                                    "fields" : [
                                        {"name": "streetaddress", "type": "string"},
                                        {"name": "city", "type": "string"}
                                    ]
                                }
                    }
                ]
            }
                      """;


    String jsonNestedRecordSchema = """
             {
                "address":{
                   "type":["object", "null"],
                   "city":{
                        "type":[ "string","null"]
                         },
                   "streetaddress":{
                    "type":["string","null"]
                   }
                },
                "lastname":{
                "type":["string","null"]
                }
             }
            """;


    String avroWithArraySchema = """
            {
              "type": "record",
              "fields": [
                {
                  "name": "identifier",
                  "type": [
                    null,
                    {
                      "type": "array",
                      "items": ["null", "string"]
                    }
                  ]
                }
              ]
            }
                      
            """;

    String jsonWithArraySchema = """
            {
            "identifier": {
                  "type": ["array", "null"],
                  "items" :  [
                    {"type":["null"]},
                    {"type":["string","null"]}
                  ]
                }
                }
            """;

    String avroWithArrayAndRecordSchema = """
            {
                "type": "record",
                "name": "TestObject",
                "namespace": "ca.dataedu",
                "fields": [{
                    "name": "array_field",
                    "type": ["null", {
                        "type": "array",
                        "items": ["null", {
                            "type": "record",
                            "name": "Array_field",
                            "fields": [{
                                "name": "id",
                                "type": ["null", {
                                    "type": "record",
                                    "name": "Id",
                                    "fields": [{
                                        "name": "id_part_1",
                                        "type": ["null", "int"],
                                        "default": null
                                    }]
                                }],
                                "default": null
                            }]
                        }]
                    }],
                    "default": null
                }]
            }
                      
            """;


    String jsonWithArrayAndRecordSchema = """
            {
              "array_field": {
                "type": ["array", "null"],
                "items": [
                  {
                      "id": {
                          "id_part_1": { "type": ["integer", "null"] }
                      }
                    }
                ]
              }
            }
            """;


    String avroWithArrayAndNestedRecordSchema = """
            {
                "type": "record",
                "name": "TestObject",
                "namespace": "ca.dataedu",
                "fields": [{
                    "name": "array_field",
                    "type": ["null", {
                        "type": "array",
                        "items": ["null", {
                            "type": "record",
                            "name": "Array_field",
                            "fields": [{
                                "name": "id",
                                "type": ["null", {
                                    "type": "record",
                                    "name": "Id",
                                    "fields": [{
                                        "name": "id_part_1",
                                        "type": ["null", "int"],
                                        "default": null
                                    }, {
                                        "name": "id_part_2",
                                        "type": ["null", "string"],
                                        "default": null
                                    }]
                                }],
                                "default": null
                            }, {
                                "name": "message",
                                "type": ["null", "string"],
                                "default": null
                            }]
                        }]
                    }],
                    "default": null
                }]
            }
                      
            """;

    String jsonWithArrayAndNestedRecordSchema = """
            {
              "array_field": {
                "type": ["array", "null"],
                "items": [
                  {
                      "id": {
                          "id_part_1": { "type": ["integer", "null"] },
                          "id_part_2": { "type": ["string", "null"] }
                      },
                      "message" : {"type": [ "string", "null"] }
                  }
                ]
              }
            }
            """;


    String avroWithCombinedRestrictionsSchema = """
                {
                "type": "record",
                "name": "sampleAvro",
                "namespace": "AVRO",
                "fields": [
                    {"name": "name", "type": "string"},
                    {"name": "age", "type": ["int", "null"]},
                    {"name": "address", "type": ["float", "string", "null"]}
                ]
            }
                """;

    String jsonWithCombinedRestrictionsSchema = """
            {
             "address": {"anyOf": [ 
                           {"type": ["string", "null"]},
                           {"type": ["number", "null"]}
                         ]},
              "age": {"type": ["integer", "null"]},
              "name": {"type": ["string", "null"]}
            }
              
             """;


    @Test
    public void testConverterAvroSimpleSchema() throws Exception {
        Map<String, Object> jsonSchema = mapper.readValue(avroSimpleSchema, new TypeReference<Map<String, Object>>() {
        });
        Avro2JsonConvert converter = new Avro2JsonConvert();
        Map<String, Object> airbyteSchema = converter.convertoToAirbyteJson(jsonSchema);
        JsonNode expect = mapper.readTree(jsonSimpleSchema);
        JsonNode actual = mapper.readValue(mapper.writeValueAsString(airbyteSchema), JsonNode.class);
        assertEquals(expect, actual);
    }

    @Test
    public void testConverterAvroNestedSchema() throws Exception {
        Map<String, Object> jsonSchema = mapper.readValue(avroNestedRecordsSchema, new TypeReference<Map<String, Object>>() {
        });
        Avro2JsonConvert converter = new Avro2JsonConvert();
        Map<String, Object> airbyteSchema = converter.convertoToAirbyteJson(jsonSchema);
        JsonNode expect = mapper.readTree(jsonNestedRecordSchema);
        System.out.println(mapper.writeValueAsString(airbyteSchema));
        JsonNode actual = mapper.readValue(mapper.writeValueAsString(airbyteSchema), JsonNode.class);

        System.out.println(mapper.writeValueAsString(jsonSchema));


        assertEquals(expect, actual);
    }

    @Test
    public void testConverterAvroWithArray() throws Exception {

        Map<String, Object> jsonSchema = mapper.readValue(avroWithArraySchema, new TypeReference<Map<String, Object>>() {
        });
        Avro2JsonConvert converter = new Avro2JsonConvert();
        Map<String, Object> airbyteSchema = converter.convertoToAirbyteJson(jsonSchema);
        JsonNode expect = mapper.readTree(jsonWithArraySchema);
        System.out.println(mapper.writeValueAsString(airbyteSchema));
        JsonNode actual = mapper.readValue(mapper.writeValueAsString(airbyteSchema), JsonNode.class);

        System.out.println(mapper.writeValueAsString(jsonSchema));


        assertEquals(expect, actual);
    }


    @Test
    public void testConverterAvroWithArrayComplex() throws Exception {

        Map<String, Object> jsonSchema = mapper.readValue(avroWithArrayAndRecordSchema, new TypeReference<Map<String, Object>>() {
        });
        Avro2JsonConvert converter = new Avro2JsonConvert();
        Map<String, Object> airbyteSchema = converter.convertoToAirbyteJson(jsonSchema);
        JsonNode expect = mapper.readTree(jsonWithArrayAndRecordSchema);
        System.out.println(mapper.writeValueAsString(airbyteSchema));
        JsonNode actual = mapper.readValue(mapper.writeValueAsString(airbyteSchema), JsonNode.class);

        System.out.println(mapper.writeValueAsString(jsonSchema));


        assertEquals(expect, actual);
    }


    @Test
    public void testConverterAvroWithCombinedRestrictions() throws Exception {

        Map<String, Object> jsonSchema = mapper.readValue(avroWithCombinedRestrictionsSchema, new TypeReference<Map<String, Object>>() {
        });
        Avro2JsonConvert converter = new Avro2JsonConvert();
        Map<String, Object> airbyteSchema = converter.convertoToAirbyteJson(jsonSchema);
        JsonNode expect = mapper.readTree(jsonWithCombinedRestrictionsSchema);
        System.out.println(mapper.writeValueAsString(airbyteSchema));
        JsonNode actual = mapper.readValue(mapper.writeValueAsString(airbyteSchema), JsonNode.class);

        System.out.println(mapper.writeValueAsString(jsonSchema));


        assertEquals(expect, actual);
    }


    @Test
    public void testConverterAvroWithArrayComplex2() throws Exception {

        Map<String, Object> jsonSchema = mapper.readValue(avroWithArrayAndNestedRecordSchema, new TypeReference<Map<String, Object>>() {
        });
        Avro2JsonConvert converter = new Avro2JsonConvert();
        Map<String, Object> airbyteSchema = converter.convertoToAirbyteJson(jsonSchema);
        JsonNode expect = mapper.readTree(jsonWithArrayAndNestedRecordSchema);
        System.out.println(mapper.writeValueAsString(airbyteSchema));
        JsonNode actual = mapper.readValue(mapper.writeValueAsString(airbyteSchema), JsonNode.class);

        System.out.println(mapper.writeValueAsString(jsonSchema));


        assertEquals(expect, actual);
    }


}
