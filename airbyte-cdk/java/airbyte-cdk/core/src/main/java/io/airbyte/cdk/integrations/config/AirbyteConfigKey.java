/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.config;

public class AirbyteConfigKey<T> {

  public static final AirbyteConfigKey<String> JDBC_URL_PARAMS = new AirbyteConfigKey<>("jdbc_url_params");
  public static final AirbyteConfigKey<String> CONNECTION_PROPERTIES = new AirbyteConfigKey<>("connection_properties");
  final String jsonName;

  private AirbyteConfigKey(String jsonName) {
    this.jsonName = jsonName;
  }

}
