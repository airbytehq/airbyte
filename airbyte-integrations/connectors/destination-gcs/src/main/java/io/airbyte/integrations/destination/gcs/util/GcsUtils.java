/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.util;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.s3.avro.AvroConstants;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import javax.annotation.Nullable;
import org.apache.avro.LogicalTypes;
import org.apache.avro.Schema;
import org.apache.avro.Schema.Type;
import org.apache.avro.SchemaBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GcsUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(GcsUtils.class);

  public static final String NESTED_ARRAY_FIELD = "value";
  protected static final String PROPERTIES_FIELD = "properties";
  private static final String TYPE_FIELD = "type";
  private static final String FORMAT_FIELD = "format";

  public static Schema getDefaultAvroSchema(final String name,
                                            @Nullable final String namespace,
                                            final boolean appendAirbyteFields) {
    LOGGER.info("Default schema.");
    final String stdName = AvroConstants.NAME_TRANSFORMER.getIdentifier(name);
    SchemaBuilder.RecordBuilder<Schema> builder = SchemaBuilder.record(stdName);

    if (namespace != null) {
      builder = builder.namespace(namespace);
    }

    SchemaBuilder.FieldAssembler<Schema> assembler = builder.fields();

    Schema TIMESTAMP_MILLIS_SCHEMA = LogicalTypes.timestampMillis()
        .addToSchema(Schema.create(Schema.Type.LONG));
    Schema UUID_SCHEMA = LogicalTypes.uuid()
        .addToSchema(Schema.create(Schema.Type.STRING));

    if (appendAirbyteFields) {
      assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_AB_ID).type(UUID_SCHEMA).noDefault();
      assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)
          .type(TIMESTAMP_MILLIS_SCHEMA).noDefault();
    }
    assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_DATA).type().stringType().noDefault();

    return assembler.endRecord();
  }

  public static Schema getAvroSchema(JsonNode airbyteSchema,
                                     StandardNameTransformer nameTransformer,
                                     String name,
                                     @Nullable final String namespace,
                                     final boolean appendAirbyteFields) {
    final String stdName = AvroConstants.NAME_TRANSFORMER.getIdentifier(name);
    SchemaBuilder.RecordBuilder<Schema> builder = SchemaBuilder.record(stdName);

    if (namespace != null) {
      builder = builder.namespace(namespace);
    }

    final SchemaBuilder.FieldAssembler<Schema> assembler = builder.fields();

    final ObjectNode properties = (ObjectNode) airbyteSchema.get(PROPERTIES_FIELD);
    Jsons.keys(properties).forEach(fieldName -> {
      JsonNode fieldType = properties.get(fieldName);
      Schema.Type avroType = getAvroType(fieldType);
      assembler.name(nameTransformer.getIdentifier(fieldName)).type().optional().type(avroType.getName());
    });

    if (appendAirbyteFields)
      addAirbyteFields(assembler);

    return assembler.endRecord();
  }

  private static void addAirbyteFields(SchemaBuilder.FieldAssembler<Schema> assembler) {
    Schema TIMESTAMP_MILLIS_SCHEMA = LogicalTypes.timestampMillis()
        .addToSchema(Schema.create(Schema.Type.LONG));
    Schema UUID_SCHEMA = LogicalTypes.uuid()
        .addToSchema(Schema.create(Schema.Type.STRING));

    assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_AB_ID).type(UUID_SCHEMA).noDefault();
    assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)
        .type(TIMESTAMP_MILLIS_SCHEMA).noDefault();
  }

  private static Schema.Type getAvroType(JsonNode fieldType) {
    JsonNode type = fieldType.get(TYPE_FIELD);
    Map<String, Type> typeMap = getTypeMap();
    Schema.Type schemaType;
    if (type == null) {
      schemaType = Type.STRING;
      LOGGER.info("Types null");
    } else if (type.isTextual()) {
      schemaType = typeMap.get(type.asText());
      LOGGER.info("Types r : " + schemaType);

      if (schemaType == null)
        schemaType = Type.STRING;
    } else if (type.isArray()) {
      List<String> types = MoreIterators.toList(type.elements()).stream().map(JsonNode::asText).collect(Collectors.toList());
      LOGGER.info("Types: " + types);
      schemaType = Type.STRING;
    } else {
      LOGGER.info("Types else ");
      schemaType = Type.STRING;
    }
    LOGGER.info("Types result : " + schemaType + " from " + fieldType);
    return schemaType;
  }

  private static Map<String, Type> getTypeMap() {
    Map<String, Type> map = new HashMap<>();
    map.put("string", Type.STRING);
    map.put("number", Type.DOUBLE);
    map.put("integer", Type.INT);
    map.put("object", Type.RECORD);
    map.put("array", Type.ARRAY);
    map.put("boolean", Type.BOOLEAN);
    return map;
  }

}
