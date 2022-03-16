/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

import com.zaxxer.hikari.HikariConfig;
import java.io.IOException;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A token loader to refresh access token every 7 minutes. Snowflake access token expires after 10
 * minutes. For the cases when sync duration is more than 10 mins, access token must be refreshed by
 * the new one.
 */
public class SnowflakeAccessTokenLoader extends Thread {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeAccessTokenLoader.class);
  private final HikariConfig hikariDataSource;

  public SnowflakeAccessTokenLoader(HikariConfig hikariDataSource) {
    this.hikariDataSource = hikariDataSource;
  }

  @Override
  public void run() {
    LOGGER.info("SnowflakeAccessTokenLoader started..");
    while (SnowflakeSource.isSourceAlive) {
      var properties = hikariDataSource.getDataSourceProperties();
      try {
        LOGGER.info("Request access token");
        var token = SnowflakeOAuthUtils.getAccessTokenUsingRefreshToken(
            properties.getProperty("host"), properties.getProperty("client_id"),
            properties.getProperty("client_secret"), properties.getProperty("refresh_token"));
        properties.setProperty("token", token);
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
      try {
        // To refresh token every 7 minutes
        TimeUnit.MINUTES.sleep(7);
      } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
      }
    }
    LOGGER.info("SnowflakeAccessTokenLoader finished.");
  }

}
