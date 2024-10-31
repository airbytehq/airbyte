/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.state;

import java.util.UUID;

public record MongoDbStreamState(String id, InitialSnapshotStatus status, IdType idType, Byte binarySubType) {

  public MongoDbStreamState(String id, InitialSnapshotStatus status, IdType idType) {
    this(id, status, idType, getBinarySubType(id, idType));
  }

  private static byte getBinarySubType(final String id, final IdType idType) {
    byte binarySubType = 0;
    if (idType == IdType.BINARY) {
      try {
        UUID.fromString(id);
        binarySubType = (byte) 4;
        // do something
      } catch (IllegalArgumentException exception) {
        // This is not a UUID, so assume it is a regular binary string from old state format
      }
    }
    return binarySubType;
  }

}
