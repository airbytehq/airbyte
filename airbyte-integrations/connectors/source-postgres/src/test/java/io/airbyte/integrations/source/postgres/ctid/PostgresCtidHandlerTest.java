package io.airbyte.integrations.source.postgres.ctid;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.List;
import org.apache.commons.lang3.tuple.Pair;
import org.junit.jupiter.api.Test;

public class PostgresCtidHandlerTest {

  @Test
  void testCtidQueryBounds() {
    var chunks = PostgresCtidHandler.ctidQueryPlan(new Ctid(0,0),380545032192L, 8192L, 50);
    var expected = List.of(
        Pair.of(Ctid.of(0,0), Ctid.of(6400000, 0)),
        Pair.of(Ctid.of(6400000,0), Ctid.of(12800000, 0)),
        Pair.of(Ctid.of(12800000,0), Ctid.of(19200000, 0)),
        Pair.of(Ctid.of(19200000,0), Ctid.of(25600000, 0)),
        Pair.of(Ctid.of(25600000,0), Ctid.of(32000000, 0)),
        Pair.of(Ctid.of(32000000,0), Ctid.of(38400000, 0)),
        Pair.of(Ctid.of(38400000,0), Ctid.of(44800000, 0)),
        Pair.of(Ctid.of(44800000,0), null));
    assertEquals(chunks, expected);

    chunks = PostgresCtidHandler.ctidQueryPlan(new Ctid("(23000000,123)"),380545032192L, 8192L, 45);
    expected = List.of(
        Pair.of(Ctid.of("(23000000,123)"), Ctid.of(28760000, 0)),
        Pair.of(Ctid.of(28760000,0), Ctid.of("(34520000,0)")),
        Pair.of(Ctid.of("(34520000,0)"), Ctid.of(40280000,0)),
        Pair.of(Ctid.of(40280000,0), Ctid.of("(46040000,0)")),
        Pair.of(Ctid.of(46040000,0), null));
    assertEquals(chunks, expected);

    chunks = PostgresCtidHandler.ctidQueryPlan(Ctid.of(0,0),380545L, 8192L, 45);
    expected = List.of(
        Pair.of(Ctid.of(0, 0), null));
    assertEquals(chunks, expected);

    chunks = PostgresCtidHandler.ctidQueryPlan(Ctid.of(9876,5432),380545L, 8192L, 45);
    expected = List.of(
        Pair.of(Ctid.of(9876, 5432), null));
    assertEquals(chunks, expected);

    chunks = PostgresCtidHandler.ctidQueryPlan(Ctid.of(0,0),4096L, 8192L, 45);
    expected = List.of(
        Pair.of(Ctid.of(0, 0), null));
    assertEquals(chunks, expected);
  }
}
