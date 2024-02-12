/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.state;

public record MongoDbStreamState(String id, InitialSnapshotStatus status, IdType idType) {

  /**
   * Takes a value converting it to the appropriate MongoDb type based on the IdType of this record.
   *
   * @param value the value to convert
   * @return a converted value.
   */
  public Object idTypeAsMongoDbType(final String value) {
    return idType.convert(value);
  }

}
