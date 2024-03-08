/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mysql;

import io.airbyte.cdk.integrations.debug.DebugUtil;

public class MySqlDebugger {

  @SuppressWarnings({"unchecked", "deprecation", "resource"})
  public static void main(final String[] args) throws Exception {
    final MySqlSource mysqlSource = new MySqlSource();
    DebugUtil.debug(mysqlSource);
  }

}
