/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yellowbrick;

import java.sql.Connection;
import java.sql.SQLException;

public class YellowbrickConnectionHandler {

  /**
   * For to close a connection. Aimed to be use in test only.
   *
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
