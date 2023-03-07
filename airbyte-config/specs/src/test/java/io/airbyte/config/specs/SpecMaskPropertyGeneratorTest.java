/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.specs;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import java.util.Set;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link SpecMaskPropertyGenerator} class.
 */
class SpecMaskPropertyGeneratorTest {

  private SpecMaskPropertyGenerator specMaskPropertyGenerator;

  @BeforeEach
  void setup() {
    specMaskPropertyGenerator = new SpecMaskPropertyGenerator();
  }

  @Test
  void testSecretProperties() {
    final JsonNode json = Jsons.deserialize(
        "{\"api_key\":{\"type\":\"string\",\"description\":\"The API Key for the Airtable account.\",\"title\":\"API Key\",\"airbyte_secret\":true,\"examples\":[\"key1234567890\"],\"base_id\":{\"type\":\"string\",\"description\":\"The Base ID to integrate the data from.\",\"title\":\"Base ID\",\"examples\":[\"app1234567890\"]},\"tables\":{\"type\":\"array\",\"items\":[{\"type\":\"string\"}],\"description\":\"The list of Tables to integrate.\",\"title\":\"Tables\",\"examples\":[\"table 1\",\"table 2\"]}}}");
    final Set<String> propertyNames = specMaskPropertyGenerator.getSecretFieldNames(json);
    assertEquals(Set.of("api_key"), propertyNames);
  }

  @Test
  void testSecretPropertiesFalse() {
    final JsonNode json = Jsons.deserialize(
        "{\"api_key\":{\"type\":\"string\",\"description\":\"The API Key for the Airtable account.\",\"title\":\"API Key\",\"airbyte_secret\":false,\"examples\":[\"key1234567890\"],\"base_id\":{\"type\":\"string\",\"description\":\"The Base ID to integrate the data from.\",\"title\":\"Base ID\",\"examples\":[\"app1234567890\"]},\"tables\":{\"type\":\"array\",\"items\":[{\"type\":\"string\"}],\"description\":\"The list of Tables to integrate.\",\"title\":\"Tables\",\"examples\":[\"table 1\",\"table 2\"]}}}");
    final Set<String> propertyNames = specMaskPropertyGenerator.getSecretFieldNames(json);
    assertEquals(0, propertyNames.size());
  }

  @Test
  void testNestedSecretProperties() {
    final JsonNode json = Jsons.deserialize(
        "{\"title\":\"Authentication Method\",\"type\":\"object\",\"description\":\"The type of authentication to be used\",\"oneOf\":[{\"title\":\"None\",\"additionalProperties\":false,\"description\":\"No authentication will be used\",\"required\":[\"method\"],\"properties\":{\"method\":{\"type\":\"string\",\"const\":\"none\"}}},{\"title\":\"Api Key/Secret\",\"additionalProperties\":false,\"description\":\"Use a api key and secret combination to authenticate\",\"required\":[\"method\",\"apiKeyId\",\"apiKeySecret\"],\"properties\":{\"method\":{\"type\":\"string\",\"const\":\"secret\"},\"apiKeyId\":{\"title\":\"API Key ID\",\"description\":\"The Key ID to used when accessing an enterprise Elasticsearch instance.\",\"type\":\"string\"},\"apiKeySecret\":{\"title\":\"API Key Secret\",\"description\":\"The secret associated with the API Key ID.\",\"type\":\"string\",\"airbyte_secret\":true}}},{\"title\":\"Username/Password\",\"additionalProperties\":false,\"description\":\"Basic auth header with a username and password\",\"required\":[\"method\",\"username\",\"password\"],\"properties\":{\"method\":{\"type\":\"string\",\"const\":\"basic\"},\"username\":{\"title\":\"Username\",\"description\":\"Basic auth username to access a secure Elasticsearch server\",\"type\":\"string\"},\"password\":{\"title\":\"Password\",\"description\":\"Basic auth password to access a secure Elasticsearch server\",\"type\":\"string\",\"airbyte_secret\":true}}}]}");
    final Set<String> propertyNames = specMaskPropertyGenerator.getSecretFieldNames(json);
    assertEquals(Set.of("apiKeySecret", "password"), propertyNames);
  }

  @Test
  void testNullProperties() {
    final Set<String> propertyNames = specMaskPropertyGenerator.getSecretFieldNames(null);
    assertEquals(0, propertyNames.size());
  }

  @Test
  void testNonObjectProperties() {
    final JsonNode json = Jsons.deserialize("{\"array\":[\"foo\",\"bar\"]}");
    final Set<String> propertyNames = specMaskPropertyGenerator.getSecretFieldNames(json.get("array"));
    assertEquals(0, propertyNames.size());
  }

}
