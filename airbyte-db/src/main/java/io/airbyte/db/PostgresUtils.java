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
import com.google.common.base.Preconditions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import java.nio.ByteBuffer;
import java.sql.SQLException;
import java.util.List;

public class PostgresUtils {

  public static String getLsn(JdbcDatabase database) throws SQLException {
    // pg version > 9.
    final List<JsonNode> jsonNodes = database
        .bufferedResultSetQuery(conn -> conn.createStatement().executeQuery("SELECT pg_current_wal_lsn()"), JdbcUtils::rowToJson);

    Preconditions.checkState(jsonNodes.size() == 1);
    return jsonNodes.get(0).get("pg_current_wal_lsn").asText();
  }

  // https://www.postgresql.org/docs/current/datatype-pg-lsn.html
  public static int compareLsns(String lsn1, String lsn2) {
    final long decoded1 = lsnToLong(lsn1);
    final long decoded2 = lsnToLong(lsn2);

    return Long.compare(decoded1, decoded2);
  }

  // https://github.com/davecramer/LogicalDecode
  public static long lsnToLong(String lsn) {
    int slashIndex = lsn.lastIndexOf('/');
    Preconditions.checkArgument(slashIndex >= 0);

    String logicalXLogStr = lsn.substring(0, slashIndex);
    // parses as a long but then cast to int. this allows us to retain the full 32 bits of the integer
    // as opposed to the reduced value of Integer.MAX_VALUE.
    int logicalXlog = (int) Long.parseLong(logicalXLogStr, 16);
    String segmentStr = lsn.substring(slashIndex + 1, lsn.length());
    int segment = (int) Long.parseLong(segmentStr, 16);

    ByteBuffer buf = ByteBuffer.allocate(8);
    buf.putInt(logicalXlog);
    buf.putInt(segment);
    buf.position(0);
    return buf.getLong();
  }

  public static String longToLsn(long long1) {
    int front = (int) (long1 >> 32);
    int back = (int) long1;
    return (Integer.toHexString(front) + "/" + Integer.toHexString(back)).toUpperCase();
  }

}
