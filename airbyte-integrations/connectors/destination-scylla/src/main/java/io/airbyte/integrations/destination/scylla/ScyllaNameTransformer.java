/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.scylla;

import com.google.common.base.CharMatcher;
import io.airbyte.commons.text.Names;
import io.airbyte.integrations.destination.StandardNameTransformer;

class ScyllaNameTransformer extends StandardNameTransformer {

  private final ScyllaConfig scyllaConfig;

  public ScyllaNameTransformer(ScyllaConfig scyllaConfig) {
    this.scyllaConfig = scyllaConfig;
  }

  String outputKeyspace(String namespace) {
    if (namespace == null || namespace.isBlank()) {
      return scyllaConfig.getKeyspace();
    }
    return CharMatcher.is('_').trimLeadingFrom(Names.toAlphanumericAndUnderscore(namespace));
  }

  String outputTable(String streamName) {
    var tableName = super.getRawTableName(streamName.toLowerCase()).substring(1);
    // max allowed length for a scylla table is 48 characters
    return tableName.length() > 48 ? tableName.substring(0, 48) : tableName;
  }

  String outputTmpTable(String streamName) {
    var tableName = super.getTmpTableName(streamName.toLowerCase()).substring(1);
    // max allowed length for a scylla table is 48 characters
    return tableName.length() > 48 ? tableName.substring(0, 48) : tableName;
  }

  String outputColumn(String columnName) {
    return Names.doubleQuote(columnName.toLowerCase());
  }

}
