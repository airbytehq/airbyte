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

package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Field.Builder;
import com.google.cloud.bigquery.Field.Mode;
import com.google.cloud.bigquery.FieldList;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDenormalizedDestination extends BigQueryDestination {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDenormalizedDestination.class);

  protected static final String PROPERTIES_FIELD = "properties";
  protected static final String NESTED_ARRAY_FIELD = "value";
  private static final String TYPE_FIELD = "type";

  @Override
  protected String getTargetTableName(String streamName) {
    // This BigQuery destination does not write to a staging "raw" table but directly to a normalized
    // table
    return getNamingResolver().getIdentifier(streamName);
  }

  @Override
  protected AirbyteMessageConsumer getRecordConsumer(BigQuery bigquery,
                                                     Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs,
                                                     ConfiguredAirbyteCatalog catalog,
                                                     Consumer<AirbyteMessage> outputRecordCollector,
                                                     boolean isGcsUploadingMode,
                                                     boolean isKeepFilesInGcs) {
    return new BigQueryDenormalizedRecordConsumer(bigquery, writeConfigs, catalog, outputRecordCollector, getNamingResolver());
  }

  @Override
  protected Schema getBigQuerySchema(JsonNode jsonSchema) {
    final List<Field> fieldList = getSchemaFields(getNamingResolver(), jsonSchema);
    if (fieldList.stream().noneMatch(f -> f.getName().equals(JavaBaseConstants.COLUMN_NAME_AB_ID))) {
      fieldList.add(Field.of(JavaBaseConstants.COLUMN_NAME_AB_ID, StandardSQLTypeName.STRING));
    }
    if (fieldList.stream().noneMatch(f -> f.getName().equals(JavaBaseConstants.COLUMN_NAME_EMITTED_AT))) {
      fieldList.add(Field.of(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, StandardSQLTypeName.TIMESTAMP));
    }
    return com.google.cloud.bigquery.Schema.of(fieldList);
  }

  private static List<Field> getSchemaFields(BigQuerySQLNameTransformer namingResolver, JsonNode jsonSchema) {
    Preconditions.checkArgument(jsonSchema.isObject() && jsonSchema.has(PROPERTIES_FIELD));
    final ObjectNode properties = (ObjectNode) jsonSchema.get(PROPERTIES_FIELD);
    return Jsons.keys(properties).stream().map(key -> getField(namingResolver, key, properties.get(key)).build()).collect(Collectors.toList());
  }

  private static Builder getField(BigQuerySQLNameTransformer namingResolver, String key, JsonNode fieldDefinition) {
    final String fieldName = namingResolver.getIdentifier(key);
    final Builder builder = Field.newBuilder(fieldName, StandardSQLTypeName.STRING);
    final List<JsonSchemaType> fieldTypes = getTypes(fieldName, fieldDefinition.get(TYPE_FIELD));
    for (int i = 0; i < fieldTypes.size(); i++) {
      final JsonSchemaType fieldType = fieldTypes.get(i);
      if (fieldType == JsonSchemaType.NULL) {
        builder.setMode(Mode.NULLABLE);
      }
      if (i == 0) {
        // Treat the first type in the list with the widest scope as the primary type
        final JsonSchemaType primaryType = fieldTypes.get(i);
        switch (primaryType) {
          case NULL -> {
            builder.setType(StandardSQLTypeName.STRING);
          }
          case STRING, NUMBER, INTEGER, BOOLEAN -> {
            builder.setType(primaryType.getBigQueryType());
          }
          case ARRAY -> {
            final JsonNode items;
            if (fieldDefinition.has("items")) {
              items = fieldDefinition.get("items");
            } else {
              LOGGER.warn("Source connector provided schema for ARRAY with missed \"items\", will assume that it's a String type");
              // this is handler for case when we get "array" without "items"
              // (https://github.com/airbytehq/airbyte/issues/5486)
              items = getTypeStringSchema();
            }
            final Builder subField = getField(namingResolver, fieldName, items).setMode(Mode.REPEATED);
            // "Array of Array of" (nested arrays) are not permitted by BigQuery ("Array of Record of Array of"
            // is)
            // Turn all "Array of" into "Array of Record of" instead
            return builder.setType(StandardSQLTypeName.STRUCT, subField.setName(NESTED_ARRAY_FIELD).build());
          }
          case OBJECT -> {
            final JsonNode properties;
            if (fieldDefinition.has(PROPERTIES_FIELD)) {
              properties = fieldDefinition.get(PROPERTIES_FIELD);
            } else {
              properties = fieldDefinition;
            }
            final FieldList fieldList = FieldList.of(Jsons.keys(properties)
                .stream()
                .map(f -> getField(namingResolver, f, properties.get(f)).build())
                .collect(Collectors.toList()));
            if (fieldList.size() > 0) {
              builder.setType(StandardSQLTypeName.STRUCT, fieldList);
            } else {
              builder.setType(StandardSQLTypeName.STRING);
            }
          }
          default -> {
            throw new IllegalStateException(
                String.format("Unexpected type for field %s: %s", fieldName, primaryType));
          }
        }
      }
    }
    return builder;
  }

  private static JsonNode getTypeStringSchema() {
    return Jsons.deserialize("{\n"
        + "    \"type\": [\n"
        + "      \"string\"\n"
        + "    ]\n"
        + "  }");
  }

  private static List<JsonSchemaType> getTypes(String fieldName, JsonNode type) {
    if (type == null) {
      LOGGER.warn("Field {} has no type defined, defaulting to STRING", fieldName);
      return List.of(JsonSchemaType.STRING);
    } else if (type.isArray()) {
      return MoreIterators.toList(type.elements()).stream()
          .map(s -> JsonSchemaType.fromJsonSchemaType(s.asText()))
          // re-order depending to make sure wider scope types are first
          .sorted(Comparator.comparingInt(JsonSchemaType::getOrder))
          .collect(Collectors.toList());
    } else if (type.isTextual()) {
      return Collections.singletonList(JsonSchemaType.fromJsonSchemaType(type.asText()));
    } else {
      throw new IllegalStateException("Unexpected type: " + type);
    }
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new BigQueryDenormalizedDestination();
    LOGGER.info("starting destination: {}", BigQueryDenormalizedDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", BigQueryDenormalizedDestination.class);
  }

}
