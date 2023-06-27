package io.airbyte.integrations.source.postgres.ctid;

import java.util.Objects;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Class represents a postgres ctid record in the form of "(number,number)"
 * Used to simplify code dealing with ctid calculations.
 */
public class Ctid {

  final Long page;
  final Long tuple;

  public static Ctid of(final long page, final long tuple) {
    return new Ctid(page, tuple);
  }

  public static Ctid of(final String ctid) {
    return new Ctid(ctid);
  }

  Ctid(final long page, final long tuple) {
    this.page = page;
    this.tuple = tuple;
  }

  Ctid(final String ctid) {
    final Pattern p = Pattern.compile("\\d+");
    final Matcher m = p.matcher(ctid);
    if (!m.find()) {
      throw new IllegalArgumentException("Invalid ctid format");
    }
    final String ctidPageStr = m.group();
    this.page = Long.parseLong(ctidPageStr);

    if (!m.find()) {
      throw new IllegalArgumentException("Invalid ctid format");
    }
    final String ctidTupleStr = m.group();
    this.tuple = Long.parseLong(ctidTupleStr);

    Objects.requireNonNull(this.page);
    Objects.requireNonNull(this.tuple);
  }

  @Override
  public String toString() {
    return "(%d,%d)".formatted(page, tuple);
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final Ctid ctid = (Ctid) o;
    return Objects.equals(page, ctid.page) && Objects.equals(tuple, ctid.tuple);
  }

  @Override
  public int hashCode() {
    return Objects.hash(page, tuple);
  }
}
