package io.airbyte.integrations.source.kafka.format;


import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static java.util.Map.entry;

public class Avro2JsonConvert {

    private ObjectMapper mapper = new ObjectMapper();

    /**
     * Mapping from avro to Json type
     * @link https://docs.airbyte.com/understanding-airbyte/json-avro-conversion/#conversion-rules
     */
    private static final Map<String, List<String>> AVRO_TO_JSON_DATA_TYPE_MAPPING = Map.ofEntries(
            entry("null", List.of("null")),
            entry("boolean", List.of("boolean", "null")),
            entry("int", List.of("integer", "null")),
            entry("long", List.of("integer", "null")),
            entry("float", List.of("number", "null")),
            entry("double", List.of("number", "null")),
            entry("bytes", List.of("string", "null")),
            entry("string", List.of("string", "null")),
            entry("record", List.of("object", "null")),
            entry("enum", List.of("string", "null")),
            entry("array", List.of("array", "null")),
            entry("map", List.of("object", "null")),
            entry("fixed", List.of("string", "null"))
    );


    private List<String> avroTypeToJsonType(String avroType) {
        List<String> jsonTypes = AVRO_TO_JSON_DATA_TYPE_MAPPING.get(avroType);
        if (jsonTypes == null) {
            throw new IllegalArgumentException("Unknown Avro type: " + avroType);
        }
        return jsonTypes;
    }

    public JsonNode convertoToAirbyteJson(String avroSchema) throws Exception {
        Map<String, Object> mapAvroSchema = mapper.readValue(avroSchema, new TypeReference<>() {
        });
        Map<String, Object> mapJsonSchema = convertoToAirbyteJson(mapAvroSchema);
        JsonNode jsonSchema = mapper.readValue(mapper.writeValueAsString(mapJsonSchema), JsonNode.class);

        return jsonSchema;
    }

    /**
     * Method to convert the avro schema in to Json schema in order to save the schema in the Airbyte Catalog
     * @link https://docs.airbyte.com/understanding-airbyte/json-avro-conversion/
     * @param avroSchema  Map<String, Object> map with Avro struct
     * @return Map<String, Object> map with Json struct
     * @throws Exception
     */
    public Map<String, Object> convertoToAirbyteJson(Map<String, Object> avroSchema) throws Exception {
        Map<String, Object> jsonSchema = new HashMap<>();
        List<Map<String, Object>> fields = (List<Map<String, Object>>) avroSchema.get("fields");
        for (Map<String, Object> field : fields) {
            String fieldName = (String) field.get("name");
            Object fieldSchema = null;
            List<Object> filedTypes = null;
            if (field.get("type") instanceof List) {
                List fieldType = (List<Object>) field.get("type");
                filedTypes = fieldType.stream().filter(x -> (x != null) && (!x.equals("null"))).toList();
                //Case when there is a list of type ex. ["null", "string"]
                if (filedTypes instanceof List) {
                    if (filedTypes.stream().filter(x -> x instanceof String).count() == 1) {
                        String singleType = (String) filedTypes.stream()
                                .findFirst()
                                .orElse(null);
                        fieldSchema = Map.of("type", avroTypeToJsonType(singleType));
                    } else if (filedTypes.stream().filter(x -> x instanceof String).count() > 1) {

                        List<Object> anyOfSchemas = new ArrayList<>();
                        filedTypes.forEach(type -> anyOfSchemas.add(Map.of("type", avroTypeToJsonType((String) type))));
                        fieldSchema = Map.of("anyOf", anyOfSchemas);
                    }
                } else {
                    Map<String, Object> mapType = (Map<String, Object>) removeNull(fieldType);
                    if (mapType.get("type").equals("array") && mapType.get("items") instanceof List) {
                        List<Object> typeList = (ArrayList<Object>) mapType.get("items");
                        Object items = removeNull(typeList);
                        if (items instanceof Map) {
                            //Case when there is a List of Object
                            fieldSchema = Map.of("type", avroTypeToJsonType("array"), "items", List.of(convertoToAirbyteJson((Map<String, Object>) items)));
                        } else {
                            //Case when there is a List of type
                            List<Map<String, List<String>>> types = typeList.stream().map(x -> Map.of("type", avroTypeToJsonType((String) x))).toList();
                            fieldSchema = Map.of("type", avroTypeToJsonType("array"), "items", types);
                        }
                    } else if (mapType.get("type").equals("array") && mapType.get("items") instanceof Map) {
                        //Case when there is a single Object
                        fieldSchema = Map.of("type", avroTypeToJsonType("array"), "items", convertoToAirbyteJson((Map<String, Object>) mapType.get("items")));
                    } else {
                        fieldSchema = convertoToAirbyteJson(mapType);
                    }

                }
            } else if (field.get("type") instanceof Map) {
                //Case when there are a list of Objetct not in the array
                Map<String, Object> fieldType = (Map<String, Object>) field.get("type");
                Map<String, Object> map3 = Stream.of(Map.of("type", new String[]{"object", "null"}), convertoToAirbyteJson(fieldType))
                        .flatMap(map -> map.entrySet().stream())
                        .collect(Collectors.toMap(
                                Map.Entry::getKey,
                                Map.Entry::getValue));
                fieldSchema = map3;
            } else if (field.get("type") instanceof List) {
                List<String> fieldTypes = (List<String>) field.get("type");
                List<Object> anyOfSchemas = new ArrayList<>();
                fieldTypes.forEach(type -> anyOfSchemas.add(avroTypeToJsonType(type)));
                for (String type : fieldTypes) {
                    if (!type.equals("fields")) {
                        continue;
                    }
                    anyOfSchemas.add(avroTypeToJsonType(type));
                }
                fieldSchema = Map.of("anyOf", anyOfSchemas);
            } else {
                String singleType = List.of((String) field.get("type")).stream()
                        .filter(type -> !"null".equals(type))
                        .findFirst()
                        .orElse(null);
                fieldSchema = Map.of("type", avroTypeToJsonType(singleType));
            }
            jsonSchema.put(fieldName, fieldSchema);
        }
        return jsonSchema;
    }

    /**
     * Remove null or "null" value present in the Type array
     * @param field
     * @return
     * @throws Exception
     */
    private static Object removeNull(List field) throws Exception {
        Optional<Object> fieldWithoutNull = field.stream().filter(x -> (x != null) && (!x.equals("null"))).findFirst();
        if (fieldWithoutNull.isEmpty()) {
            throw new Exception("Unknown Avro converter:" + field);
        }
        return fieldWithoutNull.get();
    }


}