/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.state;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public record MongoDbStreamState(String id, InitialSnapshotStatus status, IdType idType) {
  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbStreamState.class);
//  /**
//   * Takes a value converting it to the appropriate MongoDb type based on the IdType of this record.
//   *
//   * @param value the value to convert
//   * @return a converted value.
//   */
//  public Object idTypeAsMongoDbType(final String value) {
//    LOGGER.info("***{} converted to {}", value , idType.convert(value));
//    return idType.convert(value);
//  }

}
