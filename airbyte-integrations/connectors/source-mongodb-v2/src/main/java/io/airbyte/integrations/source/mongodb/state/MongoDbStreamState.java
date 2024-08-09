/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.state;

public record MongoDbStreamState(String id, InitialSnapshotStatus status, IdType idType, Byte binarySubType) {

  public MongoDbStreamState(String id, InitialSnapshotStatus status, IdType idType) {
    this(id, status, idType, (byte) 0);
    assert idType != IdType.BINARY;
  }

}
