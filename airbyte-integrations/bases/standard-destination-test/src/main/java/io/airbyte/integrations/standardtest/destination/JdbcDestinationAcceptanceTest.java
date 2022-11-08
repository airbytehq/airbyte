/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.Arrays;
import org.jooq.Record;

public abstract class JdbcDestinationAcceptanceTest extends DestinationAcceptanceTest {

  protected final ObjectMapper mapper = new ObjectMapper();

  protected JsonNode getJsonFromRecord(Record record) {
    ObjectNode node = mapper.createObjectNode();

    Arrays.stream(record.fields()).forEach(field -> {
      var value = record.get(field);

      switch (field.getDataType().getTypeName()) {
        case "varchar", "nvarchar", "jsonb", "json", "other":
          var stringValue = (value != null ? value.toString() : null);
          DestinationAcceptanceTestUtils.putStringIntoJson(stringValue, field.getName(), node);
          break;
        default:
          node.put(field.getName(), (value != null ? value.toString() : null));
      }
    });
    return node;
  }

}
