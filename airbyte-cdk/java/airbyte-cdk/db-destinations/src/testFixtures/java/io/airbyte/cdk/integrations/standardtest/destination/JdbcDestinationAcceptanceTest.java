/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.standardtest.destination;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.Arrays;
import java.util.Optional;
import java.util.function.Function;
import org.jooq.Record;

public abstract class JdbcDestinationAcceptanceTest extends DestinationAcceptanceTest {

  protected final ObjectMapper mapper = new ObjectMapper();

  protected JsonNode getJsonFromRecord(final Record record) {
    return getJsonFromRecord(record, x -> Optional.empty());
  }

  protected JsonNode getJsonFromRecord(final Record record, final Function<Object, Optional<String>> valueParser) {
    final ObjectNode node = mapper.createObjectNode();

    Arrays.stream(record.fields()).forEach(field -> {
      final var value = record.get(field);

      final Optional<String> parsedValue = valueParser.apply(value);
      if (parsedValue.isPresent()) {
        node.put(field.getName(), parsedValue.get());
      } else {
        switch (field.getDataType().getTypeName()) {
          case "varchar", "nvarchar", "jsonb", "json", "other":
            final var stringValue = (value != null ? value.toString() : null);
            DestinationAcceptanceTestUtils.putStringIntoJson(stringValue, field.getName(), node);
            break;
          default:
            node.put(field.getName(), (value != null ? value.toString() : null));
        }
      }
    });
    return node;
  }

}
