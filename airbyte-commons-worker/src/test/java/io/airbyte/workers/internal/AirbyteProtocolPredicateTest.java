/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.json.Jsons;
import io.airbyte.workers.test_utils.AirbyteMessageUtils;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class AirbyteProtocolPredicateTest {

  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";
  private static final String GREEN = "green";

  private AirbyteProtocolPredicate predicate;

  @BeforeEach
  void setup() {
    predicate = new AirbyteProtocolPredicate();
  }

  @Test
  void testValid() {
    assertTrue(predicate.test(Jsons.jsonNode(AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, GREEN))));
  }

  @Test
  void testInValid() {
    assertFalse(predicate.test(Jsons.deserialize("{ \"fish\": \"tuna\"}")));
  }

  @Test
  void testConcatenatedValid() {
    final String concatenated =
        Jsons.serialize(AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, GREEN))
            + Jsons.serialize(AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "yellow"));

    assertTrue(predicate.test(Jsons.deserialize(concatenated)));
  }

  @Test
  void testMissingNewLineAndLineStartsWithValidRecord() {
    final String concatenated =
        Jsons.serialize(AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, GREEN))
            + "{ \"fish\": \"tuna\"}";

    assertTrue(predicate.test(Jsons.deserialize(concatenated)));
  }

  @Test
  void testMissingNewLineAndLineStartsWithInvalidRecord() {
    final String concatenated =
        "{ \"fish\": \"tuna\"}"
            + Jsons.serialize(AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, GREEN));

    assertFalse(predicate.test(Jsons.deserialize(concatenated)));
  }

}
