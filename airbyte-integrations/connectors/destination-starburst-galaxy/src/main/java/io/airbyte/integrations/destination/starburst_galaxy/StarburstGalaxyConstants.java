/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static io.airbyte.db.factory.DatabaseDriver.STARBURST;

public final class StarburstGalaxyConstants {

  public static final String STARBURST_GALAXY_DRIVER_CLASS = STARBURST.getDriverClassName();
  public static final String ACCEPT_TERMS = "accept_terms";
  public static final String SERVER_HOSTNAME = "server_hostname";
  public static final String PORT = "port";
  public static final String USERNAME = "username";
  public static final String PASSWORD = "password";
  public static final String CATALOG = "catalog";
  public static final String CATALOG_SCHEMA = "catalog_schema";
  public static final String OBJECT_STORE_TYPE = "object_store_type";
  public static final String PURGE_STAGING_TABLE = "purge_staging_table";
  public static final String STAGING_OBJECT_STORE = "staging_object_store";

  private StarburstGalaxyConstants() {}

}
