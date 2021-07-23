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

package io.airbyte.db;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.stream.Stream;

public abstract class SqlDatabase implements AutoCloseable {

  private JsonNode sourceConfig;
  private JsonNode databaseConfig;

  public abstract void execute(String sql) throws Exception;

  public abstract Stream<JsonNode> query(String sql, String... params) throws Exception;

  public JsonNode getSourceConfig() {
    return sourceConfig;
  }

  public void setSourceConfig(JsonNode sourceConfig) {
    this.sourceConfig = sourceConfig;
  }

  public JsonNode getDatabaseConfig() {
    return databaseConfig;
  }

  public void setDatabaseConfig(JsonNode databaseConfig) {
    this.databaseConfig = databaseConfig;
  }

}
