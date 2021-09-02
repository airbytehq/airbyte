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

import java.io.IOException;
import java.sql.SQLException;

/**
 * Wraps a {@link Database} object and throwing IOExceptions instead of SQLExceptions.
 */
public class ExceptionWrappingDatabase implements AutoCloseable {

  private final Database database;

  public ExceptionWrappingDatabase(Database database) {
    this.database = database;
  }

  public <T> T query(ContextQueryFunction<T> transform) throws IOException {
    try {
      return database.query(transform);
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  public <T> T transaction(ContextQueryFunction<T> transform) throws IOException {
    try {
      return database.transaction(transform);
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  @Override
  public void close() throws Exception {
    database.close();
  }

}
