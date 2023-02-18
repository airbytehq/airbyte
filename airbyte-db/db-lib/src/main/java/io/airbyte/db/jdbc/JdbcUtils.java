/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import org.jooq.JSONFormat;

public class JdbcUtils {

  public static final String HOST_KEY = "host";
  public static final String PORT_KEY = "port";
  public static final String DATABASE_KEY = "database";
  public static final String SCHEMA_KEY = "schema";

  public static final String USERNAME_KEY = "username";
  public static final String PASSWORD_KEY = "password";
  public static final String SSL_KEY = "ssl";

  private static final JSONFormat defaultJSONFormat = new JSONFormat().recordFormat(JSONFormat.RecordFormat.OBJECT);

  public static JSONFormat getDefaultJSONFormat() {
    return defaultJSONFormat;
  }

}
