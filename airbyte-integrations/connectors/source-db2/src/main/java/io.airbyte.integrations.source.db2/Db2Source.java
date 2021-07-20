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

package io.airbyte.integrations.source.db2;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Db2Source extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(Db2Source.class);
  public static final String DRIVER_CLASS = "com.ibm.db2.jcc.DB2Driver";

  public Db2Source() {
    super(DRIVER_CLASS, new Db2JdbcStreamingQueryConfiguration());
  }

  public static void main(String[] args) throws Exception {
    final Source source = new Db2Source();
    LOGGER.info("starting source: {}", Db2Source.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", Db2Source.class);
  }

  @Override
  public JsonNode toDatabaseConfig(JsonNode config) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("jdbc_url", String.format("jdbc:db2://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("db").asText()))
        .put("username", config.get("username").asText())
        .put("password", config.get("password").asText())
        .build());
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of(
        "NULLID", "SYSCAT", "SQLJ", "SYSFUN", "SYSIBM", "SYSIBMADM", "SYSIBMINTERNAL", "SYSIBMTS",
        "SYSPROC", "SYSPUBLIC", "SYSSTAT", "SYSTOOLS");
  }

}
