/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.state;

import static org.junit.jupiter.api.Assertions.*;

import org.bson.types.ObjectId;
import org.junit.jupiter.api.Test;

class IdTypeTest {

  @Test
  void convert() {
    assertEquals(101, IdType.INT.convert("101"));
    assertEquals(202L, IdType.LONG.convert("202"));
    assertEquals("example", IdType.STRING.convert("example"));
    assertEquals(new ObjectId("012301230123012301230123"), IdType.OBJECT_ID.convert("012301230123012301230123"));
  }

  @Test
  void findByBsonType() {
    assertTrue(IdType.findByBsonType("objectId").isPresent(), "objectId not found");
    assertTrue(IdType.findByBsonType("objectid").isPresent(), "should have found nothing as it is case-insensitive");
    assertTrue(IdType.findByBsonType(null).isEmpty(), "passing in a null is fine");
  }

  @Test
  void findByJavaType() {
    assertTrue(IdType.findByJavaType("objectId").isPresent(), "objectId not found");
    assertTrue(IdType.findByJavaType("objectid").isPresent(), "should have found nothing as it is case-insensitive");
    assertTrue(IdType.findByJavaType("Integer").isPresent(), "Integer not found");
    assertTrue(IdType.findByJavaType(null).isEmpty(), "passing in a null is fine");
  }

  @Test
  void supported() {
    assertEquals("objectId, string, int, long", IdType.SUPPORTED);
  }

}
