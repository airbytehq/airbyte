/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;

public class DestinationAcceptanceTestUtils {

  public static void putStringIntoJson(String stringValue, String fieldName, ObjectNode node) {
    if (stringValue != null && (stringValue.startsWith("[") && stringValue.endsWith("]")
        || stringValue.startsWith("{") && stringValue.endsWith("}"))) {
      node.set(fieldName, Jsons.deserialize(stringValue));
    } else {
      node.put(fieldName, stringValue);
    }
  }

}
