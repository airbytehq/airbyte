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
import com.google.cloud.bigquery.FieldList;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.Schema;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDenormalizedRecordConsumer extends BigQueryRecordConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDenormalizedRecordConsumer.class);

  private final StandardNameTransformer namingResolver;
  private final Set<String> invalidKeys;

  public BigQueryDenormalizedRecordConsumer(BigQuery bigquery,
                                            Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs,
                                            ConfiguredAirbyteCatalog catalog,
                                            Consumer<AirbyteMessage> outputRecordCollector,
                                            StandardNameTransformer namingResolver) {
    super(bigquery, writeConfigs, catalog, outputRecordCollector);
    this.namingResolver = namingResolver;
    invalidKeys = new HashSet<>();
  }

  @Override
  protected JsonNode formatRecord(Schema schema, AirbyteRecordMessage recordMessage) {
    // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds then
    // use BQ helpers to string-format correctly.
    long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
    final String formattedEmittedAt = QueryParameterValue.timestamp(emittedAtMicroseconds).getValue();
    Preconditions.checkArgument(recordMessage.getData().isObject());
    final ObjectNode data = (ObjectNode) formatData(schema.getFields(), recordMessage.getData());
    data.put(JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString());
    data.put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, formattedEmittedAt);
    return data;
  }

  protected JsonNode formatData(FieldList fields, JsonNode root) {
    if (root.isObject()) {
      final List<String> fieldNames = fields.stream().map(Field::getName).collect(Collectors.toList());
      return Jsons.jsonNode(Jsons.keys(root).stream()
          .filter(key -> {
            final boolean validKey = fieldNames.contains(namingResolver.getIdentifier(key));
            if (!validKey && !invalidKeys.contains(key)) {
              LOGGER.warn("Ignoring field {} as it is not defined in catalog", key);
              invalidKeys.add(key);
            }
            return validKey;
          })
          .collect(Collectors.toMap(namingResolver::getIdentifier,
              key -> formatData(fields.get(namingResolver.getIdentifier(key)).getSubFields(), root.get(key)))));
    } else if (root.isArray()) {
      // Arrays can have only one field
      Field arrayField = fields.get(0);
      // If an array of records, we should use subfields
      FieldList subFields = (arrayField.getSubFields() == null || arrayField.getSubFields().isEmpty() ? fields : arrayField.getSubFields());
      final JsonNode items = Jsons.jsonNode(MoreIterators.toList(root.elements()).stream()
          .map(p -> formatData(subFields, p))
          .collect(Collectors.toList()));

      // "Array of Array of" (nested arrays) are not permitted by BigQuery ("Array of Record of Array of"
      // is)
      // Turn all "Array of" into "Array of Record of" instead
      return Jsons.jsonNode(ImmutableMap.of(BigQueryDenormalizedDestination.NESTED_ARRAY_FIELD, items));
    } else {
      return root;
    }
  }

}
