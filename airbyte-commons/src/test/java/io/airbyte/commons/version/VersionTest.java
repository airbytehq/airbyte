/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.version;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.Test;

class VersionTest {

  @Test
  void testJsonSerializationDeserialization() {
    final String jsonString = """
                              {"version": "1.2.3"}
                              """;
    final Version expectedVersion = new Version("1.2.3");

    final Version deserializedVersion = Jsons.deserialize(jsonString, Version.class);
    assertEquals(expectedVersion, deserializedVersion);

    final Version deserializedVersionLoop = Jsons.deserialize(Jsons.serialize(deserializedVersion), Version.class);
    assertEquals(expectedVersion, deserializedVersionLoop);
  }

}
