/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mongodb;

import io.airbyte.cdk.integrations.debug.DebugUtil;

public class MongoDbDebugger {

  @SuppressWarnings({"unchecked", "deprecation", "resource"})
  public static void main(final String[] args) throws Exception {
    final MongoDbSource mongoDbSource = new MongoDbSource();
    DebugUtil.debug(mongoDbSource);
  }

}
