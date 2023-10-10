/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import java.sql.Connection;
import java.sql.SQLException;

public class RedshiftConnectionHandler {

  /**
   * For to close a connection. Aimed to be use in test only.
   *
   * @param connection The connection to close
   */
  public static void close(Connection connection) {
    try {
      connection.setAutoCommit(false);
      connection.commit();
      connection.close();
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }
  }

}
