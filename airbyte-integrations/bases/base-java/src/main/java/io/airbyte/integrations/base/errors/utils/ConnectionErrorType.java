/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.utils;

public enum ConnectionErrorType {

  INCORRECT_USERNAME_OR_PASSWORD("Incorrect username or password"),
  INCORRECT_CREDENTIALS("Incorrect credentials"),
  INCORRECT_BUCKET_NAME("Incorrect bucket name"),
  INCORRECT_HOST_OR_PORT("Incorrect host or port"),
  INCORRECT_HOST_OR_PORT_OR_DATABASE("Some of provided parameters are incorrect: host, port or database name"),
  INCORRECT_USERNAME_OR_HOST("Incorrect username or host"),
  INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE("Some of provided parameters are incorrect: username, password or database name"),
  INCORRECT_CLUSTER("Incorrect cluster"),
  INCORRECT_DB_NAME("Incorrect data base name"),
  INCORRECT_SCHEMA_NAME("Incorrect schema name"),
  INCORRECT_ACCESS_PERMISSION("Insufficient privilege");

  private final String value;

  ConnectionErrorType(String value) {
    this.value = value;
  }

  public String getValue() {
    return value;
  }

}
