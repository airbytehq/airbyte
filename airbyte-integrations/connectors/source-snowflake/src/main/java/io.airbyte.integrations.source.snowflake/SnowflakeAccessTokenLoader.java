/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

import com.zaxxer.hikari.HikariDataSource;
import java.io.IOException;
import java.util.concurrent.TimeUnit;

/**
 * A token loader to refresh access token every 7 minutes. Snowflake access token expires after 10
 * minutes. For the cases when sync duration is more than 10 mins, access token must be refreshed by
 * the new one.
 */
public class SnowflakeAccessTokenLoader extends Thread {

  private final HikariDataSource hikariDataSource;

  public SnowflakeAccessTokenLoader(HikariDataSource hikariDataSource) {
    this.hikariDataSource = hikariDataSource;
  }

  @Override
  public void run() {
    while (SnowflakeSource.isSourceAlive) {
      var properties = hikariDataSource.getDataSourceProperties();
      try {
        var token = SnowflakeOAuthUtils.getAccessTokenUsingRefreshToken(
            properties.getProperty("host"), properties.getProperty("client_id"),
            properties.getProperty("client_secret"), properties.getProperty("refresh_token"));
        properties.setProperty("token", token);
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
      try {
        TimeUnit.MINUTES.sleep(7);
      } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
      }
    }
  }

}
