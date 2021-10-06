/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.source.mssql;

import java.util.Properties;

public class MssqlCdcProperties {

  static Properties getDebeziumProperties() {
    final Properties props = new Properties();
    props.setProperty("connector.class", "io.debezium.connector.sqlserver.SqlServerConnector");

    // snapshot config
    // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-property-snapshot-mode
    props.setProperty("snapshot.mode", "initial");
    // https://docs.microsoft.com/en-us/sql/t-sql/statements/set-transaction-isolation-level-transact-sql?view=sql-server-ver15
    // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-property-snapshot-isolation-mode
    // we set this to avoid preventing other (non-Airbyte) transactions from updating table rows while
    // we snapshot
    props.setProperty("snapshot.isolation.mode", "snapshot");

    // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-property-include-schema-changes
    props.setProperty("include.schema.changes", "false");
    // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-property-provide-transaction-metadata
    props.setProperty("provide.transaction.metadata", "false");

    return props;
  }

}
