/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import io.airbyte.cdk.integrations.debug.DebugUtil;

public class PostgresDebugger {

  @SuppressWarnings({"unchecked", "deprecation", "resource"})
  public static void main(final String[] args) throws Exception {
    final PostgresSource postgresSource = new PostgresSource();
    DebugUtil.debug(postgresSource);
  }

}
