/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.util;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;

public class BigQueryDenormalizedTestDataUtils {

  public static JsonNode getSchema() {
    return Jsons.deserialize(
        "{\n"
            + "  \"type\": [\n"
            + "    \"object\"\n"
            + "  ],\n"
            + "  \"properties\": {\n"
            + "    \"accepts_marketing_updated_at\": {\n"
            + "      \"type\": [\n"
            + "        \"null\",\n"
            + "        \"string\"\n"
            + "      ],\n"
            + "      \"format\": \"date-time\"\n"
            + "    },\n"
            + "    \"name\": {\n"
            + "      \"type\": [\n"
            + "        \"string\"\n"
            + "      ]\n"
            + "    },\n"
            + "    \"permissions\": {\n"
            + "      \"type\": [\n"
            + "        \"array\"\n"
            + "      ],\n"
            + "      \"items\": {\n"
            + "        \"type\": [\n"
            + "          \"object\"\n"
            + "        ],\n"
            + "        \"properties\": {\n"
            + "          \"domain\": {\n"
            + "            \"type\": [\n"
            + "              \"string\"\n"
            + "            ]\n"
            + "          },\n"
            + "          \"grants\": {\n"
            + "            \"type\": [\n"
            + "              \"array\"\n"
            + "            ],\n"
            + "            \"items\": {\n"
            + "              \"type\": [\n"
            + "                \"string\"\n"
            + "              ]\n"
            + "            }\n"
            + "          }\n"
            + "        }\n"
            + "      }\n"
            + "    }\n"
            + "  }\n"
            + "}");

  }

  public static JsonNode getSchemaWithFormats() {
    return Jsons.deserialize(
        "{\n"
            + "  \"type\": [\n"
            + "    \"object\"\n"
            + "  ],\n"
            + "  \"properties\": {\n"
            + "    \"name\": {\n"
            + "      \"type\": [\n"
            + "        \"string\"\n"
            + "      ]\n"
            + "    },\n"
            + "    \"date_of_birth\": {\n"
            + "      \"type\": [\n"
            + "        \"string\"\n"
            + "      ],\n"
            + "      \"format\": \"date\"\n"
            + "    },\n"
            + "    \"updated_at\": {\n"
            + "      \"type\": [\n"
            + "        \"string\"\n"
            + "      ],\n"
            + "      \"format\": \"date-time\"\n"
            + "    }\n"
            + "  }\n"
            + "}");
  }

  public static JsonNode getSchemaWithDateTime() {
    return Jsons.deserialize(
        "{\n"
            + "  \"type\": [\n"
            + "    \"object\"\n"
            + "  ],\n"
            + "  \"properties\": {\n"
            + "    "
            +
            "\"updated_at\": {\n"
            + "      \"type\": [\n"
            + "        \"string\"\n"
            + "      ],\n"
            + "      \"format\": \"date-time\"\n"
            + "    },\n"
            + "    \"items\": {\n"
            + "      \"type\": [\n"
            + "        \"object\"\n"
            + "      ],\n"
            + "      \"properties\": {\n"
            + "        \"nested_datetime\": {\n"
            + "          \"type\": [\n"
            + "            \"string\"\n"
            + "          ],\n"
            + "          \"format\": \"date-time\"\n"
            + "        }\n"
            +
            "      "
            + "}\n"
            + "    }\n"
            + "  }\n"
            + "}");
  }

  public static JsonNode getSchemaWithInvalidArrayType() {
    return Jsons.deserialize(
        "{\n"
            + "  \"type\": [\n"
            + "    \"object\"\n"
            + "  ],\n"
            + "  \"properties\": {\n"
            + "    \"name\": {\n"
            + "      \"type\": [\n"
            + "        \"string\"\n"
            + "      ]\n"
            + "    },\n"
            + "    \"permissions\": {\n"
            + "      \"type\": [\n"
            + "        \"array\"\n"
            + "      ],\n"
            + "      \"items\": {\n"
            + "        \"type\": [\n"
            + "          \"object\"\n"
            + "        ],\n"
            + "        \"properties\": {\n"
            + "          \"domain\": {\n"
            + "            \"type\": [\n"
            + "              \"string\"\n"
            + "            ]\n"
            + "          },\n"
            + "          \"grants\": {\n"
            + "            \"type\": [\n"
            + "              \"array\"\n" // missed "items" element
            + "            ]\n"
            + "          }\n"
            + "        }\n"
            + "      }\n"
            + "    }\n"
            + "  }\n"
            + "}");

  }

  public static JsonNode getData() {
    return Jsons.deserialize(
        "{\n"
            + "  \"name\": \"Andrii\",\n"
            + "  \"accepts_marketing_updated_at\": \"2021-10-11T06:36:53-07:00\",\n"
            + "  \"permissions\": [\n"
            + "    {\n"
            + "      \"domain\": \"abs\",\n"
            + "      \"grants\": [\n"
            + "        \"admin\"\n"
            + "      ]\n"
            + "    },\n"
            + "    {\n"
            + "      \"domain\": \"tools\",\n"
            + "      \"grants\": [\n"
            + "        \"read\", \"write\"\n"
            + "      ]\n"
            + "    }\n"
            + "  ]\n"
            + "}");
  }

  public static JsonNode getDataWithFormats() {
    return Jsons.deserialize(
        "{\n"
            + "  \"name\": \"Andrii\",\n"
            + "  \"date_of_birth\": \"1996-01-25\",\n"
            + "  \"updated_at\": \"2021-10-11T06:36:53\"\n"
            + "}");
  }

  public static JsonNode getDataWithJSONDateTimeFormats() {
    return Jsons.deserialize(
        "{\n"
            + "  \"updated_at\": \"2021-10-11T06:36:53+00:00\",\n"
            + "  \"items\": {\n"
            + "    \"nested_datetime\": \"2021-11-11T06:36:53+00:00\"\n"
            + "  }\n"
            + "}");
  }

  public static JsonNode getDataWithJSONWithReference() {
    return Jsons.jsonNode(
        ImmutableMap.of("users", ImmutableMap.of(
            "name", "John",
            "surname", "Adams")));
  }

  public static JsonNode getSchemaWithReferenceDefinition() {
    return Jsons.deserialize(
        "{ \n"
            + "  \"type\" : [ \"null\", \"object\" ],\n"
            + "  \"properties\" : {\n"
            + "    \"users\": {\n"
            + "      \"$ref\": \"#/definitions/users_\"\n"
            +
            "    }\n"
            + "  }\n"
            +
            "}\n"
            + "  ");
  }

  public static JsonNode getDataWithEmptyObjectAndArray() {
    return Jsons.deserialize(
        "{\n"
            + "  \"name\": \"Andrii\",\n"
            + "  \"permissions\": [\n"
            + "    {\n"
            + "      \"domain\": \"abs\",\n"
            + "      \"items\": {},\n" // empty object
            + "      \"grants\": [\n"
            + "        \"admin\"\n"
            + "      ]\n"
            + "    },\n"
            + "    {\n"
            + "      \"domain\": \"tools\",\n"
            + "      \"grants\": [],\n" // empty array
            + "      \"items\": {\n" // object with empty array and object
            + "        \"object\": {},\n"
            + "        \"array\": []\n"
            + "      }\n"
            + "    }\n"
            + "  ]\n"
            + "}");
  }

}
