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
        Pair.of(Ctid.of(0,0), Ctid.of(6553600, 0)),
        Pair.of(Ctid.of(6553600,0), Ctid.of(13107200, 0)),
        Pair.of(Ctid.of(13107200,0), Ctid.of(19660800, 0)),
        Pair.of(Ctid.of(19660800,0), Ctid.of(26214400, 0)),
        Pair.of(Ctid.of(26214400,0), Ctid.of(32768000, 0)),
        Pair.of(Ctid.of(32768000,0), Ctid.of(39321600, 0)),
        Pair.of(Ctid.of(39321600,0), Ctid.of(45875200, 0)),
        Pair.of(Ctid.of(45875200,0), null));
    assertEquals(expected, chunks);

    chunks = PostgresCtidHandler.ctidQueryPlan(new Ctid("(23000000,123)"),380545032192L, 8192L, 45);
    expected = List.of(
        Pair.of(Ctid.of("(23000000,123)"), Ctid.of(28898240, 0)),
        Pair.of(Ctid.of(28898240,0), Ctid.of("(34796480,0)")),
        Pair.of(Ctid.of("(34796480,0)"), Ctid.of(40694720,0)),
        Pair.of(Ctid.of(40694720,0),null));
    assertEquals(expected, chunks);

    chunks = PostgresCtidHandler.ctidQueryPlan(Ctid.of(0,0),380545L, 8192L, 45);
    expected = List.of(
        Pair.of(Ctid.of(0, 0), null));
    assertEquals(expected, chunks);

    chunks = PostgresCtidHandler.ctidQueryPlan(Ctid.of(9876,5432),380545L, 8192L, 45);
    expected = List.of(
        Pair.of(Ctid.of(9876, 5432), null));
    assertEquals(expected, chunks);

    chunks = PostgresCtidHandler.ctidQueryPlan(Ctid.of(0,0),4096L, 8192L, 45);
    expected = List.of(
        Pair.of(Ctid.of(0, 0), null));
    assertEquals(expected, chunks);
  }
}
