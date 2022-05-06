/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import java.util.Arrays;
import org.jooq.Record;

public abstract class JdbcDestinationAcceptanceTest extends DestinationAcceptanceTest {

  protected final ObjectMapper mapper = new ObjectMapper();

  protected JsonNode getJsonFromRecord(Record record) {
    ObjectNode node = mapper.createObjectNode();

    Arrays.stream(record.fields()).forEach(field -> {
      var value = record.get(field);

      switch (field.getDataType().getTypeName()) {
        case "varchar", "nvarchar", "jsonb", "other":
          var stringValue = (value != null ? value.toString() : null);
          if (stringValue != null && (stringValue.replaceAll("[^\\x00-\\x7F]", "").matches("^\\[.*\\]$")
              || stringValue.replaceAll("[^\\x00-\\x7F]", "").matches("^\\{.*\\}$"))) {
            node.set(field.getName(), Jsons.deserialize(stringValue));
          } else {
            node.put(field.getName(), stringValue);
          }
          break;
        default:
          node.put(field.getName(), (value != null ? value.toString() : null));
      }
    });
    return node;
  }

}
