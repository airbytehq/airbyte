/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.state;

import static io.airbyte.integrations.source.mongodb.state.IdType.BINARY;
import static org.bson.BsonBinarySubType.UUID_STANDARD;
import static org.junit.jupiter.api.Assertions.*;

import java.util.UUID;
import org.bson.BsonBinary;
import org.bson.types.Binary;
import org.bson.types.ObjectId;
import org.junit.jupiter.api.Test;

class IdTypeTest {

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
    assertTrue(IdType.findByJavaType("Binary").isPresent(), "Binary not found");
    assertTrue(IdType.findByJavaType(null).isEmpty(), "passing in a null is fine");
  }

  @Test
  void supported() {
    assertEquals("objectId, string, int, long, binData", IdType.SUPPORTED);
  }

  @Test
  void idToStringRepresenation() {
    assertEquals("1234", IdType.idToStringRepresenation(1234, IdType.INT));
    assertEquals("1234567890", IdType.idToStringRepresenation(1234567890L, IdType.LONG));
    assertEquals("abcde", IdType.idToStringRepresenation("abcde", IdType.STRING));
    assertEquals("012301230123012301230123", IdType.idToStringRepresenation(new ObjectId("012301230123012301230123"), IdType.OBJECT_ID));
    assertEquals("AQIDBA==", IdType.idToStringRepresenation(new Binary(new byte[] {1, 2, 3, 4}), BINARY));
    assertEquals("74c14d29-3d25-4e59-a621-73895ee859f9",
        IdType.idToStringRepresenation(new Binary(UUID_STANDARD,
            new BsonBinary(UUID.fromString("74C14D29-3D25-4E59-A621-73895EE859F9")).getData()), BINARY));
  }

}
