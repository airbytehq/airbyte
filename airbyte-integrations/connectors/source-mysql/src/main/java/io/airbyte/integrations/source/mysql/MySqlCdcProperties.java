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

package io.airbyte.integrations.source.mysql;

import java.util.Properties;

public class MySqlCdcProperties {

  static Properties getDebeziumProperties() {
    final Properties props = new Properties();

    // debezium engine configuration
    props.setProperty("connector.class", "io.debezium.connector.mysql.MySqlConnector");

    // https://debezium.io/documentation/reference/connectors/mysql.html#mysql-boolean-values
    // https://debezium.io/documentation/reference/1.4/development/converters.html
    /**
     * {@link io.debezium.connector.mysql.converters.TinyIntOneToBooleanConverter}
     * {@link io.airbyte.integrations.debezium.internals.MySQLDateTimeConverter}
     */
    props.setProperty("converters", "boolean, datetime");
    props.setProperty("boolean.type", "io.debezium.connector.mysql.converters.TinyIntOneToBooleanConverter");
    props.setProperty("datetime.type", "io.airbyte.integrations.debezium.internals.MySQLDateTimeConverter");

    // snapshot config
    // https://debezium.io/documentation/reference/1.4/connectors/mysql.html#mysql-property-snapshot-mode
    props.setProperty("snapshot.mode", "initial");
    // https://debezium.io/documentation/reference/1.4/connectors/mysql.html#mysql-property-snapshot-locking-mode
    // This is to make sure other database clients are allowed to write to a table while Airbyte is
    // taking a snapshot. There is a risk involved that
    // if any database client makes a schema change then the sync might break
    props.setProperty("snapshot.locking.mode", "none");
    // https://debezium.io/documentation/reference/1.4/connectors/mysql.html#mysql-property-include-schema-changes
    props.setProperty("include.schema.changes", "false");

    return props;
  }

}
