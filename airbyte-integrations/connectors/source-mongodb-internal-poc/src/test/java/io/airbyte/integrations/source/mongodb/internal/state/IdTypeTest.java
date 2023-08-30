/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.state;

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
  void findByMongoDbType() {
    assertTrue(IdType.findByMongoDbType("objectId").isPresent(), "objectId not found");
    assertTrue(IdType.findByMongoDbType("objectid").isEmpty(), "should have found nothing as it is case-sensitive");
    assertTrue(IdType.findByMongoDbType(null).isEmpty(), "passing in a null is fine");
  }

  @Test
  void supported() {
    assertEquals("objectId, string, int, long", IdType.SUPPORTED);
  }

}
