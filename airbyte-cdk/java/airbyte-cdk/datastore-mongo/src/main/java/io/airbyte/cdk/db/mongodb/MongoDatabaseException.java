/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.db.mongodb;

public class MongoDatabaseException extends RuntimeException {

  public static final String MONGO_DATA_BASE_NOT_FOUND = "Data Base with given name - %s not found.";

  public MongoDatabaseException(final String databaseName) {
    super(String.format(MONGO_DATA_BASE_NOT_FOUND, databaseName));
  }

}
