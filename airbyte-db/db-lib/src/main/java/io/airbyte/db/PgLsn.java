/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
  static long lsnToLong(final String lsn) {
    final int slashIndex = lsn.lastIndexOf('/');
    Preconditions.checkArgument(slashIndex >= 0);

    final String logicalXLogStr = lsn.substring(0, slashIndex);
    // parses as a long but then cast to int. this allows us to retain the full 32 bits of the integer
    // as opposed to the reduced value of Integer.MAX_VALUE.
    final int logicalXlog = (int) Long.parseLong(logicalXLogStr, 16);
    final String segmentStr = lsn.substring(slashIndex + 1, lsn.length());
    final int segment = (int) Long.parseLong(segmentStr, 16);

    final ByteBuffer buf = ByteBuffer.allocate(8);
    buf.putInt(logicalXlog);
    buf.putInt(segment);
    buf.position(0);
    return buf.getLong();
  }

  @VisibleForTesting
  static String longToLsn(final long long1) {
    final int front = (int) (long1 >> 32);
    final int back = (int) long1;
    return (Integer.toHexString(front) + "/" + Integer.toHexString(back)).toUpperCase();
  }

  @Override
  public String toString() {
    return "PgLsn{" +
        "lsn=" + lsn +
        '}';
  }

}
