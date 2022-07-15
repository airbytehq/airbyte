/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static org.junit.Assert.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class AirbyteProtocolPredicateTest {

  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";

  private AirbyteProtocolPredicate predicate;

  @BeforeEach
  void setup() {
    predicate = new AirbyteProtocolPredicate();
  }

  @Test
  void testValid() {
    assertTrue(predicate.test(Jsons.jsonNode(AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "green"))));
  }

  @Test
  void testInValid() {
    assertFalse(predicate.test(Jsons.deserialize("{ \"fish\": \"tuna\"}")));
  }

  @Test
  void testConcatenatedValid() {
    final String concatenated =
        Jsons.serialize(AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "green"))
            + Jsons.serialize(AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "yellow"));

    assertTrue(predicate.test(Jsons.deserialize(concatenated)));
  }

  @Test
  void testMissingNewLineAndLineStartsWithValidRecord() {
    final String concatenated =
        Jsons.serialize(AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "green"))
            + "{ \"fish\": \"tuna\"}";

    assertTrue(predicate.test(Jsons.deserialize(concatenated)));
  }

  @Test
  void testMissingNewLineAndLineStartsWithInvalidRecord() {
    final String concatenated =
        "{ \"fish\": \"tuna\"}"
            + Jsons.serialize(AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "green"));

    assertFalse(predicate.test(Jsons.deserialize(concatenated)));
  }

}
