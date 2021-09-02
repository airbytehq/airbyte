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

package io.airbyte.integrations.source.oracle;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.OracleJdbcStreamingQueryConfiguration;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.CommonField;
import java.sql.JDBCType;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OracleSource extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleSource.class);

  static final String DRIVER_CLASS = "oracle.jdbc.OracleDriver";

  private List<String> schemas;

  public OracleSource() {
    super(DRIVER_CLASS, new OracleJdbcStreamingQueryConfiguration());
  }

  @Override
  public JsonNode toDatabaseConfig(JsonNode config) {
    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("jdbc_url", String.format("jdbc:oracle:thin:@//%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("sid").asText()));

    if (config.has("password")) {
      configBuilder.put("password", config.get("password").asText());
    }

    // Use the upper-cased username by default.
    schemas = List.of(config.get("username").asText().toUpperCase(Locale.ROOT));
    if (config.has("schemas") && config.get("schemas").isArray()) {
      schemas = new ArrayList<>();
      for (final JsonNode schema : config.get("schemas")) {
        schemas.add(schema.asText());
      }
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public List<TableInfo<CommonField<JDBCType>>> discoverInternal(JdbcDatabase database) throws Exception {
    List<TableInfo<CommonField<JDBCType>>> internals = new ArrayList<>();
    for (String schema : schemas) {
      LOGGER.debug("Discovering schema: {}", schema);
      internals.addAll(super.discoverInternal(database, schema));
    }

    for (TableInfo<CommonField<JDBCType>> info : internals) {
      LOGGER.debug("Found table: {}", info.getName());
    }

    return internals;
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    // need to add SYSTEM too but for that need create another user when creating the container.
    return Set.of("APEX_040000", "CTXSYS", "SYSTEM", "FLOWS_FILES", "HR", "MDSYS", "OUTLN", "SYS", "XDB");
  }

  public static void main(String[] args) throws Exception {
    final Source source = new OracleSource();
    LOGGER.info("starting source: {}", OracleSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", OracleSource.class);
  }

}
