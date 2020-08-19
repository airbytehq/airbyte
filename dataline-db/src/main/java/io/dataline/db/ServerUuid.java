/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.db;

import static org.jooq.impl.DSL.field;

import java.sql.SQLException;
import java.util.Optional;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Record;
import org.jooq.Result;

/*
The server UUID identifies a specific database installation of Dataline for analytics purposes.
 */
public class ServerUuid {
  public static Optional<String> get(BasicDataSource connectionPool) throws SQLException {
    return DatabaseHelper.query(
        connectionPool,
        ctx -> {
          Result<Record> result =
              ctx.select().from("dataline_metadata").where(field("key").eq("server-uuid")).fetch();
          Optional<Record> first = result.stream().findFirst();

          if (first.isEmpty()) {
            return Optional.empty();
          } else {
            return Optional.of((String) first.get().get("value"));
          }
        });
  }
}
