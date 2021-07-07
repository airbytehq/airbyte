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

package io.airbyte.integrations.source.scaffold_java_jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.NoOpJdbcStreamingQueryConfiguration;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ScaffoldJavaJdbcSource extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(ScaffoldJavaJdbcSource.class);

  // TODO insert your driver name. Ex: "com.microsoft.sqlserver.jdbc.SQLServerDriver"
  static final String DRIVER_CLASS = "driver_name_here";

  public ScaffoldJavaJdbcSource() {
    // By default NoOpJdbcStreamingQueryConfiguration class is used, but may be updated. See see example
    // MssqlJdbcStreamingQueryConfiguration
    super(DRIVER_CLASS, new NoOpJdbcStreamingQueryConfiguration());
  }

  // TODO The config is based on spec.json, update according to your DB
  @Override
  public JsonNode toDatabaseConfig(JsonNode aqqConfig) {
    // TODO create DB config. Ex: "Jsons.jsonNode(ImmutableMap.builder().put("username",
    // userName).put("password", pas)...build());
    return null;
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    // TODO Add tables to exaclude, Ex "INFORMATION_SCHEMA", "sys", "spt_fallback_db", etc
    return Set.of("");
  }

  public static void main(String[] args) throws Exception {
    final Source source = new ScaffoldJavaJdbcSource();
    LOGGER.info("starting source: {}", ScaffoldJavaJdbcSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", ScaffoldJavaJdbcSource.class);
  }

}
