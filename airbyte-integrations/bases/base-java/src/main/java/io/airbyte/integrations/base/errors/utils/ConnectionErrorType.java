/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.utils;

public enum ConnectionErrorType {

  INCORRECT_USERNAME_OR_PASSWORD("Incorrect username or password"),
  INCORRECT_HOST_OR_PORT("Incorrect host or port"),
  INCORRECT_PASSWORD("incorrect password"),
  INCORRECT_USERNAME_OR_HOST("Incorrect username or host"),
  INCORRECT_DB_NAME("Incorrect data base name"),
  INCORRECT_SCHEMA_NAME("Incorrect schema name");

  private final String value;

  ConnectionErrorType(String value) {
    this.value = value;
  }

  public String getValue() {
    return value;
  }

}
