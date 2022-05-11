/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import java.util.Properties;

public class MssqlCdcProperties {

  static Properties getDebeziumProperties() {
    final Properties props = new Properties();
    props.setProperty("connector.class", "io.debezium.connector.sqlserver.SqlServerConnector");

    // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-property-include-schema-changes
    props.setProperty("include.schema.changes", "false");
    // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-property-provide-transaction-metadata
    props.setProperty("provide.transaction.metadata", "false");

    props.setProperty("converters", "mssql_converter");
    props.setProperty("mssql_converter.type", "io.airbyte.integrations.debezium.internals.MSSQLConverter");

    return props;
  }

}
