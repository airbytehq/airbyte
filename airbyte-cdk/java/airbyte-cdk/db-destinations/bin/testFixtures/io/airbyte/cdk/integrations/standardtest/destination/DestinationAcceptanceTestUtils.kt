/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.json.Jsons

object DestinationAcceptanceTestUtils {
    fun putStringIntoJson(stringValue: String?, fieldName: String?, node: ObjectNode) {
        if (
            stringValue != null &&
                (stringValue.startsWith("[") && stringValue.endsWith("]") ||
                    stringValue.startsWith("{") && stringValue.endsWith("}"))
        ) {
            node.set<JsonNode>(fieldName, Jsons.deserialize(stringValue))
        } else {
            node.put(fieldName, stringValue)
        }
    }
}
