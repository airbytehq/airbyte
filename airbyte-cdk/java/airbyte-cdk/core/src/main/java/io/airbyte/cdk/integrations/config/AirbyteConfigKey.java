/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.config;

public enum AirbyteConfigKey {

  JDBC_URL_PARAMS("jdbc_url_params"),
  CONNECTION_PROPERTIES("connection_properties"),
  SCHEMA("schema"),
  ;

  final String jsonName;

  private AirbyteConfigKey(String jsonName) {
    this.jsonName = jsonName;
  }

}
