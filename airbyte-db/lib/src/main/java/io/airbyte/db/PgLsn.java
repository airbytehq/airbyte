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

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import java.nio.ByteBuffer;

/**
 * Doc on the structure of a Postgres LSN
 * https://www.postgresql.org/docs/current/datatype-pg-lsn.html
 */
public class PgLsn implements Comparable<PgLsn> {

  private final long lsn;

  public static PgLsn fromLong(final long lsn) {
    return new PgLsn(lsn);
  }

  public static PgLsn fromPgString(final String lsn) {
    return new PgLsn(lsnToLong(lsn));
  }

  private PgLsn(final long lsn) {
    this.lsn = lsn;
  }

  public long asLong() {
    return lsn;
  }

  public String asPgString() {
    return longToLsn(lsn);
  }

  @Override
  public int compareTo(final PgLsn o) {
    return Long.compare(lsn, o.asLong());
  }

  /**
   * The LSN returned by Postgres is a 64-bit integer represented as hex encoded 32-bit integers
   * separated by a /. reference: https://github.com/davecramer/LogicalDecode
   *
   * @param lsn string representation as returned by postgres
   * @return long representation of the lsn string.
   */
  @VisibleForTesting
  static long lsnToLong(String lsn) {
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

  @VisibleForTesting
  static String longToLsn(long long1) {
    int front = (int) (long1 >> 32);
    int back = (int) long1;
    return (Integer.toHexString(front) + "/" + Integer.toHexString(back)).toUpperCase();
  }

  @Override
  public String toString() {
    return "PgLsn{" +
        "lsn=" + lsn +
        '}';
  }

}
